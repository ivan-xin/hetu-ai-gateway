from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class TaskBase(BaseModel):
    """任务基础模型"""
    name: str
    description: Optional[str] = None
    project_id: str
    
class TaskCreate(TaskBase):
    """创建任务请求模型"""
    pass

class TaskUpdate(BaseModel):
    """更新任务请求模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TaskResponse(TaskBase):
    """任务响应模型"""
    id: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class TaskListResponse(BaseModel):
    """任务列表响应模型"""
    tasks: List[TaskResponse]

class TaskDeleteResponse(BaseModel):
    """任务删除响应模型"""
    message: str
    task_id: str
