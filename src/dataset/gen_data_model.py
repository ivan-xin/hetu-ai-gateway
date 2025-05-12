from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
from kiln_ai.datamodel import PromptId

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

    # 允许使用 model_name 字段
    model_config = ConfigDict(protected_namespaces=())
    drop_unsupported_params: Optional[bool] = Field(
        description="Whether to drop unsupported parameters",
        default=False,
    )


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
    input: str | Dict = Field(description="Input for this sample")
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


class DataGenBatchSaveSamplesApiInput(BaseModel):
    samples: List[DataGenSaveSamplesApiInput] = Field(
        description="List of samples to save in batch"
    )
    session_id: Optional[str] = Field(
        description="Optional session ID to group samples",
        default=None,
    )


class FileImportRequest(BaseModel):
    input_model_name: str = Field(
        description="The name of the model used to generate the input",
        default="imported_data"
    )
    input_provider: str = Field(
        description="The provider of the model used to generate the input",
        default="external"
    )
    output_model_name: str = Field(
        description="The name of the model to use",
        default="imported_data"
    )
    output_provider: str = Field(
        description="The provider of the model to use",
        default="external"
    )
    prompt_method: PromptId = Field(
        description="The prompt method used to generate the output"
    )
    session_id: Optional[str] = Field(
        description="Optional session ID to group samples",
        default=None
    )


class ImportResponse(BaseModel):
    status: str
    sample_count: int
    message: Optional[str] = None
