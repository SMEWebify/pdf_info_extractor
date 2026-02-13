"""LLM client module for invoice data extraction."""

import json
import logging
import re  # Ajout de re pour le nettoyage
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from src.config import LLM_CONFIG, SYSTEM_PROMPT, HUMAN_PROMPT, PROCESSING_CONFIG

logger = logging.getLogger(__name__)

class InvoiceLLMClient:
    """Client for interacting with LLM to extract invoice data."""
    
    def __init__(self):
        """Initialize the LLM client."""
        self.llm = ChatOpenAI(**LLM_CONFIG)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
        ])
        self.chain = self.prompt | self.llm
        self.max_retries = PROCESSING_CONFIG["max_retries"]
    
    def extract_line_items(self, table_text: str) -> List[Dict[str, Any]]:
        """Extract line items from table text using LLM."""
        try:
            # Sécurité : si la table est vide, on n'appelle pas l'IA
            if not table_text.strip():
                return []

            response = self.chain.invoke({"table_text": table_text})
            items = self._parse_response(response.content)
            logger.info(f"Extracted {len(items)} line items from table") # Changé debug en info pour voir le succès
            return items
        except Exception as e:
            logger.error(f"Failed to extract line items: {e}")
            return []
    
    def _clean_json_string(self, text: str) -> str:
        """Nettoie le texte pour ne garder que le JSON."""
        # Supprime les blocs de code Markdown (ex: ```json ... ```)
        text = re.sub(r"```json\s?", "", text)
        text = re.sub(r"```", "", text)
        return text.strip()

    def _parse_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse LLM response with robust cleaning and retry logic."""
        current_text = response_text

        for attempt in range(self.max_retries):
            try:
                cleaned_text = self._clean_json_string(current_text)
                if not cleaned_text:
                    raise ValueError("Empty response after cleaning")
                
                return json.loads(cleaned_text)
            
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON parse attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    # Au lieu de renvoyer le texte, on retente l'invocation initiale
                    # ou on demande plus simplement une correction
                    logger.info("Retrying with a simpler request...")
                    retry_msg = f"Your previous output was not valid JSON. Please provide ONLY the JSON array for this data: {current_text[:200]}..."
                    current_text = self.llm.invoke(retry_msg).content
                else:
                    logger.error(f"All JSON parse attempts failed. Final text was: {current_text[:100]}...")
        
        return []
