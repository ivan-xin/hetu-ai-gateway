# 微调 API 接口文档

## 提供商相关接口

### 获取支持的微调提供商列表
- **接口**: GET /api/finetune_providers
- **描述**: 列出所有支持的微调提供商
- **响应**: 返回支持的微调提供商列表

### 获取提供商超参数
- **接口**: GET /api/finetune/hyperparameters/{provider_id}
- **参数**: 
  - provider_id: 提供商标识
- **响应**: 返回该提供商支持的超参数列表

## 数据集相关接口

### 获取数据集分割列表
- **接口**: GET /api/projects/{project_id}/tasks/{task_id}/dataset_splits
- **参数**:
  - project_id: 项目ID
  - task_id: 任务ID
- **响应**: 返回数据集分割列表

### 创建数据集分割
- **接口**: POST /api/projects/{project_id}/tasks/{task_id}/dataset_splits
- **参数**:
  - project_id: 项目ID
  - task_id: 任务ID
  - 请求体: CreateDatasetSplitRequest
- **响应**: 返回创建的数据集分割信息

### 下载JSONL格式数据集
- **接口**: GET /api/download_dataset_jsonl
- **查询参数**:
  - project_id: 项目ID
  - task_id: 任务ID
  - dataset_id: 数据集ID
  - split_name: 分割名称
  - format_type: 格式类型
  - data_strategy: 数据策略
  - system_message_generator: 系统消息生成器（可选）
  - custom_system_message: 自定义系统消息（可选）
  - custom_thinking_instructions: 自定义思考指令（可选）
- **响应**: JSONL文件流

## 微调作业相关接口

### 获取微调作业列表
- **接口**: GET /api/projects/{project_id}/tasks/{task_id}/finetunes
- **参数**:
  - project_id: 项目ID
  - task_id: 任务ID
  - update_status: 是否更新作业状态（查询参数，布尔值，默认false）
- **响应**: 返回微调作业列表

### 获取特定微调作业
- **接口**: GET /api/projects/{project_id}/tasks/{task_id}/finetunes/{finetune_id}
- **参数**:
  - project_id: 项目ID
  - task_id: 任务ID
  - finetune_id: 微调作业ID
- **响应**: 返回微调作业详情及状态

### 更新微调作业
- **接口**: PATCH /api/projects/{project_id}/tasks/{task_id}/finetunes/{finetune_id}
- **参数**:
  - project_id: 项目ID
  - task_id: 任务ID
  - finetune_id: 微调作业ID
  - 请求体: UpdateFinetuneRequest
- **响应**: 返回更新后的微调作业信息

### 创建微调作业
- **接口**: POST /api/projects/{project_id}/tasks/{task_id}/finetunes
- **参数**:
  - project_id: 项目ID
  - task_id: 任务ID
  - 请求体: CreateFinetuneRequest
- **响应**: 返回创建的微调作业信息

## 请求/响应数据结构

### CreateDatasetSplitRequest
创建数据集分割的请求结构

### CreateFinetuneRequest
创建微调作业的请求结构

### UpdateFinetuneRequest
更新微调作业的请求结构

### FinetuneWithStatus
包含状态信息的微调作业结构

### FinetuneProvider
微调提供商信息结构

### FineTuneParameter
微调超参数结构
