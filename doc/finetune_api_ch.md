# 微调 API 接口文档

## 提供商相关接口

### 获取支持的微调提供商列表
- **接口**: GET /api/finetune/providers
- **描述**: 列出所有支持的微调提供商
- **响应**:
```json
{
    "providers": {
        "TOGETHER_AI": "Together AI",
        "FIREWORKS_AI": "Fireworks AI"
    }
}
```
- **注意**: 目前仅支持Together AI，默认 Together AI

### 获取提供商参数
- **接口**: GET /api/finetune/parameters/{provider}
- **参数**: 
  - provider: 提供商标识（TOGETHER_AI/FIREWORKS_AI）
- **响应**:
```json
{
    "parameters": [
        // 参数列表
    ]
}
```

### 获取提供商支持的模型
- **接口**: GET /api/finetune/models
- **响应**:
```json
{
    "providers": [
        // 提供商支持的模型列表
    ]
}
```

## 数据集相关接口

### 上传数据集
- **接口**: POST /api/finetune/upload-dataset
- **参数**: 
  - file: 文件对象（multipart/form-data）
- **响应**:
```json
{
    "filename": "文件名",
    "path": "文件路径"
}
```

### 格式化数据集
- **接口**: POST /api/finetune/format-dataset
- **请求体**:
```json
{
    "dataset_path": "数据集路径",
    "split_name": "分割名称",
    "format_type": "格式类型",
    "data_strategy": "数据策略",
    "system_message": "系统消息",
    "thinking_instructions": "思考指令"
}
```
- **响应**:
```json
{
    "output_path": "输出文件路径"
}
```

### 下载数据集
- **接口**: GET /api/finetune/download-dataset
- **查询参数**:
  - dataset_path: 数据集路径
  - split_name: 分割名称（默认: train）
  - format_type: 格式类型
  - data_strategy: 数据策略
  - system_message: 系统消息（默认: You are a helpful assistant.）
  - thinking_instructions: 思考指令（可选）
- **响应**: 文件流

## 微调作业相关接口

### 创建微调作业
- **接口**: POST /api/finetune/jobs
- **请求体**: 微调作业创建参数
- **响应**:
```json
{
    "job": {
        // 作业详情
    }
}
```
- **Sample请求体**:
```json
{
  "name": "高级微调作业",
  "provider": "TOGETHER_AI",
  "model_name": "togethercomputer/llama-2-7b",
  "dataset_path": "/path/to/dataset.json",
  "parameters": {
    "learning_rate": 0.00002,
    "epochs": 3,
    "batch_size": 8,
    "lora_rank": 16,
    "lora_alpha": 16,
    "lora_dropout": 0.05,
    "warmup_ratio": 0.1
  },
  "description": "这是一个用于客服场景的微调作业",
  "system_message": "你是一个专业的客服助手，擅长解答用户问题。请保持礼貌和专业。",
  "thinking_instructions": "分析用户问题，考虑可能的解决方案，提供清晰的步骤指导。"
}
```

### 获取微调作业列表
- **接口**: GET /api/finetune/jobs
- **查询参数**:
  - update_status: 是否更新作业状态（布尔值，默认false）
- **响应**:
```json
{
    "jobs": [
        // 作业列表
    ]
}
```

### 获取微调作业详情
- **接口**: GET /api/finetune/jobs/{job_id}
- **参数**:
  - job_id: 作业ID
- **响应**:
```json
{
    "job": {
        // 作业详情
    }
}
```

### 取消微调作业
- **接口**: POST /api/finetune/jobs/{job_id}/cancel
- **参数**:
  - job_id: 作业ID
- **响应**:
```json
{
    "job": {
        // 更新后的作业详情
    }
}
```

## 项目任务相关接口

### 获取项目任务下的微调作业列表
- **接口**: GET /api/finetune/projects/{project_id}/tasks/{task_id}/finetunes
- **参数**:
  - project_id: 项目ID
  - task_id: 任务ID
  - update_status: 是否更新状态（查询参数，布尔值）
- **响应**:
```json
{
    "jobs": [
        // 作业列表
    ]
}
```

### 获取项目任务下的特定微调作业
- **接口**: GET /api/finetune/projects/{project_id}/tasks/{task_id}/finetunes/{finetune_id}
- **参数**:
  - project_id: 项目ID
  - task_id: 任务ID
  - finetune_id: 微调作业ID
- **响应**:
```json
{
    "job": {
        // 作业详情
    }
}
```

### 在项目任务下创建微调作业
- **接口**: POST /api/finetune/projects/{project_id}/tasks/{task_id}/finetunes
- **参数**:
  - project_id: 项目ID
  - task_id: 任务ID
  - 请求体: 微调作业创建参数
- **响应**:
```json
{
    "job": {
        // 作业详情
    }
}
```

### 取消项目任务下的微调作业
- **接口**: POST /api/finetune/projects/{project_id}/tasks/{task_id}/finetunes/{finetune_id}/cancel
- **参数**:
  - project_id: 项目ID
  - task_id: 任务ID
  - finetune_id: 微调作业ID
- **响应**:
```json
{
    "job": {
        // 更新后的作业详情
    }
}
```

### 获取数据集分割列表
- **接口**: GET /api/finetune/projects/{project_id}/tasks/{task_id}/dataset_splits
- **参数**:
  - project_id: 项目ID
  - task_id: 任务ID
- **响应**:
```json
{
    "dataset_splits": [
        // 数据集分割列表
    ]
}
```

### 创建数据集分割
- **接口**: POST /api/finetune/projects/{project_id}/tasks/{task_id}/dataset_splits
- **参数**:
  - project_id: 项目ID
  - task_id: 任务ID
- **响应**: 创建结果

### 下载JSONL格式数据集
- **接口**: GET /api/finetune/download_dataset_jsonl
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
