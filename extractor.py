"""
extractor.py — AI-powered electricity bill data extraction using Grok Vision API.

Uses xAI's Grok Vision model (OpenAI-compatible SDK) to read electricity bill
images and extract structured data for solar load calculation.
"""

import os
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Groq API client (lazily initialized)
_client = None


def _get_client() -> OpenAI:
    """Get or create the Groq API client."""
    global _client
    if _client is None:
        # Check both GROK and GROQ env vars since the user confused them
        api_key = os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY")
        if not api_key:
            raise ValueError(
                "API key not found. Please set GROQ_API_KEY in your .env file.\n"
                "Get your key at https://console.groq.com"
            )
        _client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
    return _client

EXTRACTION_PROMPT = """You are an expert at reading Indian electricity bills. 
Analyze this electricity bill image and extract the following data in JSON format.

IMPORTANT RULES:
- Extract ALL monthly consumption data visible in the bar chart on the bill
- The bar chart shows monthly units consumed — read each bar's value carefully
- Months are labeled on the Y-axis (or X-axis), values on the opposite axis
- If you cannot read a value clearly, make your best estimate from the bar height
- Consumer number should be a string (preserve leading zeros)
- Sanctioned load should include the unit (e.g., "3.30KW")
- For bill amount, extract the total payable amount from the current bill

Return ONLY valid JSON in this exact format (no markdown, no explanation):
{
    "consumer_name": "Full name as shown on bill",
    "consumer_no": "Consumer number as string",
    "sanctioned_load": "Load with unit e.g. 3.30KW",
    "connection_type": "e.g. 90/LT I Res 1-Phase",
    "monthly_data": [
        {"month": "2025-02", "units": 99},
        {"month": "2025-03", "units": 151}
    ],
    "current_bill_amount": 1460.00,
    "current_month": "2026-01",
    "current_units": 25
}

Notes:
- monthly_data should contain ALL months visible in the bar chart, ordered chronologically
- current_units is the units consumed shown in the main reading table (not from the chart)
- current_bill_amount is the total bill amount for the current month
- The bill may be in Hindi/Marathi — translate field names to English
"""


def encode_image_to_base64(image_path: str) -> str:
    """Read an image file and return its base64 encoding."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_image_media_type(image_path: str) -> str:
    """Determine the media type from file extension."""
    ext = os.path.splitext(image_path)[1].lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return media_types.get(ext, "image/jpeg")


def extract_bill_data(image_path: str) -> dict:
    """
    Extract electricity bill data from an image using Groq Vision API.
    
    Args:
        image_path: Path to the bill image file.
        
    Returns:
        Dictionary with extracted bill data.
        
    Raises:
        ValueError: If extraction fails or returns invalid data.
    """
    # Encode image
    base64_image = encode_image_to_base64(image_path)
    media_type = get_image_media_type(image_path)

    # Call Groq Vision API
    response = _get_client().chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": EXTRACTION_PROMPT,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        temperature=0.1,  # Low temperature for accurate extraction
    )

    # Parse response
    raw_text = response.choices[0].message.content.strip()

    # Clean up — remove markdown code fences if present
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]  # Remove first line
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse AI response as JSON: {e}\nRaw response: {raw_text}")

    # Validate required fields
    required_fields = ["consumer_name", "consumer_no", "sanctioned_load", "monthly_data"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    if not isinstance(data["monthly_data"], list) or len(data["monthly_data"]) == 0:
        raise ValueError("monthly_data must be a non-empty list")

    return data


def extract_from_pdf(pdf_path: str) -> dict:
    """
    Extract bill data from a PDF file.
    Converts the first page to an image, then runs extraction.
    
    Args:
        pdf_path: Path to the PDF file.
        
    Returns:
        Dictionary with extracted bill data.
    """
    import fitz  # PyMuPDF

    doc = fitz.open(pdf_path)
    page = doc[0]  # First page

    # Render page to image at 2x resolution for better OCR
    mat = fitz.Matrix(2, 2)
    pix = page.get_pixmap(matrix=mat)

    # Save as temporary PNG
    temp_image_path = pdf_path + "_page1.png"
    pix.save(temp_image_path)
    doc.close()

    try:
        result = extract_bill_data(temp_image_path)
    finally:
        # Clean up temp file
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)

    return result
