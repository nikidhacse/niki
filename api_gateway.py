"""
API Gateway Module
Handles integration between core, domain modules, and external systems
"""

import logging
from typing import Dict, Callable, Any
from data_models import ExternalSystemRequest, ExternalSystemResponse, DialogueResponse

logger = logging.getLogger(__name__)


class APIGateway:
    """
    API Gateway: Integrates core with domain modules and external systems.
    
    Responsibilities:
    - Route requests to domain modules
    - Call external systems (hotel management, hospital patient records)
    - Handle user input/output channels (voice, text)
    - Manage API endpoints
    """
    
    def __init__(self):
        self.routes: Dict[str, Callable] = {}
        self.external_systems: Dict[str, Callable] = {}
        logger.info("APIGateway: Initialized")
    
    def register_route(self, endpoint: str, handler: Callable) -> None:
        """
        Register an API route with a handler function.
        
        Args:
            endpoint: API endpoint path
            handler: Callable that handles the endpoint
        """
        self.routes[endpoint] = handler
        logger.info(f"APIGateway: Registered route '{endpoint}'")
    
    def register_external_system(self, system_name: str, handler: Callable) -> None:
        """
        Register an external system connector.
        
        Args:
            system_name: Name of the external system (e.g., 'hotel_management', 'patient_records')
            handler: Callable that communicates with the system
        """
        self.external_systems[system_name] = handler
        logger.info(f"APIGateway: Registered external system '{system_name}'")
    
    def call_external_system(
        self,
        system_name: str,
        action: str,
        data: Dict[str, Any]
    ) -> ExternalSystemResponse:
        """
        Call an external system.
        
        Args:
            system_name: Name of the external system
            action: Action to perform (e.g., 'book_room', 'schedule_appointment')
            data: Data to send to the system
            
        Returns:
            ExternalSystemResponse: Response from the external system
        """
        logger.info(f"APIGateway: Calling external system '{system_name}' with action '{action}'")
        
        if system_name not in self.external_systems:
            logger.error(f"APIGateway: External system '{system_name}' not registered")
            return ExternalSystemResponse(
                system_name=system_name,
                status="error",
                data={"error": f"System '{system_name}' not found"}
            )
        
        try:
            handler = self.external_systems[system_name]
            result = handler(action, data)
            
            logger.debug(f"APIGateway: Received response from '{system_name}'")
            
            return ExternalSystemResponse(
                system_name=system_name,
                status="success",
                data=result
            )
        
        except Exception as e:
            logger.error(f"APIGateway: Error calling '{system_name}': {str(e)}")
            return ExternalSystemResponse(
                system_name=system_name,
                status="error",
                data={"error": str(e)}
            )
    
    def handle_route(self, endpoint: str, **kwargs) -> Any:
        """
        Handle an API route request.
        
        Args:
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to the handler
            
        Returns:
            Response from the endpoint handler
        """
        logger.debug(f"APIGateway: Handling route '{endpoint}'")
        
        if endpoint not in self.routes:
            logger.error(f"APIGateway: Route '{endpoint}' not found")
            return {"error": f"Route '{endpoint}' not found"}
        
        try:
            handler = self.routes[endpoint]
            return handler(**kwargs)
        
        except Exception as e:
            logger.error(f"APIGateway: Error handling route '{endpoint}': {str(e)}")
            return {"error": str(e)}
    
    def list_routes(self) -> Dict[str, str]:
        """List all registered API routes"""
        return {endpoint: handler.__name__ for endpoint, handler in self.routes.items()}
    
    def list_external_systems(self) -> Dict[str, str]:
        """List all registered external systems"""
        return {system: handler.__name__ for system, handler in self.external_systems.items()}
    
    def cleanup(self) -> None:
        """Cleanup and release resources"""
        self.routes.clear()
        self.external_systems.clear()
        logger.info("APIGateway: Cleanup complete")
