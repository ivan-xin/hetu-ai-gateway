from typing import List, Optional
from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from kiln_ai.datamodel.task import RunConfigProperties, TaskRunConfig
from kiln_ai.datamodel.eval import Eval, EvalConfig

from .eval import (
    CreateEvaluatorRequest,
    CreateEvalConfigRequest,
    CreateTaskRunConfigRequest,
    EvalConfigCompareSummary,
    EvalResultSummary,
    EvalRunResult,
    RunEvalConfigRequest,
    UpdateEvalRequest,
)
from .eval_service import EvalService

router = APIRouter(tags=["evaluations"])


def setup_eval_routes(app: FastAPI):
    app.include_router(router, prefix="/api")


@router.post("/projects/{project_id}/tasks/{task_id}/create_evaluator")
async def create_evaluator(
    project_id: str,
    task_id: str,
    request: CreateEvaluatorRequest,
) -> Eval:
    return EvalService.create_evaluator(project_id, task_id, request)


@router.get("/projects/{project_id}/tasks/{task_id}/task_run_configs")
async def get_task_run_configs(
    project_id: str, task_id: str
) -> list[TaskRunConfig]:
    return EvalService.get_task_run_configs(project_id, task_id)


@router.get("/projects/{project_id}/tasks/{task_id}/eval/{eval_id}")
async def get_eval(project_id: str, task_id: str, eval_id: str) -> Eval:
    return EvalService.eval_from_id(project_id, task_id, eval_id)


@router.patch("/projects/{project_id}/tasks/{task_id}/eval/{eval_id}")
async def update_eval(
    project_id: str, task_id: str, eval_id: str, request: UpdateEvalRequest
) -> Eval:
    return EvalService.update_eval(project_id, task_id, eval_id, request)


@router.delete("/projects/{project_id}/tasks/{task_id}/eval/{eval_id}")
async def delete_eval(project_id: str, task_id: str, eval_id: str) -> None:
    EvalService.delete_eval(project_id, task_id, eval_id)


@router.get("/projects/{project_id}/tasks/{task_id}/evals")
async def get_evals(project_id: str, task_id: str) -> list[Eval]:
    return EvalService.get_evals(project_id, task_id)


@router.get("/projects/{project_id}/tasks/{task_id}/eval/{eval_id}/eval_configs")
async def get_eval_configs(
    project_id: str, task_id: str, eval_id: str
) -> list[EvalConfig]:
    return EvalService.get_eval_configs(project_id, task_id, eval_id)


@router.get(
    "/projects/{project_id}/tasks/{task_id}/eval/{eval_id}/eval_config/{eval_config_id}"
)
async def get_eval_config(
    project_id: str, task_id: str, eval_id: str, eval_config_id: str
) -> EvalConfig:
    return EvalService.eval_config_from_id(project_id, task_id, eval_id, eval_config_id)


@router.post("/projects/{project_id}/tasks/{task_id}/task_run_config")
async def create_task_run_config(
    project_id: str,
    task_id: str,
    request: CreateTaskRunConfigRequest,
) -> TaskRunConfig:
    return EvalService.create_task_run_config(project_id, task_id, request)


@router.post(
    "/projects/{project_id}/tasks/{task_id}/eval/{eval_id}/create_eval_config"
)
async def create_eval_config(
    project_id: str,
    task_id: str,
    eval_id: str,
    request: CreateEvalConfigRequest,
) -> EvalConfig:
    return EvalService.create_eval_config(project_id, task_id, eval_id, request)


# JS SSE client (EventSource) doesn't work with POST requests, so we use GET, even though post would be better
@router.get(
    "/projects/{project_id}/tasks/{task_id}/eval/{eval_id}/eval_config/{eval_config_id}/run_task_run_eval"
)
async def run_eval_config(
    project_id: str,
    task_id: str,
    eval_id: str,
    eval_config_id: str,
    run_config_ids: list[str] = Query([]),
    all_run_configs: bool = Query(False),
) -> StreamingResponse:
    return await EvalService.run_eval_config(
        project_id, task_id, eval_id, eval_config_id, run_config_ids, all_run_configs
    )


@router.post(
    "/projects/{project_id}/tasks/{task_id}/eval/{eval_id}/set_current_eval_config/{eval_config_id}"
)
async def set_default_eval_config(
    project_id: str,
    task_id: str,
    eval_id: str,
    eval_config_id: str,
) -> Eval:
    return EvalService.set_default_eval_config(project_id, task_id, eval_id, eval_config_id)


# JS SSE client (EventSource) doesn't work with POST requests, so we use GET, even though post would be better
@router.get(
    "/projects/{project_id}/tasks/{task_id}/eval/{eval_id}/run_eval_config_eval"
)
async def run_eval_config_eval(
    project_id: str,
    task_id: str,
    eval_id: str,
) -> StreamingResponse:
    return await EvalService.run_eval_config_eval(project_id, task_id, eval_id)


@router.get(
    "/projects/{project_id}/tasks/{task_id}/eval/{eval_id}/eval_config/{eval_config_id}/run_config/{run_config_id}/results"
)
async def get_eval_run_results(
    project_id: str,
    task_id: str,
    eval_id: str,
    eval_config_id: str,
    run_config_id: str,
) -> EvalRunResult:
    return EvalService.get_eval_run_results(
        project_id, task_id, eval_id, eval_config_id, run_config_id
    )


# This compares run_configs to each other on a given eval_config. Compare to below which compares eval_configs to each other.
@router.get(
    "/projects/{project_id}/tasks/{task_id}/eval/{eval_id}/eval_config/{eval_config_id}/score_summary"
)
async def get_eval_config_score_summary(
    project_id: str,
    task_id: str,
    eval_id: str,
    eval_config_id: str,
) -> EvalResultSummary:
    return EvalService.get_eval_config_score_summary(
        project_id, task_id, eval_id, eval_config_id
    )


# Compared to above, this is comparing all eval configs to each other, not looking at a single eval config
@router.get(
    "/projects/{project_id}/tasks/{task_id}/eval/{eval_id}/eval_configs_score_summary"
)
async def get_eval_configs_score_summary(
    project_id: str,
    task_id: str,
    eval_id: str,
) -> EvalConfigCompareSummary:
    return EvalService.get_eval_configs_score_summary(project_id, task_id, eval_id)

