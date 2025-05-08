import logging
from fastapi import APIRouter, FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional

from src.finetune.v2.finetune_model import (
    FinetuneProviderModel,
    FinetuneProvider,
    FinetuneWithStatus,
    CreateDatasetSplitRequest,
    CreateFinetuneRequest,
    UpdateFinetuneRequest,
)
from kiln_ai.adapters.fine_tune.base_finetune import FineTuneParameter
from kiln_ai.datamodel import (
    DatasetSplit,
    Finetune,
)
from src.finetune.v2.finetune_service import FinetuneService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/api/projects/{project_id}/tasks/{task_id}/dataset_splits")
async def dataset_splits(project_id: str, task_id: str) -> list[DatasetSplit]:
    return await FinetuneService.get_dataset_splits(project_id, task_id)

@router.get("/api/projects/{project_id}/tasks/{task_id}/finetunes")
async def finetunes(
    project_id: str, task_id: str, update_status: bool = False
) -> list[Finetune]:
    return await FinetuneService.get_finetunes(project_id, task_id, update_status)

@router.get("/api/projects/{project_id}/tasks/{task_id}/finetunes/{finetune_id}")
async def finetune(
    project_id: str, task_id: str, finetune_id: str
) -> FinetuneWithStatus:
    return await FinetuneService.get_finetune(project_id, task_id, finetune_id)

@router.patch("/api/projects/{project_id}/tasks/{task_id}/finetunes/{finetune_id}")
async def update_finetune(
    project_id: str,
    task_id: str,
    finetune_id: str,
    request: UpdateFinetuneRequest,
) -> Finetune:
    return await FinetuneService.update_finetune(project_id, task_id, finetune_id, request)

@router.get("/api/finetune_providers")
async def finetune_providers() -> list[FinetuneProvider]:
    return await FinetuneService.get_finetune_providers()

@router.get("/api/finetune/hyperparameters/{provider_id}")
async def finetune_hyperparameters(
    provider_id: str,
) -> list[FineTuneParameter]:
    return await FinetuneService.get_finetune_hyperparameters(provider_id)

@router.post("/api/projects/{project_id}/tasks/{task_id}/dataset_splits")
async def create_dataset_split(
    project_id: str, task_id: str, request: CreateDatasetSplitRequest
) -> DatasetSplit:
    return await FinetuneService.create_dataset_split(project_id, task_id, request)

@router.post("/api/projects/{project_id}/tasks/{task_id}/finetunes")
async def create_finetune(
    project_id: str, task_id: str, request: CreateFinetuneRequest
) -> Finetune:
    return await FinetuneService.create_finetune(project_id, task_id, request)

@router.get("/api/download_dataset_jsonl")
async def download_dataset_jsonl(
    project_id: str,
    task_id: str,
    dataset_id: str,
    split_name: str,
    format_type: str,
    data_strategy: str,
    system_message_generator: Optional[str] = None,
    custom_system_message: Optional[str] = None,
    custom_thinking_instructions: Optional[str] = None,
) -> StreamingResponse:
    path = await FinetuneService.prepare_dataset_download(
        project_id,
        task_id,
        dataset_id,
        split_name,
        format_type,
        data_strategy,
        system_message_generator,
        custom_system_message,
        custom_thinking_instructions,
    )
    
    # set headers to force download in a browser
    headers = {
        "Content-Disposition": f'attachment; filename="{path.name}"',
        "Content-Type": "application/jsonl",
    }

    return StreamingResponse(open(path, "rb"), headers=headers)

def connect_fine_tune_api(app: FastAPI):
    """Register the fine-tune API routes with the FastAPI app"""
    app.include_router(router)
