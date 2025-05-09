from typing import Dict, Any, List
from kiln_ai.datamodel import Task
from kiln_server.project_api import project_from_id

class TaskService:
    """任务管理服务，封装任务相关功能"""
    
    def task_from_id(self, project_id: str, task_id: str) -> Task:
        """根据ID获取任务"""
        parent_project = project_from_id(project_id)
        task = Task.from_id_and_parent_path(task_id, parent_project.path)
        if task:
            return task
        raise ValueError(f"Task not found. ID: {task_id}")
    
    def create_task(self, project_id: str, task_data: Dict[str, Any]) -> Task:
        """创建新任务"""
        if "id" in task_data:
            raise ValueError("Task ID cannot be set by client.")
            
        parent_project = project_from_id(project_id)

        task = Task.validate_and_save_with_subrelations(
            task_data, parent=parent_project
        )
        
        if task is None:
            raise ValueError("Failed to create task.")
        if not isinstance(task, Task):
            raise ValueError("Failed to create task.")

        return task
    
    def update_task(self, project_id: str, task_id: str, task_updates: Dict[str, Any]) -> Task:
        """更新任务信息"""
        if "input_json_schema" in task_updates or "output_json_schema" in task_updates:
            raise ValueError("Input and output JSON schemas cannot be updated.")
            
        if "id" in task_updates and task_updates["id"] != task_id:
            raise ValueError("Task ID cannot be changed by client in a patch.")
            
        original_task = self.task_from_id(project_id, task_id)
        updated_task_data = original_task.model_copy(update=task_updates)
        updated_task = Task.validate_and_save_with_subrelations(
            updated_task_data.model_dump(), parent=original_task.parent
        )
        
        if updated_task is None:
            raise ValueError("Failed to update task.")
        if not isinstance(updated_task, Task):
            raise ValueError("Failed to update task.")

        return updated_task
    
    def delete_task(self, project_id: str, task_id: str) -> None:
        """删除任务"""
        task = self.task_from_id(project_id, task_id)
        task.delete()
    
    def get_tasks(self, project_id: str) -> List[Task]:
        """获取项目下的所有任务"""
        parent_project = project_from_id(project_id)
        return parent_project.tasks()
    
    def get_task(self, project_id: str, task_id: str) -> Task:
        """获取特定任务"""
        return self.task_from_id(project_id, task_id)
