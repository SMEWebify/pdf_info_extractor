"""Data normalization module for invoice line items."""

import logging
from typing import Dict, Any
from src.config import CANONICAL_FIELDS

logger = logging.getLogger(__name__)


class InvoiceItemNormalizer:
    """Normalizes extracted invoice items to canonical schema."""
    
    @staticmethod
    def normalize(item: Dict[str, Any], source_pdf: str) -> Dict[str, Any]:
        """
        Normalize a single invoice line item to canonical schema.
        
        Args:
            item: Raw extracted item dictionary
            source_pdf: Name of the source PDF file
            
        Returns:
            Normalized dictionary with canonical fields
        """
        normalized = dict(CANONICAL_FIELDS)
        
        # Handle description field variations
        normalized["product"] = (
            item.get("description") or 
            item.get("name") or 
            item.get("product")
        )
        
        # Copy existing canonical fields
        for field in CANONICAL_FIELDS:
            if field in item:
                normalized[field] = item[field]
        
        # Add source
        normalized["source_pdf"] = source_pdf
        
        # Type conversions
        normalized["quantity"] = InvoiceItemNormalizer._safe_int(
            normalized["quantity"]
        )
        normalized["unit_price"] = InvoiceItemNormalizer._safe_float(
            normalized["unit_price"]
        )
        normalized["total_price"] = InvoiceItemNormalizer._safe_float(
            normalized["total_price"]
        )
        
        return normalized
    
    @staticmethod
    def _safe_int(value: Any) -> int | None:
        """
        Safely convert value to integer.
        
        Args:
            value: Value to convert
            
        Returns:
            Integer value or None if conversion fails
        """
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            logger.debug(f"Failed to convert {value} to int: {e}")
            return None
    
    @staticmethod
    def _safe_float(value: Any) -> float | None:
        """
        Safely convert value to float.
        
        Args:
            value: Value to convert
            
        Returns:
            Float value or None if conversion fails
        """
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError) as e:
            logger.debug(f"Failed to convert {value} to float: {e}")
            return None