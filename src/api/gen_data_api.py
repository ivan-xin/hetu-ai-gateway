from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any

from kiln_ai.datamodel import PromptId, TaskRun

from ..services.gen_data_service import DataGenService

router = APIRouter(prefix="/api", tags=["data_generation"])

# 依赖注入
def get_data_gen_service():
    return DataGenService()

# 请求模型
class DataGenCategoriesApiInput(BaseModel):
    node_path: List[str] = Field(
        description="Path to the node in the category tree", default=[]
    )
    num_subtopics: int = Field(description="Number of subtopics to generate", default=6)
    human_guidance: Optional[str] = Field(
        description="Optional human guidance for generation",
        default=None,
    )
    existing_topics: Optional[List[str]] = Field(
        description="Optional list of existing topics to avoid",
        default=None,
    )
    model_name: str = Field(description="The name of the model to use")
    provider: str = Field(description="The provider of the model to use")

    # 允许使用 model_name 字段（通常 pydantic 会保留 model_*）
    model_config = ConfigDict(protected_namespaces=())


class DataGenSampleApiInput(BaseModel):
    topic: List[str] = Field(description="Topic path for sample generation", default=[])
    num_samples: int = Field(description="Number of samples to generate", default=8)
    human_guidance: Optional[str] = Field(
        description="Optional human guidance for generation",
        default=None,
    )
    model_name: str = Field(description="The name of the model to use")
    provider: str = Field(description="The provider of the model to use")

    # 允许使用 model_name 字段
    model_config = ConfigDict(protected_namespaces=())


class DataGenSaveSamplesApiInput(BaseModel):
    input: str | dict = Field(description="Input for this sample")
    topic_path: List[str] = Field(
        description="The path to the topic for this sample. Empty is the root topic."
    )
    input_model_name: str = Field(
        description="The name of the model used to generate the input"
    )
    input_provider: str = Field(
        description="The provider of the model used to generate the input"
    )
    output_model_name: str = Field(description="The name of the model to use")
    output_provider: str = Field(description="The provider of the model to use")
    prompt_method: PromptId = Field(
        description="The prompt method used to generate the output"
    )
    human_guidance: Optional[str] = Field(
        description="Optional human guidance for generation",
        default=None,
    )


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
        raise HTTPException(status_code=400, detail=str(e))


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
