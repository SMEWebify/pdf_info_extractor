"""LLM client module for invoice data extraction."""

import json
import logging
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
        """
        Extract line items from table text using LLM.
        
        Args:
            table_text: String representation of the table
            
        Returns:
            List of dictionaries containing extracted line items
        """
        try:
            response = self.chain.invoke({"table_text": table_text})
            items = self._parse_response(response.content)
            logger.debug(f"Extracted {len(items)} line items from table")
            return items
        except Exception as e:
            logger.error(f"Failed to extract line items: {e}")
            return []
    
    def _parse_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse LLM response with retry logic.
        
        Args:
            response_text: Raw response from LLM
            
        Returns:
            Parsed JSON data as list of dictionaries
        """
        for attempt in range(self.max_retries):
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.warning(
                    f"JSON parse attempt {attempt + 1} failed: {e}"
                )
                if attempt < self.max_retries - 1:
                    # Request strict JSON format
                    response_text = self.llm.invoke(
                        f"Output STRICT JSON only: {response_text}"
                    ).content
                else:
                    logger.error("All JSON parse attempts failed")
        
        return []