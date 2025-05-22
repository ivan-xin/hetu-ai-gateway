from typing import Tuple
from kiln_ai.adapters.fine_tune.together_finetune import TogetherFinetune, _completed_statuses
from kiln_ai.adapters.fine_tune.base_finetune import FineTuneStatus, FineTuneStatusType

class CustomTogetherFinetune(TogetherFinetune):
    """
    Custom Together.ai fine-tuning adapter that ensures fine_tune_model_id is set correctly.
    """
    
    async def _status(self) -> Tuple[FineTuneStatus, str | None]:
        status, job_id = await super()._status()
        
        # 当微调完成时，确保 fine_tune_model_id 已设置
        if status.status == FineTuneStatusType.completed and not self.datamodel.fine_tune_model_id:
            try:
                fine_tuning_job_id = self.datamodel.provider_id
                if fine_tuning_job_id:
                    together_finetune = self.client.fine_tuning.retrieve(id=fine_tuning_job_id)
                    if hasattr(together_finetune, 'output_name') and together_finetune.output_name:
                        self.datamodel.fine_tune_model_id = together_finetune.output_name
                        if self.datamodel.path:
                            self.datamodel.save_to_file()
            except Exception as e:
                # 记录错误但不改变状态
                print(f"Error updating fine_tune_model_id: {e}")
        
        return status, job_id
