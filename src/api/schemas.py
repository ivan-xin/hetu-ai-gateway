from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from ..models.finetune import FineTuneJob, FineTunePlatform

class FineTuneParameterSchema(BaseModel):
    name: str
    type: str
    description: str
    optional: bool = True

class FineTuneParametersResponse(BaseModel):
    parameters: List[FineTuneParameterSchema]

class FineTuneModelSchema(BaseModel):
    id: str
    name: str

class FineTuneModelsResponse(BaseModel):
    models: List[FineTuneModelSchema]

class FineTuneJobResponse(BaseModel):
    job: FineTuneJob

class FineTuneJobsListResponse(BaseModel):
    jobs: List[FineTuneJob]

class FineTuneJobCreateRequest(BaseModel):
    name: str
    provider: FineTunePlatform
    model_name: str
    dataset_path: str
    parameters: Dict[str, Any] = {}
    description: Optional[str] = None
    system_message: Optional[str] = None
    thinking_instructions: Optional[str] = None
