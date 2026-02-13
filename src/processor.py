"""Main processing logic for invoice extraction."""

import logging
import shutil
import time
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

from src.extractor import PDFTableExtractor
from src.llm_client import InvoiceLLMClient
from src.normalizer import InvoiceItemNormalizer
from src.config import (
    INVOICES_DIR, 
    OUTPUT_DIR, 
    PROCESSED_DIR, 
    PROCESSING_CONFIG, 
    CANONICAL_FIELDS,
    PROCESSING_REPORT_PATH
)

logger = logging.getLogger(__name__)

class InvoiceProcessor:
    """Orchestrates the invoice extraction process with reporting."""
    
    def __init__(self):
        """Initialize processor with required components."""
        self.extractor = PDFTableExtractor()
        self.llm_client = InvoiceLLMClient()
        self.normalizer = InvoiceItemNormalizer()
        self.reports = []  # Liste pour stocker le bilan de chaque fichier

    def process_all_invoices(self, input_dir: Path = INVOICES_DIR) -> pd.DataFrame:
        """Process all PDF invoices, move them, and generate a report."""
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        pdf_files = self._get_pdf_files(input_dir)
        logger.info(f"Found {len(pdf_files)} PDF file(s) to process")
        
        all_line_items = []
        self.reports = [] # Reset reports for this run
        
        for pdf_path in pdf_files:
            start_time = time.time()
            status = "Success"
            error_msg = ""
            items_count = 0
            
            try:
                # 1. Extraction des données
                items = self._process_single_pdf(pdf_path)
                items_count = len(items)
                
                if items_count == 0:
                    status = "Warning: No items found"
                
                all_line_items.extend(items)
                
                # 2. Déplacement du fichier après traitement
                self._move_to_processed(pdf_path)
                
            except Exception as e:
                status = "Error"
                error_msg = str(e)
                logger.error(f"Failed to process {pdf_path.name}: {e}")

            # Enregistrement du bilan pour Laravel
            self.reports.append({
                "filename": pdf_path.name,
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": status,
                "items_extracted": items_count,
                "error_details": error_msg,
                "duration_sec": round(time.time() - start_time, 2)
            })
        
        # Sauvegarde du rapport global après la boucle
        if self.reports:
            self._save_processing_report()
        
        logger.info(f"Total line items extracted: {len(all_line_items)}")
        return self._create_dataframe(all_line_items)

    def _move_to_processed(self, pdf_path: Path):
        """Helper to move processed files to the archive folder."""
        dest_path = PROCESSED_DIR / pdf_path.name
        if dest_path.exists():
            timestamp = int(time.time())
            dest_path = PROCESSED_DIR / f"{pdf_path.stem}_{timestamp}{pdf_path.suffix}"
        
        shutil.move(str(pdf_path), str(dest_path))
        logger.info(f"Moved {pdf_path.name} to {PROCESSED_DIR.name}")

    def _save_processing_report(self):
        """Génère ou met à jour le CSV de suivi pour Laravel."""
        new_report_df = pd.DataFrame(self.reports)
        if PROCESSING_REPORT_PATH.exists():
            try:
                old_report_df = pd.read_csv(PROCESSING_REPORT_PATH)
                final_report_df = pd.concat([old_report_df, new_report_df], ignore_index=True)
            except Exception:
                final_report_df = new_report_df
        else:
            final_report_df = new_report_df
            
        final_report_df.to_csv(PROCESSING_REPORT_PATH, index=False)
        logger.info(f"Processing report updated at {PROCESSING_REPORT_PATH}")

    def _process_single_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Process a single PDF file through extraction and normalization."""
        logger.info(f"Processing {pdf_path.name}")
        line_items = []
        tables = self.extractor.extract_tables(pdf_path)
        
        for table in tables:
            table_text = table.to_string(index=False)
            raw_items = self.llm_client.extract_line_items(table_text)
            
            for item in raw_items:
                normalized = self.normalizer.normalize(item, pdf_path.name)
                line_items.append(normalized)
        
        return line_items

    def _get_pdf_files(self, directory: Path) -> List[Path]:
        """Get all PDF files, ignoring the processed directory."""
        extensions = PROCESSING_CONFIG["supported_extensions"]
        pdf_files = []
        for ext in extensions:
            # Filtre pour éviter de boucler sur le dossier processed s'il est enfant
            pdf_files.extend([f for f in directory.glob(f"*{ext}") if PROCESSED_DIR.name not in f.parts])
        return sorted(pdf_files)

    def _create_dataframe(self, line_items: List[Dict[str, Any]]) -> pd.DataFrame:
        """Create DataFrame from line items with canonical schema."""
        if not line_items:
            return pd.DataFrame(columns=CANONICAL_FIELDS.keys())
        return pd.DataFrame(line_items, columns=CANONICAL_FIELDS.keys())

    def save_results(self, df: pd.DataFrame, output_path: Path = OUTPUT_DIR / "invoices_info.csv") -> None:
        """Save final results to CSV."""
        try:
            df.to_csv(output_path, index=False)
            logger.info(f"Saved results to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            raise
