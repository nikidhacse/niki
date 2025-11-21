import logging
from typing import Dict, Optional

from interfaces import ResponseGenerator
from data_models import IntentResult, DialogueResponse

from small_model_response_generator import SmallLLMResponseGenerator

logger = logging.getLogger(__name__)

class LLMManager:
    """
    Manages multiple domain-specific LLM response generators.
    """
    def __init__(self):
        self.generators: Dict[str, ResponseGenerator] = {}
        self.default_generator: Optional[ResponseGenerator] = None

    def register_generator(self, domain: str, generator: ResponseGenerator) -> bool:
        if generator.initialize():
            self.generators[domain] = generator
            logger.info(f"LLMManager: Registered generator for domain '{domain}'")
            return True
        else:
            logger.error(f"LLMManager: Failed to initialize generator for domain '{domain}'")
            return False

    def set_default_generator(self, generator: ResponseGenerator) -> None:
        if generator.initialize():
            self.default_generator = generator
            logger.info("LLMManager: Default generator set")
        else:
            logger.error("LLMManager: Failed to initialize the default generator")

    def generate_response(self, intent_result: IntentResult, domain: Optional[str] = None) -> DialogueResponse:
        if domain and domain in self.generators:
            logger.info(f"LLMManager: Using generator for domain '{domain}'")
            generator = self.generators[domain]
        elif self.default_generator:
            logger.info("LLMManager: Using default generator")
            generator = self.default_generator
        else:
            raise ValueError("No suitable generator found")

        return generator.generate(intent_result)
