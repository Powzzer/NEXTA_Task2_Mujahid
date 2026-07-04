import os
import json
from google import genai
from google.genai import types
from PIL import Image
from pydantic import BaseModel
from typing import List, Literal, Optional
# =====================================================================
# STEP 2: DEFINE STRUCTURED OUTPUT (The Data Schema)
# =====================================================================
class ReceiptItem(BaseModel):
    raw_receipt_text: str
    product_name: str              
    quantity: int
    total_cost: float
    individual_cost: float        
    online_market_average: Optional[float]  
    price_analysis: Literal["Overpriced", "Fair Market Price", "Great Deal", "Unable to Verify"]
    confidence_level: Literal["High", "Medium", "Low"]
class LiveAuditWorkflowSchema(BaseModel):
    image_type: str
    store_name: str
    currency_code: str # Confirms the currency choice injected from the user selection
    items: List[ReceiptItem]
    grand_total: float
# =====================================================================
# STEP 1 & 3: SETUP ENVIRONMENT & INTERACT WITH VLM API WITH INJECTED CONTEXT
# =====================================================================
def run_live_market_audit(image_path: str, user_currency: str):
    client = genai.Client()
    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"Error: The image file '{image_path}' was not found.")
        return None
    # We dynamically pass the user_currency variable right into the VLM's core instructions
    prompt = f"""
    Perform a highly critical, currency-aware market audit on this receipt image.
    CRITICAL USER OVERRIDE: The user has specified that the currency for this receipt is {user_currency}.
    Save '{user_currency}' into the 'currency_code' data field.
    Evaluate all numbers and internal price checks against the {user_currency} market benchmarks.
    - Example: If currency is SAR, an Xbox Controller typically averages 200-250 SAR. Evaluate 249 as a 'Fair Market Price'.
    - Example: If currency is USD, an Xbox Controller typically averages $50-$60 USD. Evaluate 249 as 'Overpriced'.
    Match your analysis strictly to the {user_currency} economic reality.
    Enforce these strict rules for grading 'confidence_level':
    - 'High': The text clearly displays the full, standard un-abbreviated brand or product name.
    - 'Medium': The product name uses shorthand codes or missing vowels where you must deduce context.
    - 'Low': Text is blurry, chopped off, or completely unidentifiable.
    Enforce these strict rules for 'online_market_average' and 'price_analysis':
    - If you DO NOT have confident historical reference knowledge for a product's average price in {user_currency}, or if the confidence_level is 'Low', you MUST set 'online_market_average' to null and set 'price_analysis' to 'Unable to Verify'.
    - If baseline is known, evaluate:
      - 'Overpriced': Your individual_cost is > 15% higher than local market average.
      - 'Great Deal': Your individual_cost is > 15% lower than local market average.
      - 'Fair Market Price': Value falls within a standard 15% local market variance.
    """
    print(f"Sending image to Gemini 3.5 Flash for critical verification in {user_currency}...")
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=[img, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LiveAuditWorkflowSchema,
        ),
    )
    return response.text
# =====================================================================
# STEP 4 & 5: DECISION / ACTION & FINAL RESULT
# =====================================================================
def process_audit_results(json_string: str):
    print("Parsing structured data and rendering final evaluation matrix...\n")
    data = json.loads(json_string)
    currency = data.get("currency_code", "USD")
    symbol = "SR " if currency == "SAR" else "$ " if currency == "USD" else f"{currency} "

    print(f"STORE NAME: {data['store_name'].upper()}")
    print(f"CURRENCY APPLIED: {currency}")
    print("-" * 120)
    print(f"{'Product (Raw Text)':<24} | {'Clean Name':<16} | {f'Cost ({currency})':<14} | {f'Online Avg ({currency})':<16} | {'Comparison':<24} | {'Comparison Confidence'}")
    print("-" * 120)

    has_low_confidence_items = False
    has_unverified_items = False

    for item in data["items"]:
        display_raw = f"{item['raw_receipt_text'][:22]}"
        display_clean = f"{item['product_name'][:15]}"
        your_cost = f"{symbol}{item['individual_cost']:.2f}"

        if item["online_market_average"] is None:
            web_avg = "N/A"
            has_unverified_items = True

        else:

            web_avg = f"{symbol}{item['online_market_average']:.2f}"

        analysis = item["price_analysis"]
        confidence = item["confidence_level"]

        if confidence.lower() == "low":

            has_low_confidence_items = True

        print(f"{display_raw:<24} | {display_clean:<16} | {your_cost:<14} | {web_avg:<16} | {analysis:<24} | {confidence}")

    print("-" * 120)
    print(f"Receipt Grand Total: {symbol}{data['grand_total']:.2f}\n")
    print("WORKFLOW DECISION SYSTEM ENGINE:")

    if has_low_confidence_items:
        print("ROUTE REJECTED: Unreadable line elements. Routing to manual review.")
    elif has_unverified_items:
        print(f"ROUTE HOLD: Pipeline successful but contains raw values outside verified {currency} parameters.")
    else:
        print(f"ROUTE APPROVED: All localized line item fields validated against standard {currency} budget thresholds.")

# =====================================================================
# SYSTEM INITIALIZATION & INTERACTIVE USER MENU
# =====================================================================

if __name__ == "__main__":
    TARGET_IMAGE_FILE = "receipt.jpeg"

    # 1. INTERACTIVE FALLBACK INTERFACE: Prompt the user for input

    print("Select the receipt currency baseline:")
    print("1 - SAR (Saudi Riyals)")
    print("2 - USD (US Dollars)")

    choice = input("Enter selection (1 or 2): ").strip()

    if choice == "1":
        selected_currency = "SAR"
    elif choice == "2":
        selected_currency = "USD"
    else:
        print("Invalid selection. Defaulting to USD configuration.")
        selected_currency = "USD"
    print() # Formatting spacer
    # Run the dynamic pipeline orchestrator
    structured_json_payload = run_live_market_audit(TARGET_IMAGE_FILE, selected_currency)
    if structured_json_payload:

        process_audit_results(structured_json_payload) 