# ☀️ Solar Load Calculator — Energybae

Automates the process of analysing a customer's electricity bill and calculating the recommended solar system size. Upload a bill image or PDF → AI extracts the data → get a filled Excel file with solar sizing.

**Built for [Energybae](https://github.com/Jeet-Srivastava/ENERGYBAE-work)** — helping businesses and homes switch to solar power.

---

## How It Works

```
Upload Bill (JPEG/PNG/PDF)
        ↓
Grok Vision AI reads the bill
        ↓
Extracts: consumer info, monthly units, bill amounts
        ↓
Fills the Excel template with formulas
        ↓
Download ready-to-use .xlsx file
```

### What the AI Extracts
- Consumer name and number
- Sanctioned load (kW) and connection type
- Monthly consumption history (units from the bar chart on the bill)
- Current month's units and bill amount

### What the Excel Calculates
- Average monthly consumption
- Recommended solar system size (kW)
- Number of solar panels needed
- Total solar capacity

**Formula used:** `kW = (Avg Units × 12 × 1.1) / 1400`

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| UI | Streamlit |
| AI Extraction | Grok Vision API (xAI) |
| Excel Generation | openpyxl |
| Language | Python |

---

## Run Locally

### Prerequisites
- Python 3.10+
- Grok API key — get one free at [console.x.ai](https://console.x.ai)

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/Jeet-Srivastava/ENERGYBAE-work.git
cd ENERGYBAE-work

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate       # macOS / Linux
# .venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your API key
cp .env.example .env
# Open .env and replace 'your_grok_api_key_here' with your actual key

# 5. Run the app
streamlit run app.py
```

> Note: For deployed Streamlit apps, `.env` is local-only. Configure `GROQ_API_KEY` or `GROK_API_KEY` in your deployment environment variables / Streamlit secrets instead. 

The app opens at **http://localhost:8501**

---

## Usage

1. Open the app in your browser
2. Upload an electricity bill (JPEG, PNG, or PDF)
3. Click **Extract & Generate Excel**
4. Review the extracted data on screen
5. Click **Download Excel File**
6. Open in Excel or Google Sheets — solar calculations are ready

### Sidebar Settings
- **Solar Panel Wattage** — default 600W, adjust based on panel model
- **Fixed Charges** — default ₹130, adjust per connection type

---

## Project Structure

```
├── app.py                 # Streamlit UI — main entry point
├── extractor.py           # Grok Vision API — reads bill images
├── excel_generator.py     # Fills Excel template, preserves formulas
├── Data_provided/         # Sample bills + Excel template
│   ├── *.xlsx             # Energybae analysis template
│   └── *.jpeg             # Sample MSEDCL bills
├── requirements.txt       # Python dependencies
├── .env.example           # API key template
├── .gitignore
├── instruction.md         # Detailed setup & usage guide
└── README.md              # This file
```

---

## Supported Bill Formats

| Format | Status |
|--------|--------|
| MSEDCL (Maharashtra) — Image | ✅ Supported |
| MSEDCL (Maharashtra) — PDF | ✅ Supported |
| Other state electricity boards | ⚠️ May work (AI-based, flexible) |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROK_API_KEY` | Yes | Your xAI Grok API key (also supports `GROQ_API_KEY` for compatibility) |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `GROK_API_KEY not found` | Make sure `.env` file exists with your key |
| Poor extraction accuracy | Use a clear, well-lit bill image |
| Excel formulas show as text | Open in Microsoft Excel or Google Sheets |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside your venv |
