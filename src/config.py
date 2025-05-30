import os
from kiln_ai.utils.config import Config as HetuConfig

class AppConfig:
    # 应用配置
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # 微调配置
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
    MODELS_DIR = os.getenv("MODELS_DIR", "./models")
    
    # 确保目录存在
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

def setup_hetu_config():
    """设置 Hetu 配置"""
    # 设置 API 密钥
    hetu_config = HetuConfig.shared()
    
    # Together AI (用于微调)
    hetu_config.together_api_key = os.getenv("TOGETHER_API_KEY", "")
    
    # Fireworks AI (用于微调)
    # hetu_config.fireworks_api_key = os.getenv("FIREWORKS_API_KEY", "")
    
    # 其他可能需要的提供商
    # hetu_config.openai_api_key = os.getenv("OPENAI_API_KEY", "")
    # hetu_config.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
    
    # 设置自动保存运行结果
    hetu_config.autosave_runs = True
    
    return hetu_config
