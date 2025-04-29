import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Query
from fastapi.responses import FileResponse, StreamingResponse
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..services.finetune_service import FineTuneService
from ..models.finetune import FineTunePlatform, FineTuneStatus
from ..config import AppConfig
from . import schemas
from kiln_ai.datamodel import FinetuneDataStrategy
from kiln_ai.adapters.fine_tune.dataset_formatter import DatasetFormat

router = APIRouter(prefix="/api/finetune", tags=["finetune"])

# 依赖注入
def get_finetune_service():
    return FineTuneService()

@router.get("/providers", response_model=Dict[str, str])
async def list_providers():
    """列出所有支持的微调提供商"""
    return {
        FineTunePlatform.TOGETHER_AI: "Together AI",
        FineTunePlatform.FIREWORKS_AI: "Fireworks AI"
    }

@router.get("/parameters/{provider}", response_model=schemas.FineTuneParametersResponse)
async def get_parameters(provider: FineTunePlatform, 
                         service: FineTuneService = Depends(get_finetune_service)):
    """获取指定提供商的微调参数"""
    try:
        parameters = await service.get_available_parameters(provider)
        return {"parameters": parameters}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/models/{provider}", response_model=schemas.FineTuneModelsResponse)
async def get_provider_models(provider: FineTunePlatform,
                             service: FineTuneService = Depends(get_finetune_service)):
    """获取指定提供商支持的模型列表"""
    try:
        models = await service.get_provider_models()
        return {"models": models}
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

@router.post("/format-dataset")
async def format_dataset(
    dataset_path: str = Form(...),
    split_name: str = Form("train"),
    format_type: str = Form(DatasetFormat.OPENAI_CHAT_JSONL.value),
    data_strategy: str = Form(FinetuneDataStrategy.final_only.value),
    system_message: str = Form("You are a helpful assistant."),
    thinking_instructions: Optional[str] = Form(None),
    service: FineTuneService = Depends(get_finetune_service)
):
    """格式化数据集并返回下载链接"""
    try:
        # 验证数据集路径
        if not os.path.exists(dataset_path):
            raise HTTPException(status_code=400, detail="Dataset file not found")
        
        # 验证格式类型
        if format_type not in [format.value for format in DatasetFormat]:
            raise HTTPException(status_code=400, detail=f"Invalid format type: {format_type}")
        
        # 验证数据策略
        if data_strategy not in [strategy.value for strategy in FinetuneDataStrategy]:
            raise HTTPException(status_code=400, detail=f"Invalid data strategy: {data_strategy}")
        
        # 格式化数据集
        output_path = await service.format_and_download_dataset(
            dataset_path=dataset_path,
            split_name=split_name,
            format_type=DatasetFormat(format_type),
            data_strategy=FinetuneDataStrategy(data_strategy),
            system_message=system_message,
            thinking_instructions=thinking_instructions
        )
        
        # 返回文件下载链接
        return {"output_path": output_path}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/download-dataset")
async def download_dataset(
    dataset_path: str = Query(...),
    split_name: str = Query("train"),
    format_type: str = Query(DatasetFormat.OPENAI_CHAT_JSONL.value),
    data_strategy: str = Query(FinetuneDataStrategy.final_only.value),
    system_message: str = Query("You are a helpful assistant."),
    thinking_instructions: Optional[str] = Query(None),
    service: FineTuneService = Depends(get_finetune_service)
):
    """下载格式化后的数据集"""
    try:
        # 验证数据集路径
        if not os.path.exists(dataset_path):
            raise HTTPException(status_code=400, detail="Dataset file not found")
        
        # 验证格式类型
        if format_type not in [format.value for format in DatasetFormat]:
            raise HTTPException(status_code=400, detail=f"Invalid format type: {format_type}")
        
        # 验证数据策略
        if data_strategy not in [strategy.value for strategy in FinetuneDataStrategy]:
            raise HTTPException(status_code=400, detail=f"Invalid data strategy: {data_strategy}")
        
        # 格式化数据集
        output_path = await service.format_and_download_dataset(
            dataset_path=dataset_path,
            split_name=split_name,
            format_type=DatasetFormat(format_type),
            data_strategy=FinetuneDataStrategy(data_strategy),
            system_message=system_message,
            thinking_instructions=thinking_instructions
        )
        
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


@router.post("/jobs", response_model=schemas.FineTuneJobResponse)
async def create_job(
    request: schemas.FineTuneJobCreateRequest,
    service: FineTuneService = Depends(get_finetune_service)
):
    """创建新的微调作业"""
    try:
        # 验证数据集路径
        if not os.path.exists(request.dataset_path):
            raise HTTPException(status_code=400, detail="Dataset file not found")
        
        # 创建作业
        job = await service.create_job(
            name=request.name,
            provider=request.provider,
            model_name=request.model_name,
            dataset_path=request.dataset_path,
            parameters=request.parameters,
            description=request.description,
            system_message=request.system_message if request.system_message else "You are a helpful assistant.",
            thinking_instructions=request.thinking_instructions
        )
        
        return {"job": job}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/jobs", response_model=schemas.FineTuneJobsListResponse)
async def list_jobs(service: FineTuneService = Depends(get_finetune_service)):
    """列出所有微调作业"""
    jobs = service.list_jobs()
    return {"jobs": jobs}

@router.get("/jobs/{job_id}", response_model=schemas.FineTuneJobResponse)
async def get_job(job_id: str, service: FineTuneService = Depends(get_finetune_service)):
    """获取微调作业详情"""
    job = service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job": job}

@router.post("/jobs/{job_id}/cancel", response_model=schemas.FineTuneJobResponse)
async def cancel_job(job_id: str, service: FineTuneService = Depends(get_finetune_service)):
    """取消微调作业"""
    success = await service.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to cancel job")
    
    job = service.get_job(job_id)
    return {"job": job}
