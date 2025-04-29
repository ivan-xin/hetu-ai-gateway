import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Query
from fastapi.responses import FileResponse, StreamingResponse
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..services.finetune_service import FineTuneService
from ..models.finetune import (
    FineTunePlatform, FineTuneStatus, FineTuneJobCreate, 
    FineTuneJob, DatasetFormatRequest, FinetuneProvider,
    ProviderListResponse, ParameterListResponse, ModelListResponse,
    JobResponse, JobListResponse, DatasetFormatResponse
)

from ..config import AppConfig


router = APIRouter(prefix="/api/finetune", tags=["finetune"])

# 依赖注入
def get_finetune_service():
    return FineTuneService()

@router.get("/providers", response_model=ProviderListResponse)
async def list_providers():
    """列出所有支持的微调提供商"""
    return ProviderListResponse(
        providers={
            FineTunePlatform.TOGETHER_AI: "Together AI",
            FineTunePlatform.FIREWORKS_AI: "Fireworks AI"
        }
    )

@router.get("/parameters/{provider}", response_model=ParameterListResponse)
async def get_parameters(provider: FineTunePlatform, 
                         service: FineTuneService = Depends(get_finetune_service)):
    """获取指定提供商的微调参数"""
    try:
        parameters = await service.get_available_parameters(provider)
        return ParameterListResponse(parameters=parameters)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/models", response_model=ModelListResponse)
async def get_provider_models(service: FineTuneService = Depends(get_finetune_service)):
    """获取所有提供商支持的模型列表"""
    try:
        providers = await service.get_provider_models()
        return ModelListResponse(providers=providers)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    """上传数据集文件"""
    # 确保文件名安全
    if file.filename is None:
        # 如果文件名为None，生成一个默认文件名
        filename = f"dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    else:
        filename = file.filename.replace(" ", "_")
    
    file_path = os.path.join(AppConfig.UPLOAD_DIR, filename)
    
    # 保存上传的文件
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return {"filename": filename, "path": file_path}

@router.post("/format-dataset", response_model=DatasetFormatResponse)
async def format_dataset(format_request: DatasetFormatRequest,
                         service: FineTuneService = Depends(get_finetune_service)):
    """格式化数据集并返回下载链接"""
    try:
        output_path = await service.format_and_download_dataset(format_request)
        return DatasetFormatResponse(output_path=str(output_path))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/download-dataset")
async def download_dataset(
    dataset_path: str = Query(..., description="数据集路径"),
    split_name: str = Query("train", description="分割名称"),
    format_type: str = Query(..., description="格式类型"),
    data_strategy: str = Query(..., description="数据策略"),
    system_message: str = Query("You are a helpful assistant.", description="系统消息"),
    thinking_instructions: Optional[str] = Query(None, description="思考指令"),
    service: FineTuneService = Depends(get_finetune_service)
):
    """下载格式化后的数据集"""
    try:
        format_request = DatasetFormatRequest(
            dataset_path=dataset_path,
            split_name=split_name,
            format_type=format_type,
            data_strategy=data_strategy,
            system_message=system_message,
            thinking_instructions=thinking_instructions
        )
        
        output_path = await service.format_and_download_dataset(format_request)
        
        # 设置响应头以强制浏览器下载
        filename = output_path.name
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/jsonl",
        }
        
        # 返回文件流
        return StreamingResponse(open(output_path, "rb"), headers=headers)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/jobs", response_model=JobResponse)
async def create_job(job_create: FineTuneJobCreate,
                    service: FineTuneService = Depends(get_finetune_service)):
    """创建新的微调作业"""
    try:
        job = await service.create_job(job_create)
        return JobResponse(job=job)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    update_status: bool = Query(False, description="是否更新作业状态"),
    service: FineTuneService = Depends(get_finetune_service)
):
    """列出所有微调作业"""
    jobs = service.list_jobs(update_status=update_status)
    return JobListResponse(jobs=jobs)

@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, service: FineTuneService = Depends(get_finetune_service)):
    """获取微调作业详情"""
    job = service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(job=job)

@router.post("/jobs/{job_id}/cancel", response_model=JobResponse)
async def cancel_job(job_id: str, service: FineTuneService = Depends(get_finetune_service)):
    """取消微调作业"""
    success = await service.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to cancel job")
    
    job = service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(job=job)

# 添加更RESTful的路由结构，类似于finetune_api.py中的设计
# 这些路由可以与上面的路由共存，提供更灵活的API访问方式

@router.get("/projects/{project_id}/tasks/{task_id}/finetunes", response_model=JobListResponse)
async def list_project_finetunes(
    project_id: str, 
    task_id: str,
    update_status: bool = Query(False, description="是否更新作业状态"),
    service: FineTuneService = Depends(get_finetune_service)
):
    """列出项目任务下的所有微调作业"""
    # 在实际实现中，可以根据project_id和task_id过滤作业
    # 这里简化处理，返回所有作业
    jobs = service.list_jobs(update_status=update_status)
    return JobListResponse(jobs=jobs)

@router.get("/projects/{project_id}/tasks/{task_id}/finetunes/{finetune_id}", response_model=JobResponse)
async def get_project_finetune(
    project_id: str, 
    task_id: str, 
    finetune_id: str,
    service: FineTuneService = Depends(get_finetune_service)
):
    """获取项目任务下的特定微调作业"""
    job = service.get_job(finetune_id)
    if not job:
        raise HTTPException(status_code=404, detail="Finetune job not found")
    return JobResponse(job=job)

@router.post("/projects/{project_id}/tasks/{task_id}/finetunes", response_model=JobResponse)
async def create_project_finetune(
    project_id: str, 
    task_id: str,
    job_create: FineTuneJobCreate,
    service: FineTuneService = Depends(get_finetune_service)
):
    """在项目任务下创建新的微调作业"""
    try:
        # 可以在这里添加项目和任务的验证逻辑
        job = await service.create_job(job_create)
        return JobResponse(job=job)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/projects/{project_id}/tasks/{task_id}/finetunes/{finetune_id}/cancel", response_model=JobResponse)
async def cancel_project_finetune(
    project_id: str, 
    task_id: str, 
    finetune_id: str,
    service: FineTuneService = Depends(get_finetune_service)
):
    """取消项目任务下的特定微调作业"""
    success = await service.cancel_job(finetune_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to cancel job")
    
    job = service.get_job(finetune_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(job=job)

@router.get("/projects/{project_id}/tasks/{task_id}/dataset_splits")
async def list_dataset_splits(project_id: str, task_id: str):
    """列出项目任务下的所有数据集分割"""
    # 这个API需要实际的数据集分割管理逻辑
    # 简化实现，返回空列表
    return {"dataset_splits": []}

@router.post("/projects/{project_id}/tasks/{task_id}/dataset_splits")
async def create_dataset_split(project_id: str, task_id: str):
    """在项目任务下创建新的数据集分割"""
    # 这个API需要实际的数据集分割创建逻辑
    # 简化实现，返回一个示例响应
    return {"message": "Dataset split creation not implemented yet"}

@router.get("/download_dataset_jsonl")
async def download_dataset_jsonl(
    project_id: str = Query(..., description="项目ID"),
    task_id: str = Query(..., description="任务ID"),
    dataset_id: str = Query(..., description="数据集ID"),
    split_name: str = Query(..., description="分割名称"),
    format_type: str = Query(..., description="格式类型"),
    data_strategy: str = Query(..., description="数据策略"),
    system_message_generator: Optional[str] = Query(None, description="系统消息生成器"),
    custom_system_message: Optional[str] = Query(None, description="自定义系统消息"),
    custom_thinking_instructions: Optional[str] = Query(None, description="自定义思考指令"),
    service: FineTuneService = Depends(get_finetune_service)
):
    """下载数据集的JSONL格式文件"""
    try:
        # 构建请求对象
        format_request = DatasetFormatRequest(
            dataset_path=dataset_id,  # 这里简化处理，实际应该根据ID查找路径
            split_name=split_name,
            format_type=format_type,
            data_strategy=data_strategy,
            system_message=custom_system_message or "You are a helpful assistant.",
            thinking_instructions=custom_thinking_instructions
        )
        
        # 格式化并获取输出路径
        output_path = await service.format_and_download_dataset(format_request)
        
        # 设置响应头以强制浏览器下载
        headers = {
            "Content-Disposition": f'attachment; filename="{output_path.name}"',
            "Content-Type": "application/jsonl",
        }
        
        # 返回文件流
        return StreamingResponse(open(output_path, "rb"), headers=headers)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

