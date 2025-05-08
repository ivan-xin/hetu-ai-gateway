import logging
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
