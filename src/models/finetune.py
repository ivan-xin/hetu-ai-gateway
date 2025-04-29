from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class FineTunePlatform(str, Enum):
    FIREWORKS_AI = "fireworks_ai"
    TOGETHER_AI = "together_ai"

class FineTuneStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class FineTuneParameter(BaseModel):
    name: str
    type: str
    description: str
    optional: bool = True

class FinetuneProviderModel(BaseModel):
    name: str
    id: str

class FinetuneProvider(BaseModel):
    name: str
    id: str
    enabled: bool
    models: List[FinetuneProviderModel]

class FineTuneJobBase(BaseModel):
    name: str
    provider: FineTunePlatform
    model_name: str
    dataset_path: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None
    system_message: str = "You are a helpful assistant."
    thinking_instructions: Optional[str] = None

class FineTuneJobCreate(FineTuneJobBase):
    pass

class FineTuneJob(FineTuneJobBase):
    id: str
    status: FineTuneStatus = FineTuneStatus.PENDING
    provider_job_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    status_message: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    fine_tuned_model: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FineTuneJobUpdate(BaseModel):
    status: Optional[FineTuneStatus] = None
    provider_job_id: Optional[str] = None
    error_message: Optional[str] = None
    status_message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    fine_tuned_model: Optional[str] = None

class DatasetFormatRequest(BaseModel):
    dataset_path: str
    split_name: str = "train"
    format_type: str
    data_strategy: str
    system_message: str = "You are a helpful assistant."
    thinking_instructions: Optional[str] = None

# 响应模型
class ProviderListResponse(BaseModel):
    providers: Dict[str, str]

class ParameterListResponse(BaseModel):
    parameters: List[Dict[str, Any]]

class ModelListResponse(BaseModel):
    providers: List[FinetuneProvider]

class JobResponse(BaseModel):
    job: FineTuneJob

class JobListResponse(BaseModel):
    jobs: List[FineTuneJob]

class DatasetFormatResponse(BaseModel):
    output_path: str
