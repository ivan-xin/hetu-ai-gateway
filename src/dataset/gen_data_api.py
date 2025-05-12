from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from typing import List, Optional, Dict, Any

from kiln_ai.datamodel import DataSource, DataSourceType, PromptId, TaskRun

from .gen_data_service import DataGenService
from .gen_data_model import (
    DataGenCategoriesApiInput,
    DataGenSampleApiInput,
    DataGenSaveSamplesApiInput,
    DataGenBatchSaveSamplesApiInput,
    FileImportRequest,
    ImportResponse
)

router = APIRouter(prefix="/api/dataset", tags=["dataset"])

# 依赖注入
def get_data_gen_service():
    return DataGenService()


# API路由
@router.post("/projects/{project_id}/tasks/{task_id}/generate_categories")
async def generate_categories(
    project_id: str, 
    task_id: str, 
    input: DataGenCategoriesApiInput,
    service: DataGenService = Depends(get_data_gen_service)
) -> TaskRun:
    """生成分类"""
    try:
        # 添加请求体验证
        if not input.node_path:
            raise ValueError("node_path 不能为空")
        if not input.num_subtopics or input.num_subtopics <= 0:
            raise ValueError("num_subtopics 必须大于0")
        if not input.model_name:
            raise ValueError("model_name 不能为空")
        if not input.provider:
            raise ValueError("provider 不能为空")
        # 检查是否有 drop_unsupported_params 参数
        drop_params = getattr(input, "drop_unsupported_params", False)
        
        # 如果是 Together AI 并且需要丢弃不支持的参数，我们可以设置环境变量
        if drop_params and input.provider.lower() == "together_ai":
            import os
            import litellm
            
            # 临时设置 litellm.drop_params
            original_drop_params = litellm.drop_params
            litellm.drop_params = True
            
            try:
                return await service.generate_categories(
                    project_id=project_id,
                    task_id=task_id,
                    node_path=input.node_path,
                    num_subtopics=input.num_subtopics,
                    model_name=input.model_name,
                    provider=input.provider,
                    human_guidance=input.human_guidance,
                    existing_topics=input.existing_topics,
                )
            finally:
                # 恢复原始设置
                litellm.drop_params = original_drop_params
        else:
            # 正常处理
            return await service.generate_categories(
                project_id=project_id,
                task_id=task_id,
                node_path=input.node_path,
                num_subtopics=input.num_subtopics,
                model_name=input.model_name,
                provider=input.provider,
                human_guidance=input.human_guidance,
                existing_topics=input.existing_topics,
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"生成分类失败: {str(e)}")


@router.post("/projects/{project_id}/tasks/{task_id}/generate_samples")
async def generate_samples(
    project_id: str, 
    task_id: str, 
    input: DataGenSampleApiInput,
    service: DataGenService = Depends(get_data_gen_service)
) -> TaskRun:
    """生成样本"""
    try:
        return await service.generate_samples(
            project_id=project_id,
            task_id=task_id,
            topic=input.topic,
            num_samples=input.num_samples,
            model_name=input.model_name,
            provider=input.provider,
            human_guidance=input.human_guidance,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/projects/{project_id}/tasks/{task_id}/save_sample")
async def save_sample(
    project_id: str,
    task_id: str,
    sample: DataGenSaveSamplesApiInput,
    session_id: Optional[str] = None,
    service: DataGenService = Depends(get_data_gen_service)
) -> TaskRun:
    """保存样本"""
    try:
        return await service.save_sample(
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
            session_id=session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/projects/{project_id}/tasks/{task_id}/save_samples_batch")
async def save_samples_batch(
    project_id: str,
    task_id: str,
    batch: DataGenBatchSaveSamplesApiInput,
    service: DataGenService = Depends(get_data_gen_service)
) -> List[TaskRun]:
    """批量保存样本"""
    try:
        return await service.save_samples_batch(
            project_id=project_id,
            task_id=task_id,
            batch=batch,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/projects/{project_id}/tasks/{task_id}/import_samples_async")
async def import_samples_async(
    project_id: str,
    task_id: str,
    batch: DataGenBatchSaveSamplesApiInput,
    background_tasks: BackgroundTasks,
    service: DataGenService = Depends(get_data_gen_service)
) -> ImportResponse:
    """异步导入样本（在后台处理）"""
    try:
        # 启动后台任务处理样本
        background_tasks.add_task(
            service.process_samples_in_background,
            project_id,
            task_id,
            batch
        )
        
        return ImportResponse(
            status="import_started", 
            sample_count=len(batch.samples),
            message="样本导入已在后台开始处理"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/projects/{project_id}/tasks/{task_id}/import_samples_from_file")
async def import_samples_from_file(
    project_id: str,
    task_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    request: FileImportRequest = Depends(),
    service: DataGenService = Depends(get_data_gen_service)
) -> ImportResponse:
    """从文件导入样本"""
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # 如果请求对象为空，创建默认值
        if request is None:
            request = FileImportRequest(
                prompt_method="default_prompt"  # 需要一个有效的默认值
            )
        
        # 确保file不为None
        if file is None:
            raise HTTPException(
                status_code=400,
                detail="未提供文件"
            )
        
        # 根据文件类型处理
        if file.filename and file.filename.endswith('.csv'):
            batch = await service.import_from_csv(
                project_id=project_id,
                task_id=task_id,
                csv_content=content_str,
                input_model_name=request.input_model_name,
                input_provider=request.input_provider,
                output_model_name=request.output_model_name,
                output_provider=request.output_provider,
                prompt_method=request.prompt_method,
                session_id=request.session_id,
            )
        elif file.filename and file.filename.endswith('.jsonl'):
            batch = await service.import_from_jsonl(
                project_id=project_id,
                task_id=task_id,
                jsonl_content=content_str,
                input_model_name=request.input_model_name,
                input_provider=request.input_provider,
                output_model_name=request.output_model_name,
                output_provider=request.output_provider,
                prompt_method=request.prompt_method,
                session_id=request.session_id,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="不支持的文件格式。请上传CSV或JSONL文件。"
            )
        
        # 对于大文件，使用异步处理
        if len(batch.samples) > 100 and background_tasks is not None:
            background_tasks.add_task(
                service.process_samples_in_background,
                project_id,
                task_id,
                batch
            )
            
            return ImportResponse(
                status="import_started", 
                sample_count=len(batch.samples),
                message="文件导入已在后台开始处理"
            )
        else:
            # 对于小文件，直接处理
            await service.save_samples_batch(
                project_id=project_id,
                task_id=task_id,
                batch=batch,
            )
            
            return ImportResponse(
                status="import_completed", 
                sample_count=len(batch.samples),
                message="文件导入已完成"
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
