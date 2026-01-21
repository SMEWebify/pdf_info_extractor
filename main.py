"""Main entry point for invoice extraction application."""

import logging
import sys
from pathlib import Path
import dotenv

from src.processor import InvoiceProcessor
from src.config import OUTPUT_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(OUTPUT_DIR / 'extraction.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main execution function."""
    try:
        # Load environment variables
        dotenv.load_dotenv()
        logger.info("Starting invoice extraction process")
        
        # Initialize processor
        processor = InvoiceProcessor()
        
        # Process all invoices
        df = processor.process_all_invoices()
        
        # Save results
        if not df.empty:
            processor.save_results(df)
            logger.info("Invoice extraction completed successfully")
        else:
            logger.warning("No line items extracted from any invoices")
        
        return 0
    
    except FileNotFoundError as e:
        logger.error(f"File/directory not found: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())