import logging
from product_designer_generator import ProductDesigner

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    logger.info("Starting Product Designer (no TripoSR)...")

    designer = ProductDesigner()
    result = designer.generate_design("Test prompt")

    logger.info("Product Designer Output:")
    logger.info(result)
