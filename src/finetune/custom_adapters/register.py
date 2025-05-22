from kiln_ai.adapters.fine_tune.finetune_registry import finetune_registry
from kiln_ai.adapters.ml_model_list import ModelProviderName
from .together_finetune_adapter import CustomTogetherFinetune

def register_custom_adapters():
    """
    Register custom fine-tune adapters to override the default ones.
    """
    # 替换 Together.ai 适配器
    finetune_registry[ModelProviderName.together_ai] = CustomTogetherFinetune
