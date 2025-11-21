"""
Core Receptionist Engine
Main orchestrator for the Modular AI Receptionist Framework
"""

import logging
from typing import Optional, Dict, Any
from interfaces import (
    ActivationEngine,
    SpeechToTextProcessor,
    IntentRecognizer,
    ResponseGenerator
)
from data_models import AudioFrame, DialogueResponse, SystemState
from module_manager import ModuleManager
from api_gateway import APIGateway
from performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)


class ReceptionistCore:
    """
    Core AI Receptionist Engine: Main orchestrator for the framework.
    
    Responsibilities:
    - Orchestrate all components (activation, STT, NLU, response generation)
    - Manage audio processing pipeline
    - Coordinate with domain modules
    - Track system state and performance
    - Handle errors and exceptions
    """
    
    def __init__(self):
        self.state = SystemState.IDLE
        self.activation_engine: Optional[ActivationEngine] = None
        self.stt_processor: Optional[SpeechToTextProcessor] = None
        self.intent_recognizer: Optional[IntentRecognizer] = None
        self.response_generator: Optional[ResponseGenerator] = None
        
        # Core components
        self.module_manager = ModuleManager()
        self.api_gateway = APIGateway()
        self.performance_monitor = PerformanceMonitor()
        
        self.running = False
        logger.info("ReceptionistCore: Initialized")
    
    # ========================================================================
    # COMPONENT CONFIGURATION
    # ========================================================================
    
    def set_activation_engine(self, engine: ActivationEngine) -> bool:
        """
        Configure the activation engine (wake word detection).
        
        Args:
            engine: ActivationEngine instance
            
        Returns:
            bool: True if configuration successful
        """
        try:
            if engine.initialize():
                self.activation_engine = engine
                logger.info("ReceptionistCore: Activation engine configured")
                return True
            return False
        except Exception as e:
            logger.error(f"ReceptionistCore: Error setting activation engine: {str(e)}")
            return False
    
    def set_stt_processor(self, processor: SpeechToTextProcessor) -> bool:
        """
        Configure the speech-to-text processor.
        
        Args:
            processor: SpeechToTextProcessor instance
            
        Returns:
            bool: True if configuration successful
        """
        try:
            if processor.initialize():
                self.stt_processor = processor
                logger.info("ReceptionistCore: STT processor configured")
                return True
            return False
        except Exception as e:
            logger.error(f"ReceptionistCore: Error setting STT processor: {str(e)}")
            return False
    
    def set_intent_recognizer(self, recognizer: IntentRecognizer) -> bool:
        """
        Configure the intent recognizer.
        
        Args:
            recognizer: IntentRecognizer instance
            
        Returns:
            bool: True if configuration successful
        """
        try:
            if recognizer.initialize():
                self.intent_recognizer = recognizer
                logger.info("ReceptionistCore: Intent recognizer configured")
                return True
            return False
        except Exception as e:
            logger.error(f"ReceptionistCore: Error setting intent recognizer: {str(e)}")
            return False
    
    def set_response_generator(self, generator: ResponseGenerator) -> bool:
        """
        Configure the response generator.
        
        Args:
            generator: ResponseGenerator instance
            
        Returns:
            bool: True if configuration successful
        """
        try:
            if generator.initialize():
                self.response_generator = generator
                logger.info("ReceptionistCore: Response generator configured")
                return True
            return False
        except Exception as e:
            logger.error(f"ReceptionistCore: Error setting response generator: {str(e)}")
            return False
    
    # ========================================================================
    # AUDIO PROCESSING PIPELINE
    # ========================================================================
    
    def process_audio(self, audio_frame: AudioFrame) -> Optional[DialogueResponse]:
        """
        Main audio processing pipeline.
        
        Flow:
        1. Activation (optional wake word detection)
        2. Speech-to-Text conversion
        3. Intent Recognition
        4. Response Generation (via domain module or generic generator)
        
        Args:
            audio_frame: AudioFrame containing audio data
            
        Returns:
            DialogueResponse: Generated response or None if error
        """
        try:
            self.state = SystemState.LISTENING
            logger.debug("ReceptionistCore: Changed state to LISTENING")
            
            # Step 1: Wake word activation (optional)
            if self.activation_engine:
                if not self.activation_engine.detect(audio_frame):
                    logger.debug("ReceptionistCore: Wake word not detected")
                    return None
                logger.info("ReceptionistCore: Wake word detected")
            
            # Step 2: Speech-to-text conversion
            if not self.stt_processor:
                logger.error("ReceptionistCore: STT processor not configured")
                self.state = SystemState.ERROR
                self.performance_monitor.record_interaction(success=False)
                return None
            
            self.state = SystemState.PROCESSING
            transcribed = self.stt_processor.transcribe(audio_frame.data, audio_frame.sample_rate)
            self.performance_monitor.record_metric("stt", "confidence", transcribed.confidence)
            logger.info(f"ReceptionistCore: Transcribed - '{transcribed.text}'")
            
            # Step 3: Intent recognition
            if not self.intent_recognizer:
                logger.error("ReceptionistCore: Intent recognizer not configured")
                self.state = SystemState.ERROR
                self.performance_monitor.record_interaction(success=False)
                return None
            
            intent_result = self.intent_recognizer.recognize(transcribed.text)
            self.performance_monitor.record_metric("intent_recognizer", "confidence", intent_result.confidence)
            logger.info(f"ReceptionistCore: Recognized intent '{intent_result.intent}'")
            
            # Step 4: Response generation
            self.state = SystemState.RESPONDING
            
            # Try domain-specific module first
            response = self.module_manager.process_with_module(intent_result)
            
            # Fall back to generic response generator
            if not response and self.response_generator:
                response = self.response_generator.generate(intent_result)
            
            if response:
                logger.info(f"ReceptionistCore: Generated response from {response.module}")
                self.performance_monitor.record_interaction(success=True)
                return response
            else:
                logger.warning("ReceptionistCore: No response generated")
                self.performance_monitor.record_interaction(success=False)
                return None
        
        except Exception as e:
            logger.error(f"ReceptionistCore: Error processing audio: {str(e)}")
            self.state = SystemState.ERROR
            self.performance_monitor.record_interaction(success=False)
            return None
        
        finally:
            self.state = SystemState.IDLE
            logger.debug("ReceptionistCore: Changed state to IDLE")
    
    # ========================================================================
    # LIFECYCLE MANAGEMENT
    # ========================================================================
    
    def start(self) -> None:
        """Start the receptionist system"""
        self.running = True
        logger.info("ReceptionistCore: System started")
    
    def stop(self) -> None:
        """Stop the receptionist system"""
        self.running = False
        logger.info("ReceptionistCore: System stopped")
    
    def is_running(self) -> bool:
        """Check if system is running"""
        return self.running
    
    # ========================================================================
    # STATUS AND REPORTING
    # ========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current system status.
        
        Returns:
            Dict: System status information
        """
        return {
            "running": self.running,
            "state": self.state.value,
            "active_module": self.module_manager.get_active_module_name(),
            "registered_modules": list(self.module_manager.list_modules().keys()),
            "timestamp": str(__import__('datetime').datetime.now().isoformat())
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance metrics report"""
        return self.performance_monitor.get_metrics_summary()
    
    def get_feedback_report(self) -> Dict[str, Any]:
        """Get feedback for module updates"""
        return self.performance_monitor.get_feedback_report()
    
    # ========================================================================
    # CLEANUP
    # ========================================================================
    
    def cleanup(self) -> None:
        """Cleanup all resources and release connections"""
        try:
            logger.info("ReceptionistCore: Starting cleanup")
            
            if self.activation_engine:
                self.activation_engine.cleanup()
                logger.debug("ReceptionistCore: Activation engine cleaned up")
            
            if self.stt_processor:
                self.stt_processor.cleanup()
                logger.debug("ReceptionistCore: STT processor cleaned up")
            
            if self.intent_recognizer:
                self.intent_recognizer.cleanup()
                logger.debug("ReceptionistCore: Intent recognizer cleaned up")
            
            if self.response_generator:
                self.response_generator.cleanup()
                logger.debug("ReceptionistCore: Response generator cleaned up")
            
            self.module_manager.cleanup_all()
            self.api_gateway.cleanup()
            
            self.running = False
            self.state = SystemState.IDLE
            
            logger.info("ReceptionistCore: Cleanup complete")
        
        except Exception as e:
            logger.error(f"ReceptionistCore: Error during cleanup: {str(e)}")