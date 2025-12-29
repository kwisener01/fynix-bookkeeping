"""
Fynix Systems - Receipt OCR with Claude Vision
===============================================
Extracts structured data from receipt images using Claude's vision capabilities.
"""

import os
import base64
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
import anthropic
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ReceiptOCR")


@dataclass
class ReceiptExtraction:
    """Structured receipt data extracted via OCR."""
    vendor: str
    date: datetime
    total: float
    tax: Optional[float]
    line_items: List[Dict[str, Any]]
    payment_method: Optional[str]
    receipt_number: Optional[str]
    confidence: float
    raw_response: Optional[str] = None


class ReceiptOCR:
    """
    Extract structured data from receipt images using Claude Vision API.

    Handles:
    - Photos of paper receipts
    - PDF receipts
    - Screenshots
    - Low quality images
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize with Anthropic API key.

        Args:
            api_key: Anthropic API key. If None, reads from ANTHROPIC_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = anthropic.Anthropic(api_key=self.api_key)

    async def extract_from_file(self, file_path: str) -> ReceiptExtraction:
        """
        Extract receipt data from a local file.

        Args:
            file_path: Path to receipt image (JPG, PNG, PDF)

        Returns:
            ReceiptExtraction with structured data
        """
        # Read and encode image
        with open(file_path, 'rb') as f:
            image_data = f.read()

        # Determine media type
        ext = Path(file_path).suffix.lower()
        media_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        media_type = media_type_map.get(ext, 'image/jpeg')

        return await self.extract_from_bytes(image_data, media_type)

    async def extract_from_bytes(
        self,
        image_data: bytes,
        media_type: str = "image/jpeg"
    ) -> ReceiptExtraction:
        """
        Extract receipt data from image bytes.

        Args:
            image_data: Raw image bytes
            media_type: MIME type (image/jpeg, image/png, etc.)

        Returns:
            ReceiptExtraction with structured data
        """
        # Encode to base64
        image_base64 = base64.standard_b64encode(image_data).decode('utf-8')

        # Call Claude Vision
        logger.info("Sending image to Claude Vision for OCR extraction...")

        message = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": self._get_extraction_prompt()
                    }
                ]
            }]
        )

        # Parse response
        response_text = message.content[0].text
        logger.info("Received response from Claude Vision")

        return self._parse_response(response_text)

    def _get_extraction_prompt(self) -> str:
        """
        Returns the prompt for Claude to extract receipt data.
        """
        return """Analyze this receipt image and extract the following information. Return ONLY valid JSON with no additional text.

Required JSON structure:
{
    "vendor": "vendor/business name",
    "date": "YYYY-MM-DD",
    "total": 123.45,
    "tax": 12.34,
    "subtotal": 111.11,
    "line_items": [
        {
            "description": "item description",
            "quantity": 1,
            "unit_price": 10.00,
            "total": 10.00
        }
    ],
    "payment_method": "cash/credit/debit/check",
    "receipt_number": "receipt or invoice number if visible",
    "confidence": 0.95
}

Instructions:
- vendor: Extract the business name from the top of the receipt
- date: Parse the transaction date in YYYY-MM-DD format
- total: The final total amount paid
- tax: Sales tax amount (if shown separately)
- subtotal: Amount before tax (if shown)
- line_items: Extract individual items purchased (description, quantity, price)
- payment_method: Infer from payment info shown (last 4 digits of card = "credit")
- receipt_number: Transaction ID, receipt #, or invoice # if visible
- confidence: Your confidence in the extraction (0.0-1.0)

If any field cannot be determined, use null for optional fields.
If the image is not a receipt or is unreadable, set confidence to 0.0.

Return ONLY the JSON object, no markdown formatting or explanations."""

    def _parse_response(self, response_text: str) -> ReceiptExtraction:
        """
        Parse Claude's JSON response into ReceiptExtraction object.
        """
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            data = json.loads(response_text.strip())

            # Parse date
            date_str = data.get("date")
            try:
                date = datetime.fromisoformat(date_str) if date_str else datetime.now()
            except (ValueError, TypeError):
                logger.warning(f"Could not parse date: {date_str}, using today")
                date = datetime.now()

            return ReceiptExtraction(
                vendor=data.get("vendor", "Unknown Vendor"),
                date=date,
                total=float(data.get("total", 0)),
                tax=float(data["tax"]) if data.get("tax") else None,
                line_items=data.get("line_items", []),
                payment_method=data.get("payment_method"),
                receipt_number=data.get("receipt_number"),
                confidence=float(data.get("confidence", 0.8)),
                raw_response=response_text
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error parsing response: {e}")
            logger.error(f"Response was: {response_text}")

            # Return low-confidence extraction
            return ReceiptExtraction(
                vendor="Unknown Vendor",
                date=datetime.now(),
                total=0.0,
                tax=None,
                line_items=[],
                payment_method=None,
                receipt_number=None,
                confidence=0.0,
                raw_response=response_text
            )


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_ocr():
        """
        Test OCR with a sample receipt.
        Set ANTHROPIC_API_KEY environment variable before running.
        """

        # Check for API key
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("ERROR: Set ANTHROPIC_API_KEY environment variable")
            print("Example: export ANTHROPIC_API_KEY='sk-ant-...'")
            return

        ocr = ReceiptOCR()

        # Create a test receipt image path
        test_image = "test_receipt.jpg"

        if not os.path.exists(test_image):
            print(f"No test receipt found at {test_image}")
            print("\nTo test:")
            print("1. Take a photo of a receipt")
            print("2. Save it as 'test_receipt.jpg' in this directory")
            print("3. Run this script again")
            return

        print("Extracting data from receipt...")
        result = await ocr.extract_from_file(test_image)

        print("\n" + "=" * 60)
        print("RECEIPT EXTRACTION RESULTS")
        print("=" * 60)
        print(f"\nVendor: {result.vendor}")
        print(f"Date: {result.date.strftime('%Y-%m-%d')}")
        print(f"Total: ${result.total:.2f}")
        if result.tax:
            print(f"Tax: ${result.tax:.2f}")
        print(f"Payment Method: {result.payment_method or 'Not specified'}")
        print(f"Receipt #: {result.receipt_number or 'Not found'}")
        print(f"\nConfidence: {result.confidence * 100:.0f}%")

        if result.line_items:
            print(f"\nLine Items ({len(result.line_items)}):")
            for i, item in enumerate(result.line_items, 1):
                desc = item.get('description', 'Unknown')
                qty = item.get('quantity', 1)
                price = item.get('total', item.get('unit_price', 0))
                print(f"  {i}. {desc} × {qty} = ${price:.2f}")

        print("\n" + "=" * 60)

    asyncio.run(test_ocr())
