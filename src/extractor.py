"""PDF table extraction module."""

import logging
from pathlib import Path
from typing import List
import pandas as pd
import tabula

logger = logging.getLogger(__name__)


class PDFTableExtractor:
    """Extracts tables from PDF files using tabula."""
    
    @staticmethod
    def extract_tables(pdf_path: Path) -> List[pd.DataFrame]:
        """
        Extract all tables from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of pandas DataFrames containing extracted tables
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If extraction fails
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            logger.info(f"Extracting tables from {pdf_path.name}")
            tables = tabula.read_pdf(
                str(pdf_path),
                pages='all',
                multiple_tables=True
            )
            logger.info(f"Extracted {len(tables)} table(s) from {pdf_path.name}")
            return tables
        except Exception as e:
            logger.error(f"Failed to extract tables from {pdf_path.name}: {e}")
            raise