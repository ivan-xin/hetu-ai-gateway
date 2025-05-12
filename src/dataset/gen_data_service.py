# import litellm
# litellm.drop_params = True
import logging
import json
import csv
import io
import asyncio
from typing import List, Optional, Dict, Any

from kiln_ai.adapters.adapter_registry import adapter_for_task
from kiln_ai.adapters.data_gen.data_gen_task import (
    DataGenCategoriesTask,
    DataGenCategoriesTaskInput,
    DataGenSampleTask,
    DataGenSampleTaskInput,
    wrap_task_with_guidance,
)
from kiln_ai.adapters.model_adapters.base_adapter import AdapterConfig
from kiln_ai.datamodel import DataSource, DataSourceType, PromptId, TaskRun
from kiln_server.run_api import model_provider_from_string
from kiln_server.task_api import task_from_id

from .gen_data_model import DataGenSaveSamplesApiInput, DataGenBatchSaveSamplesApiInput

logger = logging.getLogger(__name__)

class DataGenService:
    """数据生成服务，提供生成分类和样本的功能"""
    
    async def generate_categories(
        self,
        project_id: str,
        task_id: str,
        node_path: List[str],
        num_subtopics: int,
        model_name: str,
        provider: str,
        human_guidance: Optional[str] = None,
        existing_topics: Optional[List[str]] = None,
    ) -> TaskRun:
        """生成分类"""
        task = task_from_id(project_id, task_id)
        categories_task = DataGenCategoriesTask()

        task_input = DataGenCategoriesTaskInput.from_task(
            task=task,
            node_path=node_path,
            num_subtopics=num_subtopics,
            human_guidance=human_guidance,
            existing_topics=existing_topics,
        )


        adapter = adapter_for_task(
            categories_task,
            model_name=model_name,
            provider=model_provider_from_string(provider),
        )
        
        categories_run = await adapter.invoke(task_input.model_dump())
        return categories_run
    
    async def generate_samples(
        self,
        project_id: str,
        task_id: str,
        topic: List[str],
        num_samples: int,
        model_name: str,
        provider: str,
        human_guidance: Optional[str] = None,
    ) -> TaskRun:
        """生成样本"""
        task = task_from_id(project_id, task_id)
        sample_task = DataGenSampleTask(target_task=task, num_samples=num_samples)

        task_input = DataGenSampleTaskInput.from_task(
            task=task,
            topic=topic,
            num_samples=num_samples,
            human_guidance=human_guidance,
        )

        adapter = adapter_for_task(
            sample_task,
            model_name=model_name,
            provider=model_provider_from_string(provider),
        )

        samples_run = await adapter.invoke(task_input.model_dump())
        return samples_run
    
    async def save_sample(
        self,
        project_id: str,
        task_id: str,
        input_data: str | dict,
        topic_path: List[str],
        input_model_name: str,
        input_provider: str,
        output_model_name: str,
        output_provider: str,
        prompt_method: PromptId,
        human_guidance: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> TaskRun:
        """保存样本"""
        task = task_from_id(project_id, task_id)

        # 如果提供了人工指导，则用它包装任务指令
        if human_guidance is not None and human_guidance.strip() != "":
            task.instruction = wrap_task_with_guidance(
                task.instruction, human_guidance
            )

        tags = ["synthetic"]
        if session_id:
            tags.append(f"synthetic_session_{session_id}")

        adapter = adapter_for_task(
            task,
            model_name=output_model_name,
            provider=model_provider_from_string(output_provider),
            prompt_id=prompt_method,
            base_adapter_config=AdapterConfig(default_tags=tags),
        )

        properties: Dict[str, str | int | float] = {
            "model_name": input_model_name,
            "model_provider": input_provider,
            "adapter_name": "kiln_data_gen",
        }
        
        topic_path_str = self.topic_path_to_string(topic_path)
        if topic_path_str:
            properties["topic_path"] = topic_path_str

        run = await adapter.invoke(
            input=input_data,
            input_source=DataSource(
                type=DataSourceType.synthetic,
                properties=properties,
            ),
        )

        run.save_to_file()
        return run
    
    async def save_samples_batch(
        self,
        project_id: str,
        task_id: str,
        batch: DataGenBatchSaveSamplesApiInput,
    ) -> List[TaskRun]:
        """批量保存样本"""
        results = []
        
        for sample in batch.samples:
            try:
                run = await self.save_sample(
                    project_id=project_id,
                    task_id=task_id,
                    input_data=sample.input,
                    topic_path=sample.topic_path,
                    input_model_name=sample.input_model_name,
                    input_provider=sample.input_provider,
                    output_model_name=sample.output_model_name,
                    output_provider=sample.output_provider,
                    prompt_method=sample.prompt_method,
                    human_guidance=sample.human_guidance,
                    session_id=batch.session_id,
                )
                results.append(run)
            except Exception as e:
                logger.error(f"Error saving sample: {e}")
                # 继续处理其他样本
        
        return results
    
    async def process_samples_in_background(
        self,
        project_id: str,
        task_id: str,
        batch: DataGenBatchSaveSamplesApiInput,
    ) -> None:
        """在后台处理样本，分批处理大量数据"""
        # 分批处理，每批100个样本
        chunk_size = 100
        for i in range(0, len(batch.samples), chunk_size):
            chunk = batch.samples[i:i+chunk_size]
            chunk_batch = DataGenBatchSaveSamplesApiInput(
                samples=chunk,
                session_id=batch.session_id
            )
            
            # 处理这一批
            await self.save_samples_batch(project_id, task_id, chunk_batch)
            
            # 小延迟，防止系统过载
            await asyncio.sleep(0.1)
    
    async def import_from_csv(
        self,
        project_id: str,
        task_id: str,
        csv_content: str,
        input_model_name: str,
        input_provider: str,
        output_model_name: str,
        output_provider: str,
        prompt_method: PromptId,
        session_id: Optional[str] = None,
    ) -> DataGenBatchSaveSamplesApiInput:
        """从CSV内容导入样本"""
        reader = csv.DictReader(io.StringIO(csv_content))
        samples = []
        
        for row in reader:
            if 'input' not in row or 'output' not in row:
                raise ValueError("CSV必须包含'input'和'output'列")
            
            # 为每行创建一个样本
            sample = DataGenSaveSamplesApiInput(
                input=row['input'],
                topic_path=row.get('topic_path', '').split('>>>>>') if row.get('topic_path') else [],
                input_model_name=input_model_name,
                input_provider=input_provider,
                output_model_name=output_model_name,
                output_provider=output_provider,
                prompt_method=prompt_method,
                human_guidance=row.get('human_guidance')
            )
            samples.append(sample)
        
        return DataGenBatchSaveSamplesApiInput(samples=samples, session_id=session_id)
    
    async def import_from_jsonl(
        self,
        project_id: str,
        task_id: str,
        jsonl_content: str,
        input_model_name: str,
        input_provider: str,
        output_model_name: str,
        output_provider: str,
        prompt_method: PromptId,
        session_id: Optional[str] = None,
    ) -> DataGenBatchSaveSamplesApiInput:
        """从JSONL内容导入样本"""
        samples = []
        
        for line in jsonl_content.strip().split('\n'):
            if not line.strip():
                continue
                
            try:
                data = json.loads(line)
                if 'input' not in data:
                    raise ValueError("每行JSONL必须包含'input'字段")
                
                # 为每行创建一个样本
                sample = DataGenSaveSamplesApiInput(
                    input=data['input'],
                    topic_path=data.get('topic_path', []),
                    input_model_name=input_model_name,
                    input_provider=input_provider,
                    output_model_name=output_model_name,
                    output_provider=output_provider,
                    prompt_method=prompt_method,
                    human_guidance=data.get('human_guidance')
                )
                samples.append(sample)
            except json.JSONDecodeError as e:
                raise ValueError(f"无效的JSON行: {line}. 错误: {str(e)}")
        
        return DataGenBatchSaveSamplesApiInput(samples=samples, session_id=session_id)
    
    def topic_path_to_string(self, topic_path: List[str]) -> Optional[str]:
        """将主题路径列表转换为字符串"""
        if topic_path and len(topic_path) > 0:
            return ">>>>>".join(topic_path)
        return None
    
    def topic_path_from_string(self, topic_path: Optional[str]) -> List[str]:
        """将主题路径字符串转换为列表"""
        if topic_path:
            return topic_path.split(">>>>>")
        return []
