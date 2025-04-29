import os
import json
import uuid
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Type
from pathlib import Path

from kiln_ai.adapters.fine_tune.finetune_registry import finetune_registry
from kiln_ai.adapters.fine_tune.base_finetune import BaseFinetuneAdapter, FineTuneParameter, FineTuneStatus
from kiln_ai.adapters.ml_model_list import (
    ModelProviderName,
    built_in_models,
)
from kiln_ai.adapters.prompt_builders import (
    chain_of_thought_prompt,
    prompt_builder_from_id,
)
from kiln_ai.adapters.provider_tools import (
    provider_enabled,
    provider_name_from_id,
)
from kiln_ai.datamodel import DatasetSplit, Finetune, FineTuneStatusType, FinetuneDataStrategy
from kiln_ai.adapters.fine_tune.dataset_formatter import DatasetFormat, DatasetFormatter

from ..models.finetune import FineTuneJob, FinetuneProviderModel,FinetuneProvider, FineTunePlatform, FineTuneStatus as JobStatus
from ..config import AppConfig

logger = logging.getLogger(__name__)

class FineTuneService:
    def __init__(self):
        self.jobs_dir = os.path.join(AppConfig.MODELS_DIR, "jobs")
        os.makedirs(self.jobs_dir, exist_ok=True)
        
        # 初始化适配器字典 - 存储活跃的微调适配器实例
        self.adapters: Dict[str, BaseFinetuneAdapter] = {}
        
        # 加载现有作业
        self.jobs: Dict[str, FineTuneJob] = {}
        self._load_jobs()
        
        # 后台任务
        self.background_task = None
        self._ensure_background_task()
    
    def _load_jobs(self):
        """加载现有作业"""
        for filename in os.listdir(self.jobs_dir):
            if filename.endswith('.json'):
                job_path = os.path.join(self.jobs_dir, filename)
                try:
                    with open(job_path, 'r') as f:
                        job_data = json.load(f)
                    job = FineTuneJob(**job_data)
                    self.jobs[job.id] = job
                    
                    # 如果作业状态是运行中，尝试恢复适配器
                    if job.status == JobStatus.RUNNING and job.provider_job_id:
                        self._try_restore_adapter(job)
                except Exception as e:
                    logger.error(f"Error loading job {filename}: {e}")
    
    def _save_job(self, job: FineTuneJob):
        """保存作业到文件"""
        job_path = os.path.join(self.jobs_dir, f"{job.id}.json")
        with open(job_path, 'w') as f:
            f.write(job.model_dump_json(indent=2))
    
    def _get_provider_name(self, provider: FineTunePlatform) -> ModelProviderName:
        """将 FineTunePlatform 转换为 ModelProviderName"""  
        provider_map = {
            FineTunePlatform.TOGETHER_AI: ModelProviderName.together_ai,
            FineTunePlatform.FIREWORKS_AI: ModelProviderName.fireworks_ai,
        }
        
        provider_name = provider_map.get(provider)
        if not provider_name:
            raise ValueError(f"Unsupported provider: {provider}")
        
        return provider_name
    
    def _get_adapter_class(self, provider: FineTunePlatform) -> Type[BaseFinetuneAdapter]:
        """获取适配器类"""
        provider_name = self._get_provider_name(provider)
        
        if provider_name not in finetune_registry:
            raise ValueError(f"Provider {provider} not found in finetune_registry")
        
        return finetune_registry[provider_name]
    
    def _try_restore_adapter(self, job: FineTuneJob) -> None:
        """尝试为现有作业恢复适配器实例"""
        try:
            # 创建一个 Finetune 数据模型
            finetune_model = Finetune(
                id=job.id,
                name=job.name,
                provider=self._get_provider_name(job.provider).value,
                base_model_id=job.model_name,
                provider_id=job.provider_job_id,
                fine_tune_model_id=job.fine_tuned_model,
                dataset_split_id=os.path.basename(job.dataset_path),
                train_split_name="train",  # 假设训练分割名称为 "train"
                parameters=job.parameters,
                system_message="You are a helpful assistant.",  # 默认系统消息
                data_strategy=FinetuneDataStrategy.final_only,
                description=job.description if hasattr(job, 'description') else None
            )
            
            # 获取适配器类并创建实例
            adapter_class = self._get_adapter_class(job.provider)
            self.adapters[job.id] = adapter_class(finetune_model)
            logger.info(f"Restored adapter for job {job.id}")
        except Exception as e:
            logger.error(f"Failed to restore adapter for job {job.id}: {e}")
    
    async def create_job(self, 
                         name: str, 
                         provider: FineTunePlatform, 
                         model_name: str, 
                         dataset_path: str, 
                         parameters: Dict[str, Any] | None = None,
                         description: str | None = None,
                         system_message: str = "You are a helpful assistant.",
                         thinking_instructions: str | None = None) -> FineTuneJob:
        """创建微调作业"""
        # 验证数据集路径
        if not os.path.exists(dataset_path):
            raise ValueError(f"Dataset not found: {dataset_path}")
        
        # 验证参数
        adapter_class = self._get_adapter_class(provider)
        if parameters:
            try:
                adapter_class.validate_parameters(parameters)
            except ValueError as e:
                raise ValueError(f"Invalid parameters: {str(e)}")
        
        # 创建作业
        job_id = str(uuid.uuid4())
        job = FineTuneJob(
            id=job_id,
            name=name,
            provider=provider,
            model_name=model_name,
            dataset_path=dataset_path,
            parameters=parameters or {},
            status=JobStatus.PENDING,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),

            description=description or "",
            fine_tuned_model=""
        )
        
        # 保存作业
        self.jobs[job_id] = job
        self._save_job(job)
        
        # 确保后台任务在运行
        self._ensure_background_task()
        

        return job    
    async def _start_job(self, job: FineTuneJob) -> None:
        """启动微调作业"""
        try:
            # 获取适配器类
            adapter_class = self._get_adapter_class(job.provider)
            
            # 更新作业状态
            job.status = JobStatus.RUNNING
            job.updated_at = datetime.now().isoformat()
            self._save_job(job)
            
            # 创建数据集分割对象
            dataset = DatasetSplit.load_from_file(Path(job.dataset_path))

            # 使用静态方法创建适配器和微调模型
            adapter, finetune_model = await adapter_class.create_and_start(
                dataset=dataset,
                provider_id=self._get_provider_name(job.provider).value,
                provider_base_model_id=job.model_name,
                train_split_name="train",  # 假设训练分割名称为 "train"
                system_message="You are a helpful assistant.",  # 提供一个默认的系统消息
                thinking_instructions=None,
                data_strategy=FinetuneDataStrategy.final_only,
                parameters=job.parameters,
                name=job.name,
                description=job.description,
                validation_split_name="validation" if "validation" in dataset.split_contents else None
            )
            
            # 保存适配器实例以便后续使用
            self.adapters[job.id] = adapter
            
            # 更新作业信息
            job.provider_job_id = finetune_model.provider_id
            job.fine_tuned_model = finetune_model.fine_tune_model_id or ""
            self._save_job(job)
            
            logger.info(f"Started fine-tuning job {job.id} with provider {job.provider}")
        
        except Exception as e:
            logger.error(f"Error starting fine-tuning job {job.id}: {e}")
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.updated_at = datetime.now().isoformat()
            self._save_job(job)
    
    def get_job(self, job_id: str) -> Optional[FineTuneJob]:
        """获取作业详情"""
        return self.jobs.get(job_id)
    
    def list_jobs(self) -> List[FineTuneJob]:
        """列出所有作业"""
        return list(self.jobs.values())
    
    def _ensure_background_task(self):
        """确保后台任务在运行"""
        if self.background_task is None or self.background_task.done():
            self.background_task = asyncio.create_task(self._process_jobs())
            logger.info("Started background job processing task")
    
    async def _process_jobs(self):
        """处理待处理的作业和检查运行中的作业"""
        while True:
            try:
                # 查找待处理的作业
                pending_jobs = [job for job in self.jobs.values() 
                               if job.status == JobStatus.PENDING]
                
                for job in pending_jobs:
                    await self._start_job(job)
                
                # 检查运行中的作业
                running_jobs = [job for job in self.jobs.values() 
                               if job.status == JobStatus.RUNNING]
                
                for job in running_jobs:
                    await self._check_job_status(job)
                
            except Exception as e:
                logger.error(f"Error in job processing: {e}")
            
            # 每分钟检查一次
            await asyncio.sleep(60)
    
    async def _check_job_status(self, job: FineTuneJob):
        """检查作业状态"""
        try:
            # 获取适配器实例
            adapter = self.adapters.get(job.id)
            if not adapter:
                # 如果没有找到适配器实例，尝试恢复
                self._try_restore_adapter(job)
                adapter = self.adapters.get(job.id)
                if not adapter:
                    logger.warning(f"Could not find or restore adapter for job {job.id}")
                    return
            
            # 获取作业状态
            status = await adapter.status()
            
            # 更新作业状态
            if status.status == FineTuneStatusType.completed:
                job.status = JobStatus.COMPLETED
                # 尝试部署模型（如果适配器支持）
                # if hasattr(adapter, '_deploy'):
                #     try:
                #         deployed = await adapter._deploy()
                #         if not deployed:
                #             logger.warning(f"Failed to deploy model for job {job.id}")
                #     except Exception as e:
                #         logger.error(f"Error deploying model for job {job.id}: {e}")
                
                # 获取微调后的模型 ID
                # _, model_id = await adapter.status()
                # if model_id:
                #     job.fine_tuned_model = model_id
    

            elif status.status == FineTuneStatusType.failed:
                job.status = JobStatus.FAILED
                job.error_message = status.message
            
            elif status.status == FineTuneStatusType.running:
                # 状态仍然是运行中，但可能有新消息
                if status.message:
                    job.status_message = status.message
            
            job.updated_at = datetime.now().isoformat()
            self._save_job(job)
            
        except Exception as e:
            logger.error(f"Error checking job status for {job.id}: {e}")
    
    async def cancel_job(self, job_id: str) -> bool:
        """取消微调作业"""
        job = self.get_job(job_id)
        if not job:
            return False
        
        if job.status != JobStatus.RUNNING:
            return False
        
        # 目前 Kiln 的适配器不支持取消，所以我们只能标记为失败
        job.status = JobStatus.FAILED
        job.error_message = "Job cancelled by user"
        job.updated_at = datetime.now().isoformat()
        self._save_job(job)
        
        # 清理适配器
        if job_id in self.adapters:
            del self.adapters[job_id]
        
        return True
    
    async def get_available_parameters(self, provider: FineTunePlatform) -> List[Dict[str, Any]]:
        """获取指定提供商支持的参数列表"""
        try:
            adapter_class = self._get_adapter_class(provider)
            parameters = adapter_class.available_parameters()
            
            # 转换为字典列表
            return [
                {
                    "name": param.name,
                    "type": param.type,
                    "description": param.description,
                    "optional": param.optional
                }
                for param in parameters
            ]
        except Exception as e:
            logger.error(f"Error getting available parameters for {provider}: {e}")
            return []
            
    async def get_provider_models(self) -> list[FinetuneProvider]:
        """获取指定提供商支持的模型列表"""
        provider_models: dict[ModelProviderName, list[FinetuneProviderModel]] = {}

        # Collect models by provider
        for model in built_in_models:
            for provider in model.providers:
                # Skip Fireworks models, as they are added separately
                if provider.name == ModelProviderName.fireworks_ai:
                    continue

                if provider.provider_finetune_id:
                    if provider.name not in provider_models:
                        provider_models[provider.name] = []
                    provider_models[provider.name].append(
                        FinetuneProviderModel(
                            name=model.friendly_name, id=provider.provider_finetune_id
                        )
                    )

        # Add models from Fireworks
        # try:
        #     fireworks_models = await fetch_fireworks_finetune_models()
        #     provider_models[ModelProviderName.fireworks_ai] = fireworks_models
        # except Exception as e:
        #     logger.error(f"Error fetching Fireworks models: {e}")

        # Create provider entries
        providers: list[FinetuneProvider] = []
        for provider_name, models in provider_models.items():
            providers.append(
                FinetuneProvider(
                    name=provider_name_from_id(provider_name),
                    id=provider_name,
                    enabled=await provider_enabled(provider_name),
                    models=models,
                )
            )

        return providers
            
    async def format_and_download_dataset(self, 
                                        dataset_path: str, 
                                        split_name: str = "train",
                                        format_type: DatasetFormat = DatasetFormat.OPENAI_CHAT_JSONL,
                                        data_strategy: FinetuneDataStrategy = FinetuneDataStrategy.final_only,
                                        system_message: str = "You are a helpful assistant.",
                                        thinking_instructions: str | None = None) -> Path:
        """格式化并下载数据集"""
        try:
            # 创建数据集分割对象
            dataset = DatasetSplit.load_from_file(Path(dataset_path))
            
            # 检查分割名称是否存在
            if split_name not in dataset.split_contents:
                raise ValueError(f"Split name '{split_name}' not found in dataset")
            
            # 使用 DatasetFormatter 格式化数据集
            formatter = DatasetFormatter(
                dataset=dataset,
                system_message=system_message,
                thinking_instructions=thinking_instructions,
            )
            
            # 导出为文件
            output_path = formatter.dump_to_file(
                split_name,
                format_type,
                data_strategy
            )
            
            return output_path
        except Exception as e:
            logger.error(f"Error formatting dataset: {e}")
            raise ValueError(f"Error formatting dataset: {e}")
