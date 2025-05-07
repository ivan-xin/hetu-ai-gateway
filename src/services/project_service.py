import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from kiln_ai.datamodel import Project
from kiln_server.project_api import project_from_id, default_project_path, add_project_to_config

class ProjectService:
    """项目管理服务，封装Kiln项目API的功能"""
    
    def create_project(self, name: str, description: Optional[str] = None) -> Project:
        """创建新项目"""
        project_path = os.path.join(default_project_path(), name)
        if os.path.exists(project_path):
            raise ValueError(f"项目文件夹已存在: {name}。请选择不同的名称或重命名现有文件夹。")

        # 创建项目文件夹
        os.makedirs(project_path)
        
        # 创建项目对象
        project = Project(name=name, description=description or "")
        
        # 保存项目文件
        project_file = os.path.join(project_path, "project.kiln")
        project.path = Path(project_file)
        project.save_to_file()

        # 添加到项目列表
        add_project_to_config(project_file)

        return project
    
    def get_projects(self) -> List[Project]:
        """获取所有项目"""
        from kiln_ai.utils.config import Config
        
        project_paths = Config.shared().projects
        projects = []
        
        for project_path in project_paths if project_paths is not None else []:
            try:
                project = Project.load_from_file(project_path)
                projects.append(project)
            except Exception:
                # 跳过已删除的文件
                continue
                
        return projects
    
    def get_project(self, project_id: str) -> Project:
        """获取特定项目"""
        return project_from_id(project_id)
    
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Project:
        """更新项目信息"""
        original_project = self.get_project(project_id)
        
        # 应用更新
        for key, value in updates.items():
            setattr(original_project, key, value)
            
        # 保存更新
        original_project.save_to_file()
        return original_project
    
    def delete_project(self, project_id: str) -> bool:
        """从配置中移除项目（不删除文件）"""
        project = self.get_project(project_id)
        
        # 从配置中移除
        from kiln_ai.utils.config import Config
        projects_before = Config.shared().projects
        projects_after = [p for p in projects_before if p != str(project.path)]
        Config.shared().save_setting("projects", projects_after)
        
        return True
    
    def import_project(self, project_path: str) -> Project:
        """导入现有项目"""
        if not os.path.exists(project_path):
            raise ValueError(f"项目文件不存在: {project_path}")
            
        try:
            project = Project.load_from_file(Path(project_path))
        except Exception as e:
            raise ValueError(f"加载项目失败，文件可能无效: {e}")
            
        # 添加到项目列表
        add_project_to_config(project_path)
        
        return project
