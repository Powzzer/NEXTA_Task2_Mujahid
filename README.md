# AI Receipt Reader & Market Auditor 

This app reads receipt images, extracts the items, and checks if you were overcharged compared to average market prices.

---

## How it Works

Image Upload
     ->
Gemini 3.5 Flash Model
     ->
Structured JSON Data
     ->
Automated Decision Block
     ->
Results Table

---

## How to Run This Project

1. **Install libraries:**
   pip install google-genai streamlit pillow pydantic

2. **Run the app:**
   python -m streamlit run app.py

3. **Use the app:** Open http://localhost:8501 in your browser, enter your Gemini API Key in the sidebar, upload your receipt, and click "Analyze Price".

---

## Example Output

* **Image Used:** receipt.png (Receipt sample)
* **AI Model:** gemini-3.5-flash

### Prompt Used:
    Perform a highly critical, currency-aware market audit on this receipt image. 
    Save '{user_currency}' into the 'currency_code' data field.
    Evaluate all numbers and internal price checks against the {user_currency} market benchmarks.
    
    Enforce these strict rules for grading 'confidence_level':
    - 'High': Clear full product name.
    - 'Medium': Shorthand codes or missing vowels.
    - 'Low': Blurry or unidentifiable.
    
    Enforce these strict rules for 'online_market_average' and 'price_analysis':
    - If unknown or low confidence, set 'online_market_average' to null and 'price_analysis' to 'Unable to Verify'.
    - 'Overpriced': > 15% higher than local average.
    - 'Great Deal': > 15% lower than local average.
    - 'Fair Market Price': within a 15% variance.

### Generated Table Result (Jarir Bookstore):
| Receipt Text | Clean Name | Your Cost | Online Avg | Comparison | Confidence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| XBOX CONTROLLER WLC BLUE... | Xbox Wireless Controller Blue | SR 259.00 | SR 249.00 | Fair Market Price | High |
| MOUSE BLUETOOTH BLACK... | Microsoft Bluetooth Mouse Black | SR 89.00 | SR 85.00 | Fair Market Price | High |
| ADAPTER BLUETOOTH 5.0... | TP-Link UB500 Bluetooth Adapter | SR 39.00 | SR 39.00 | Fair Market Price | High |

**System Action:** `ROUTE APPROVED: All rows successfully validated against standard budget thresholds.`

---

## 🔧 AI Help vs. My Work

* **What AI Helped With:** Setting up the basic code for the Streamlit layout and connecting to the new google-genai SDK.
* **What I Fixed Myself:** Changing the table code to use strict object dot notation (item.price_analysis instead of item["price_analysis"]) to prevent the app from crashing. I also built the dynamic currency symbol switcher.
* **What I Learned:** How a local computer acts as a web server (localhost), and how Pydantic makes sure unstructured images always turn into clean tables.
