"""
Module Manager
Manages domain-specific modules: registration, switching, and communication
"""

import logging
from typing import Dict, Optional, List
from interfaces import DomainModule
from data_models import IntentResult, DialogueResponse

logger = logging.getLogger(__name__)


class ModuleManager:
    """
    Module Manager: Controls loading, swapping, and communication with domain modules.
    
    Responsibilities:
    - Register domain-specific modules
    - Switch between active modules
    - Route intents to appropriate modules
    - Manage module lifecycle (initialization, cleanup)
    """
    
    def __init__(self):
        self.modules: Dict[str, DomainModule] = {}
        self.active_module: Optional[str] = None
        logger.info("ModuleManager: Initialized")
    
    def register_module(self, domain_name: str, module: DomainModule) -> bool:
        """
        Register a new domain-specific module.
        
        Args:
            domain_name: Unique identifier for the domain (e.g., 'hotel', 'hospital')
            module: Instance of DomainModule
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        try:
            if module.initialize():
                self.modules[domain_name] = module
                logger.info(f"ModuleManager: Registered module '{domain_name}'")
                return True
            else:
                logger.error(f"ModuleManager: Failed to initialize module '{domain_name}'")
                return False
        except Exception as e:
            logger.error(f"ModuleManager: Error registering '{domain_name}': {str(e)}")
            return False
    
    def switch_module(self, domain_name: str) -> bool:
        """
        Switch to a different domain module.
        
        Args:
            domain_name: Name of the domain module to switch to
            
        Returns:
            bool: True if switch successful, False if module not found
        """
        if domain_name not in self.modules:
            logger.error(f"ModuleManager: Module '{domain_name}' not found")
            return False
        
        self.active_module = domain_name
        logger.info(f"ModuleManager: Switched to module '{domain_name}'")
        return True
    
    def get_active_module(self) -> Optional[DomainModule]:
        """
        Get the currently active domain module.
        
        Returns:
            DomainModule: Active module or None if no module is active
        """
        if self.active_module and self.active_module in self.modules:
            return self.modules[self.active_module]
        return None
    
    def get_active_module_name(self) -> Optional[str]:
        """Get the name of the currently active module"""
        return self.active_module
    
    def process_with_module(self, intent_result: IntentResult) -> Optional[DialogueResponse]:
        """
        Process intent with the active domain module.
        
        Args:
            intent_result: Recognized intent to process
            
        Returns:
            DialogueResponse: Response from the module or None if no module handles it
        """
        module = self.get_active_module()
        if module and module.supports_intent(intent_result.intent):
            logger.debug(f"ModuleManager: Processing with module '{self.active_module}'")
            return module.handle(intent_result)
        
        logger.debug("ModuleManager: No active module or module doesn't support intent")
        return None
    
    def list_modules(self) -> Dict[str, str]:
        """
        List all registered modules with their domain names.
        
        Returns:
            Dict: Mapping of module names to domain names
        """
        return {name: module.get_domain_name() for name, module in self.modules.items()}
    
    def get_module_intents(self, domain_name: str) -> Optional[List[str]]:
        """
        Get all supported intents for a specific module.
        
        Args:
            domain_name: Name of the domain module
            
        Returns:
            List[str]: List of supported intents or None if module not found
        """
        if domain_name in self.modules:
            return self.modules[domain_name].get_supported_intents()
        return None
    
    def has_module(self, domain_name: str) -> bool:
        """Check if a module is registered"""
        return domain_name in self.modules
    
    def get_all_supported_intents(self) -> Dict[str, List[str]]:
        """
        Get all supported intents across all registered modules.
        
        Returns:
            Dict: Mapping of module names to their supported intents
        """
        return {
            name: module.get_supported_intents()
            for name, module in self.modules.items()
        }
    
    def cleanup_all(self) -> None:
        """Cleanup all registered modules and release resources"""
        for domain_name, module in self.modules.items():
            try:
                module.cleanup()
                logger.info(f"ModuleManager: Cleaned up module '{domain_name}'")
            except Exception as e:
                logger.error(f"ModuleManager: Error cleaning up '{domain_name}': {str(e)}")
        
        self.modules.clear()
        self.active_module = None
        logger.info("ModuleManager: All modules cleaned up")
