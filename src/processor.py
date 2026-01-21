"""Main processing logic for invoice extraction."""

import logging
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

from src.extractor import PDFTableExtractor
from src.llm_client import InvoiceLLMClient
from src.normalizer import InvoiceItemNormalizer
from src.config import INVOICES_DIR, OUTPUT_DIR, PROCESSING_CONFIG, CANONICAL_FIELDS

logger = logging.getLogger(__name__)


class InvoiceProcessor:
    """Orchestrates the invoice extraction process."""
    
    def __init__(self):
        """Initialize processor with required components."""
        self.extractor = PDFTableExtractor()
        self.llm_client = InvoiceLLMClient()
        self.normalizer = InvoiceItemNormalizer()
    
    def process_all_invoices(self, input_dir: Path = INVOICES_DIR) -> pd.DataFrame:
        """
        Process all PDF invoices in the input directory.
        
        Args:
            input_dir: Directory containing PDF files
            
        Returns:
            DataFrame containing all extracted line items
        """
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        pdf_files = self._get_pdf_files(input_dir)
        logger.info(f"Found {len(pdf_files)} PDF file(s) to process")
        
        all_line_items = []
        
        for pdf_path in pdf_files:
            items = self._process_single_pdf(pdf_path)
            all_line_items.extend(items)
        
        logger.info(f"Total line items extracted: {len(all_line_items)}")
        
        return self._create_dataframe(all_line_items)
    
    def _process_single_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """
        Process a single PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of normalized line items
        """
        logger.info(f"Processing {pdf_path.name}")
        line_items = []
        
        try:
            tables = self.extractor.extract_tables(pdf_path)
            
            for table in tables:
                table_text = table.to_string(index=False)
                raw_items = self.llm_client.extract_line_items(table_text)
                
                for item in raw_items:
                    normalized = self.normalizer.normalize(
                        item, 
                        pdf_path.name
                    )
                    line_items.append(normalized)
            
            logger.info(
                f"Extracted {len(line_items)} items from {pdf_path.name}"
            )
        except Exception as e:
            logger.error(f"Error processing {pdf_path.name}: {e}")
        
        return line_items
    
    def _get_pdf_files(self, directory: Path) -> List[Path]:
        """
        Get all PDF files from directory.
        
        Args:
            directory: Directory to search
            
        Returns:
            List of PDF file paths
        """
        extensions = PROCESSING_CONFIG["supported_extensions"]
        pdf_files = []
        
        for ext in extensions:
            pdf_files.extend(directory.glob(f"*{ext}"))
        
        return sorted(pdf_files)
    
    def _create_dataframe(self, line_items: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Create DataFrame from line items.
        
        Args:
            line_items: List of normalized line items
            
        Returns:
            DataFrame with canonical column order
        """
        if not line_items:
            logger.warning("No line items to create DataFrame")
            return pd.DataFrame(columns=CANONICAL_FIELDS.keys())
        
        return pd.DataFrame(line_items, columns=CANONICAL_FIELDS.keys())
    
    def save_results(
        self, 
        df: pd.DataFrame, 
        output_path: Path = OUTPUT_DIR / "invoices_info.csv"
    ) -> None:
        """
        Save results to CSV file.
        
        Args:
            df: DataFrame to save
            output_path: Path for output CSV file
        """
        try:
            df.to_csv(output_path, index=False)
            logger.info(f"Saved results to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            raise