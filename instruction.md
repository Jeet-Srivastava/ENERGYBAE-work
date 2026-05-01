# 📋 Solar Load Calculator — Instructions

## What This Tool Does

This tool automates Energybae's electricity bill analysis workflow:

1. **Upload** a customer's electricity bill (JPEG, PNG, or PDF)
2. **AI extracts** key data automatically — consumer name, units consumed, sanctioned load, monthly history
3. **Excel is generated** — extracted data fills the standard analysis template with solar sizing formulas
4. **Download** the ready-to-use `.xlsx` file

**Time saved**: From 15–30 minutes → **under 30 seconds**.

---

## Tech Stack

- **Python** — entire project
- **Streamlit** — web UI
- **Groq Vision API** — AI-powered bill reading (Llama 4)
- **openpyxl** — Excel file generation

---

## Setup

### Prerequisites
- Python 3.10+
- Groq API key from [console.groq.com](https://console.groq.com)

### 1. Install

```bash
git clone https://github.com/Jeet-Srivastava/ENERGYBAE-work.git
cd ENERGYBAE-work

python3 -m venv .venv
source .venv/bin/activate       # macOS/Linux
# .venv\Scripts\activate        # Windows

pip install -r requirements.txt
```

### 2. Configure API Key

```bash
cp .env.example .env
```

Edit `.env` and add your key:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run

```bash
streamlit run app.py
```

Opens automatically at **http://localhost:8501**

---

## How to Use

1. Open the app in your browser
2. Upload an electricity bill (JPEG, PNG, or PDF)
3. Wait for AI extraction (~5–15 seconds)
4. Review the extracted data on screen
5. Click **Download Excel** or **Download PDF** to get the filled template
6. Open the file to see the auto-calculated solar sizing

---

## Configurable Settings (Sidebar)

| Setting | Default | Description |
|---------|---------|-------------|
| Solar Panel Wattage | 600W | Wattage of panels used for calculation |
| Fixed Charges | ₹130 | Monthly fixed charges for the connection |

---

## Supported Formats

| Format | Status |
|--------|--------|
| MSEDCL (Maharashtra) bills — JPEG/PNG | ✅ Supported |
| MSEDCL bills — PDF | ✅ Supported |
| Other state electricity boards | ⚠️ May work (AI is flexible) |

---

## Project Structure

```
electricity-bill/
├── app.py                    # Streamlit UI (main entry point)
├── extractor.py              # Grok Vision API extraction
├── excel_generator.py        # Excel template filler
├── Data_provided/            # Sample bills + Excel template
├── requirements.txt          # Python dependencies
├── .env.example              # API key template
└── instruction.md            # This file
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not found" | Ensure `.env` has `GROK_API_KEY` set |
| Poor extraction | Use a clear, well-lit bill image |
| Excel formulas not computing | Open in Excel or Google Sheets (not preview apps) |
