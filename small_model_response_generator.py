from interfaces import ResponseGenerator
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from data_models import DialogueResponse, IntentResult
import logging

logger = logging.getLogger(__name__)

class SmallLLMResponseGenerator(ResponseGenerator):
    def __init__(self, device="cpu", model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        self.device = torch.device(device)
        self.model_name = model_name
        
        print(f"📦 Loading {model_name} on {self.device}...")
        print("   (First time downloads ~2GB, subsequent runs load from cache)")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32 if device == "cpu" else torch.float16,
            low_cpu_mem_usage=True
        )
        self.model = self.model.to(self.device)  # type: ignore
        self.model.eval()
        
        logger.info(f"✓ Model loaded: {model_name}")

    def initialize(self) -> bool:
        return True

    def generate(self, intent_result: IntentResult) -> DialogueResponse:
        input_text = intent_result.raw_text
        
        # TinyLlama chat format
        prompt = f"<|system|>\nYou are a helpful AI assistant.</s>\n<|user|>\n{input_text}</s>\n<|assistant|>\n"
        
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True).to(self.device)
        
        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=150,
                do_sample=True,
                temperature=0.7,
                top_k=50,
                top_p=0.95,
                pad_token_id=self.tokenizer.eos_token_id
            )

        # Decode only new tokens
        completion = self.tokenizer.decode(
            output[0, inputs['input_ids'].shape[-1]:], 
            skip_special_tokens=True
        ).strip()
        
        return DialogueResponse(text=completion)

    def cleanup(self) -> None:
        if hasattr(self, 'model'):
            del self.model
        if hasattr(self, 'tokenizer'):
            del self.tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Model cleaned up")
