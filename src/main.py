import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import AppConfig, setup_kiln_config
from .finetune.v1.finetune_api import router as finetune_router

# 初始化 Kiln 配置
setup_kiln_config()

# 创建 FastAPI 应用
app = FastAPI(
    title="Kiln Fine-Tuning Service",
    description="A service for fine-tuning language models using Kiln-AI",
    version="0.1.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(finetune_router)

# 异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    if isinstance(exc, HTTPException):
        return exc
    return HTTPException(status_code=500, detail=str(exc))

# 启动服务器
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=AppConfig.HOST,
        port=AppConfig.PORT,
        reload=AppConfig.DEBUG
    )
