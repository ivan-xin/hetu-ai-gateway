
from enum import Enum
from kiln_ai.adapters.fine_tune.base_finetune import FineTuneParameter, FineTuneStatus
from pydantic import BaseModel
from kiln_ai.datamodel import (
    DatasetSplit,
    Finetune,
    FinetuneDataStrategy,
    FineTuneStatusType,
    Task,
)

from kiln_ai.datamodel.dataset_filters import (
    DatasetFilterId,
)

from kiln_ai.datamodel.dataset_split import (
    AllSplitDefinition,
    Train60Test20Val20SplitDefinition,
    Train80Test10Val10SplitDefinition,
    Train80Test20SplitDefinition,
)

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


class DatasetSplitType(Enum):
    """Dataset split types used in the API. Any split type can be created in code."""

    TRAIN_TEST = "train_test"
    TRAIN_TEST_VAL = "train_test_val"
    TRAIN_TEST_VAL_80 = "train_test_val_80"
    ALL = "all"


api_split_types = {
    DatasetSplitType.TRAIN_TEST: Train80Test20SplitDefinition,
    DatasetSplitType.TRAIN_TEST_VAL: Train60Test20Val20SplitDefinition,
    DatasetSplitType.TRAIN_TEST_VAL_80: Train80Test10Val10SplitDefinition,
    DatasetSplitType.ALL: AllSplitDefinition,
}


class CreateDatasetSplitRequest(BaseModel):
    """Request to create a dataset split"""

    dataset_split_type: DatasetSplitType
    filter_id: DatasetFilterId
    name: str | None = None
    description: str | None = None


class CreateFinetuneRequest(BaseModel):
    """Request to create a finetune"""

    name: str | None = None
    description: str | None = None
    dataset_id: str
    train_split_name: str
    validation_split_name: str | None = None
    parameters: dict[str, str | int | float | bool]
    provider: str
    base_model_id: str
    system_message_generator: str | None = None
    custom_system_message: str | None = None
    custom_thinking_instructions: str | None = None
    data_strategy: FinetuneDataStrategy


class FinetuneWithStatus(BaseModel):
    """Finetune with status"""

    finetune: Finetune
    status: FineTuneStatus


class UpdateFinetuneRequest(BaseModel):
    """Request to update a finetune"""

    name: str
    description: str | None = None