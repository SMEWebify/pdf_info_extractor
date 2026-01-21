"""Configuration module for invoice extraction project."""

import os
from pathlib import Path
from typing import Dict, Any
import dotenv
# Directory paths
BASE_DIR = Path(__file__).parent.parent
INVOICES_DIR = BASE_DIR / "invoices_files"
OUTPUT_DIR = BASE_DIR / "output"

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
    "model": "meta-llama/llama-3.3-70b-instruct:free",
    "base_url": "https://openrouter.ai/api/v1",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "temperature": 0,
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
SYSTEM_PROMPT = """You are a data extraction engine. Your task is to extract ONLY invoice line items from raw tables extracted from a PDF. 

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