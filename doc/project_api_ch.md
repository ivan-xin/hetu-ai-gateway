
# 项目管理 API 接口文档

## 基础信息
- 基础路径: `/api/v1/projects`
- 响应格式: JSON

## API 列表

### 1. 创建项目
- **接口**: POST /api/v1/projects
- **功能**: 创建新项目
- **请求体**:
```json
{
    "name": "项目名称",
    "description": "项目描述(可选)"
}
```
- **响应**:
```json
{
    "id": "项目ID",
    "name": "项目名称",
    "description": "项目描述",
    "created_at": "创建时间"
}
```

### 2. 获取项目列表
- **接口**: GET /api/v1/projects
- **功能**: 获取所有项目
- **响应**:
```json
{
    "projects": [
        {
            "id": "项目ID",
            "name": "项目名称",
            "description": "项目描述",
            "created_at": "创建时间"
        }
    ]
}
```

### 3. 获取单个项目
- **接口**: GET /api/v1/projects/{project_id}
- **功能**: 获取特定项目详情
- **响应**:
```json
{
    "id": "项目ID",
    "name": "项目名称",
    "description": "项目描述",
    "created_at": "创建时间"
}
```

### 4. 更新项目
- **接口**: PUT /api/v1/projects/{project_id}
- **功能**: 更新项目信息
- **请求体**:
```json
{
    "name": "新项目名称(可选)",
    "description": "新项目描述(可选)"
}
```
- **响应**:
```json
{
    "id": "项目ID",
    "name": "项目名称",
    "description": "项目描述",
    "created_at": "创建时间"
}
```

### 5. 删除项目
- **接口**: DELETE /api/v1/projects/{project_id}
- **功能**: 删除指定项目
- **响应**:
```json
{
    "message": "操作结果消息",
    "project_id": "被删除的项目ID"
}
```

### 6. 导入项目
- **接口**: POST /api/v1/projects/import
- **功能**: 导入现有项目
- **请求体**:
```json
{
    "project_path": "项目文件路径"
}
```
- **响应**:
```json
{
    "id": "项目ID",
    "name": "项目名称",
    "description": "项目描述",
    "created_at": "创建时间"
}
```

## 错误处理
所有接口在发生错误时会返回相应的HTTP状态码和错误信息：
```json
{
    "detail": "错误描述信息"
}
```

常见错误码：
- 400: 请求参数错误
- 404: 资源不存在
- 500: 服务器内部错误

## 注意事项
1. 所有时间字段格式为ISO 8601标准
2. 项目名称不能重复
3. 项目路径必须是有效的文件系统路径
