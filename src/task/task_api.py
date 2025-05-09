from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List

from kiln_ai.datamodel import Task
from .task_service import TaskService

router = APIRouter(prefix="/api", tags=["tasks"])

# 依赖注入
def get_task_service():
    return TaskService()

# API路由
@router.post("/projects/{project_id}/task")
async def create_task(
    project_id: str, 
    task_data: Dict[str, Any],
    service: TaskService = Depends(get_task_service)
) -> Task:
    """创建新任务"""
    try:
        task = service.create_task(project_id, task_data)
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/projects/{project_id}/task/{task_id}")
async def update_task(
    project_id: str, 
    task_id: str, 
    task_updates: Dict[str, Any],
    service: TaskService = Depends(get_task_service)
) -> Task:
    """更新任务信息"""
    try:
        updated_task = service.update_task(project_id, task_id, task_updates)
        return updated_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/projects/{project_id}/task/{task_id}")
async def delete_task(
    project_id: str, 
    task_id: str,
    service: TaskService = Depends(get_task_service)
) -> None:
    """删除任务"""
    try:
        service.delete_task(project_id, task_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/projects/{project_id}/tasks")
async def get_tasks(
    project_id: str,
    service: TaskService = Depends(get_task_service)
) -> List[Task]:
    """获取项目下的所有任务"""
    try:
        tasks = service.get_tasks(project_id)
        return tasks
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/projects/{project_id}/tasks/{task_id}")
async def get_task(
    project_id: str, 
    task_id: str,
    service: TaskService = Depends(get_task_service)
) -> Task:
    """获取特定任务"""
    try:
        task = service.get_task(project_id, task_id)
        return task
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
