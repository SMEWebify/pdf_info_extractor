"""Configuration module for invoice extraction project."""

import os
from pathlib import Path
from typing import Dict, Any
import dotenv

# Directory paths
BASE_DIR = Path(__file__).parent.parent

INVOICES_DIR = Path(r"C:\laragon\www\WebErpMesv2\storage\app\public\invoices_files")
OUTPUT_DIR = Path(r"C:\laragon\www\WebErpMesv2\storage\app\public\output")
PROCESSED_DIR = OUTPUT_DIR / "processed"

# On crée les dossiers (mkdir fonctionne maintenant car ce sont des objets Path)
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
PROCESSED_DIR.mkdir(exist_ok=True, parents=True)

# Le chemin du fichier de rapport (concaténation avec / )
PROCESSING_REPORT_PATH = OUTPUT_DIR / "processing_report.csv"


# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)
dotenv.load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY not found in environment variables. "
        "Please check your .env file."
    )

# LLM Configuration
LLM_CONFIG = {
    #"model": "meta-llama/llama-3.3-70b-instruct:free",
    #"base_url": "https://openrouter.ai/api/v1",
    #"api_key": os.getenv("OPENROUTER_API_KEY"),
    #"temperature": 0,
	"model": "google/gemini-2.0-flash-001", 
    "base_url": "https://openrouter.ai/api/v1",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "temperature": 0,
	"response_format": { "type": "json_object" }
}

# Canonical schema for invoice line items
CANONICAL_FIELDS = {
    "reference": None,
    "product": None,
    "quantity": None,
    "unit_price": None,
    "total_price": None,
    "source_pdf": None,
}

# Processing configuration
PROCESSING_CONFIG = {
    "max_retries": 2,
    "supported_extensions": [".pdf"],
}

# Prompts
SYSTEM_PROMPT = """ou are a data extraction engine.
Output ONLY a valid JSON array of objects. 
DO NOT include markdown formatting like ```json. 
DO NOT include any text before or after the JSON
. Your task is to extract ONLY invoice line items from raw tables extracted from a PDF. 

STRICT RULES: 
- Output STRICT JSON only 
- No markdown 
- No explanations 
- No comments 
- Do NOT invent values 
- Ignore rows that are not product or service line items 
- Missing values are usually extraction and structural mistakes 
- Convert decimal commas to dots 
- Ensure numeric fields are numbers, not strings 
- Output an empty JSON array if no line items are found 
- Ignore metadata tables

OUTPUT FORMAT:
- Output STRICT JSON only
- Output an array of objects
- All products have a reference 
- Each object MUST contain EXACTLY these keys
- If an object misses one of these keys, set its value to null:

reference
product
quantity
unit_price
total_price

The invoice language may be French.
"""

HUMAN_PROMPT = """Extract invoice line items from the following table.

TABLE DATA:
{table_text}
"""
