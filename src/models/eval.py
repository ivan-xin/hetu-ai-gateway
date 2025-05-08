from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel
from datetime import datetime

from kiln_ai.datamodel import (
    BasePrompt,
    DataSource,
    DataSourceType,
    PromptId,
    Task,
    TaskRun,
)
from kiln_ai.datamodel.basemodel import ID_TYPE
from kiln_ai.datamodel.dataset_filters import DatasetFilterId
from kiln_ai.datamodel.eval import (
    Eval,
    EvalConfig,
    EvalConfigType,
    EvalOutputScore,
    EvalRun,
    EvalTemplateId,
)
from kiln_ai.datamodel.json_schema import string_to_json_key
from kiln_ai.datamodel.task import RunConfigProperties, TaskRunConfig
from kiln_ai.adapters.ml_model_list import ModelProviderName

from ..utils.correlation_calculator import (
    CorrelationCalculator,
    CorrelationResult,
    CorrelationScore,
)

class ScoreSummary(BaseModel):
    """评分摘要"""
    mean_score: float

class EvalRunResult(BaseModel):
    """评估运行结果"""
    results: List[EvalRun]
    eval: Eval
    eval_config: EvalConfig
    run_config: TaskRunConfig

class EvalResultSummary(BaseModel):
    """评估结果摘要"""
    # run_config_id -> output_score_id -> ScoreSummary
    results: Dict[ID_TYPE, Dict[str, ScoreSummary]]
    # run_config_id -> percent of the dataset that has been processed
    run_config_percent_complete: Dict[ID_TYPE, float]
    # The total size of the dataset used for the eval
    dataset_size: int

class EvalConfigCompareSummary(BaseModel):
    """评估配置比较摘要"""
    # Summary of results. eval_config_id -> output_score_id -> CorrelationResult
    results: Dict[ID_TYPE, Dict[str, CorrelationResult]]
    # eval_config_id -> percent of the dataset that has been processed (run with eval scores)
    eval_config_percent_complete: Dict[ID_TYPE, float]
    # The total size of the dataset used for the eval config comparisons
    dataset_size: int
    # The number of dataset items which are fully rated, partially rated, or not rated at all.
    fully_rated_count: int
    partially_rated_count: int
    not_rated_count: int

# Request models
class CreateEvaluatorRequest(BaseModel):
    """创建评估器请求"""
    name: str
    description: str
    template: Optional[EvalTemplateId] = None
    output_scores: List[EvalOutputScore]
    eval_set_filter_id: DatasetFilterId
    eval_configs_filter_id: DatasetFilterId

class CreateEvalConfigRequest(BaseModel):
    """创建评估配置请求"""
    name: Optional[str] = None
    type: EvalConfigType
    properties: Dict[str, Any]
    model_name: str
    provider: ModelProviderName

class CreateTaskRunConfigRequest(BaseModel):
    """创建任务运行配置请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    model_name: str
    model_provider_name: ModelProviderName
    prompt_id: PromptId

class RunEvalConfigRequest(BaseModel):
    """运行评估配置请求"""
    run_config_ids: List[str]

class UpdateEvalRequest(BaseModel):
    """更新评估请求"""
    name: str
    description: Optional[str] = None
