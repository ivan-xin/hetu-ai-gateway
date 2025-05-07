from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# 请求模型
class ProjectCreate(BaseModel):
    """创建项目的请求模型"""
    name: str = Field(..., description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")

class ProjectUpdate(BaseModel):
    """更新项目的请求模型"""
    name: Optional[str] = Field(None, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")

class ProjectImport(BaseModel):
    """导入项目的请求模型"""
    project_path: str = Field(..., description="项目文件路径")

# 响应模型
class ProjectResponse(BaseModel):
    """项目响应模型"""
    id: Optional[str] = Field(None, description="项目ID")
    name: str = Field(..., description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    
    class Config:
        orm_mode = True

class ProjectListResponse(BaseModel):
    """项目列表响应模型"""
    projects: List[ProjectResponse] = Field(..., description="项目列表")

class ProjectDeleteResponse(BaseModel):
    """删除项目响应模型"""
    message: str = Field(..., description="操作结果消息")
    project_id: str = Field(..., description="被删除的项目ID")
