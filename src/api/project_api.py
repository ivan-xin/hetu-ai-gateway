from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ..models.project import (
    ProjectCreate, ProjectUpdate, ProjectImport,
    ProjectResponse, ProjectListResponse, ProjectDeleteResponse
)
from ..services.project_service import ProjectService
from kiln_ai.datamodel import Project

router = APIRouter(prefix="/api", tags=["projects"])

# 依赖注入
def get_project_service():
    return ProjectService()

# API路由
@router.post("/project", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    service: ProjectService = Depends(get_project_service)
):
    """创建新项目"""
    try:
        project = service.create_project(
            name=project_data.name,
            description=project_data.description
        )
        # 将Project对象转换为ProjectResponse
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            created_at=project.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/projects", response_model=ProjectListResponse)
async def get_projects(service: ProjectService = Depends(get_project_service)):
    """获取所有项目"""
    projects = service.get_projects()
    # 将Project对象列表转换为ProjectResponse列表
    project_responses = [
        ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            created_at=p.created_at,
        ) for p in projects
    ]
    return ProjectListResponse(projects=project_responses)

@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """获取特定项目"""
    try:
        project = service.get_project(project_id)
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            created_at=project.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"项目未找到: {project_id}")

@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    updates: ProjectUpdate,
    service: ProjectService = Depends(get_project_service)
):
    """更新项目信息"""
    try:
        project = service.update_project(
            project_id=project_id,
            updates=updates.dict(exclude_unset=True)
        )
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            created_at=project.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"更新项目失败: {str(e)}")

@router.delete("/projects/{project_id}", response_model=ProjectDeleteResponse)
async def delete_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """删除项目（从配置中移除）"""
    try:
        service.delete_project(project_id)
        return ProjectDeleteResponse(
            message="项目已成功移除",
            project_id=project_id
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"删除项目失败: {str(e)}")

@router.post("/import-project", response_model=ProjectResponse)
async def import_project(
    import_data: ProjectImport,
    service: ProjectService = Depends(get_project_service)
):
    """导入现有项目"""
    try:
        project = service.import_project(import_data.project_path)
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            created_at=project.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))