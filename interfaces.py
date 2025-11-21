"""
Abstract Interfaces Module
Defines abstract base classes for all core components and domain modules
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from data_models import AudioFrame, TranscribedText, IntentResult, DialogueResponse


class ActivationEngine(ABC):
    """
    Abstract interface for wake word detection and system activation.
    
    Implementations: Porcupine, Snowboy, custom deep learning models
    Replaces: MockActivationEngine (in core module)
    """
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the activation engine"""
        pass
    
    @abstractmethod
    def detect(self, audio_frame: AudioFrame) -> bool:
        """
        Detect if wake word/phrase is present in audio.
        
        Args:
            audio_frame: AudioFrame containing audio data
            
        Returns:
            bool: True if wake word detected, False otherwise
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup and release resources"""
        pass


class SpeechToTextProcessor(ABC):
    """
    Abstract interface for speech-to-text processing.
    
    Implementations: Deepgram, AssemblyAI, Google Cloud Speech, Azure Speech, Whisper
    Replaces: MockSpeechToTextProcessor (in core module)
    """
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the STT processor"""
        pass
    
    @abstractmethod
    def transcribe(self, audio_data: bytes, sample_rate: int) -> TranscribedText:
        """
        Convert speech audio to text.
        
        Args:
            audio_data: Raw audio bytes
            sample_rate: Sample rate of audio (e.g., 16000)
            
        Returns:
            TranscribedText: Transcribed text with confidence score
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup and release resources"""
        pass


class IntentRecognizer(ABC):
    """
    Abstract interface for natural language understanding and intent recognition.
    
    Implementations: Rasa, spaCy, Dialogflow, LUIS, custom BERT models, LLMs
    Replaces: MockIntentRecognizer (in core module)
    """
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the intent recognizer"""
        pass
    
    @abstractmethod
    def recognize(self, text: str) -> IntentResult:
        """
        Recognize intent and extract entities from text.
        
        Args:
            text: User input text
            
        Returns:
            IntentResult: Recognized intent with entities and confidence
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup and release resources"""
        pass


class ResponseGenerator(ABC):
    """
    Abstract interface for response generation and dialogue management.
    
    Implementations: GPT-4, Claude, Llama, Rasa Core, custom rule-based systems
    Replaces: MockResponseGenerator (in core module)
    """
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the response generator"""
        pass
    
    @abstractmethod
    def generate(self, intent_result: IntentResult) -> DialogueResponse:
        """
        Generate a dialogue response based on intent.
        
        Args:
            intent_result: Recognized intent and entities
            
        Returns:
            DialogueResponse: Generated response with action and metadata
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup and release resources"""
        pass


class DomainModule(ABC):
    """
    Abstract interface for domain-specific modules.
    
    Implementations: HotelModule, HospitalModule, BankingModule, etc.
    
    Domain modules handle specialized business logic, workflows, and knowledge
    bases tailored to specific use cases.
    """
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the domain module"""
        pass
    
    @abstractmethod
    def handle(self, intent_result: IntentResult) -> DialogueResponse:
        """
        Handle domain-specific intent processing.
        
        Args:
            intent_result: Recognized intent with entities
            
        Returns:
            DialogueResponse: Domain-specific response
        """
        pass
    
    @abstractmethod
    def supports_intent(self, intent: str) -> bool:
        """
        Check if this module supports the given intent.
        
        Args:
            intent: Intent name
            
        Returns:
            bool: True if module supports this intent
        """
        pass
    
    @abstractmethod
    def get_domain_name(self) -> str:
        """
        Get the domain name of this module.
        
        Returns:
            str: Domain name (e.g., 'hotel', 'hospital')
        """
        pass
    
    @abstractmethod
    def get_supported_intents(self) -> List[str]:
        """
        Get list of all supported intents.
        
        Returns:
            List[str]: List of supported intent names
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup and release resources"""
        pass
