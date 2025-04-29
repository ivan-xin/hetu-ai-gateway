from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class FinetuneProviderModel(BaseModel):
    """Finetune provider model: a model a provider supports for fine-tuning"""

    name: str
    id: str

class FinetuneProvider(BaseModel):
    """Finetune provider: list of models a provider supports for fine-tuning"""

    name: str
    id: str
    enabled: bool
    models: list[FinetuneProviderModel]

class FineTunePlatform(str, Enum):
    FIREWORKS_AI = "fireworks_ai"
    TOGETHER_AI = "together_ai"

class FineTuneStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class FineTuneJob(BaseModel):
    id: str
    name: str
    provider: FineTunePlatform
    model_name: str
    dataset_path: str
    parameters: Dict[str, Any]
    status: FineTuneStatus = FineTuneStatus.PENDING
    provider_job_id: Optional[str] = None
    created_at: str
    updated_at: str
    error_message: Optional[str] = None
    status_message: Optional[str] = None  
    metrics: Dict[str, Any] = Field(default_factory=dict)
    fine_tuned_model: Optional[str] = None  # Make this optional
    description: Optional[str] = None  

class FineTuneRequest(BaseModel):
    model_name: str
    provider: str
    dataset_path: str
    hyperparameters: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

class FineTuneJobCreate(BaseModel):
    name: str
    provider: FineTunePlatform
    model_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
