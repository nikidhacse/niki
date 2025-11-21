import logging
logger = logging.getLogger(__name__)

class ProductDesigner:
    """
    Product Designer module WITHOUT TripoSR.
    Only text-based design suggestions.
    """
    def __init__(self):
        logger.info("ProductDesigner: Initialized (NO 3D GENERATION)")

    def generate_design(self, prompt: str):
        logger.warning("3D model generation disabled (TripoSR removed). Returning placeholder.")
        return {
            "status": "ok",
            "model_generated": False,
            "message": "3D model generation disabled on this platform.",
            "design_summary": f"High-level design concept based on: {prompt}",
            "placeholder_model_path": None
        }
