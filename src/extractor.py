"""PDF table extraction module."""

import logging
import os
import jpype
from pathlib import Path
from typing import List
import pandas as pd
import tabula

logger = logging.getLogger(__name__)

# --- CORRECTIF JPYPE ---
try:
    if not jpype.isJVMStarted():
        # On localise le JAR de support qui pose problème
        jpype_jar = os.path.join(os.path.dirname(jpype.__file__), "org.jpype.jar")
        
        # On démarre la JVM explicitement avec le bon classpath
        logger.info("Initializing JVM for PDF extraction...")
        jpype.startJVM(convertStrings=False, classpath=[jpype_jar])
except Exception as e:
    logger.warning(f"Note: Manual JVM start info/error: {e}")
# -----------------------

class PDFTableExtractor:
    """Extracts tables from PDF files using tabula."""
    
    @staticmethod
    def extract_tables(pdf_path: Path) -> List[pd.DataFrame]:
        """
        Extract all tables from a PDF file.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            logger.info(f"Extracting tables from {pdf_path.name}")
            # tabula utilisera la JVM déjà démarrée ci-dessus
            tables = tabula.read_pdf(
                str(pdf_path),
                pages='all',
                multiple_tables=True,
                java_options=["-Dfile.encoding=UTF8"] # Optionnel : aide pour les accents
            )
            logger.info(f"Extracted {len(tables)} table(s) from {pdf_path.name}")
            return tables
        except Exception as e:
            logger.error(f"Failed to extract tables from {pdf_path.name}: {e}")
            raise
