import asyncio
from kiln_ai.adapters.ml_model_list import built_in_models, ModelProviderName

async def print_together_models():
    print("Together.ai models:")
    for model in built_in_models:
        for provider in model.providers:
            if provider.name == ModelProviderName.together_ai and provider.provider_finetune_id:
                print(f"- {model.friendly_name}: {provider.provider_finetune_id}")

if __name__ == "__main__":
    asyncio.run(print_together_models())
