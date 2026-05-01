# Energybae Solar Load Calculator: Technical Overview & Video Script

## Part 1: Technical Architecture & Explanation

The **Solar Load Calculator** is a Python-based automation pipeline designed to replace a manual 15-to-30-minute data entry task with a fully automated process that takes less than 30 seconds.

### 1. User Interface (Streamlit)
- **Framework:** `streamlit`
- **Functionality:** Provides a lightweight, responsive web interface. It handles file uploads (JPEG, PNG, PDF) and gives users real-time feedback with loading spinners. It also features a sidebar for configurable global variables (Solar Panel Wattage and Fixed Charges) which influence the final Excel calculations.

### 2. Document Pre-Processing
- **Framework:** `PyMuPDF` (fitz)
- **Functionality:** When a user uploads a PDF instead of an image, the system cannot send it directly to the vision model. The `extract_from_pdf` function uses PyMuPDF to read the first page of the PDF and render it into a high-resolution PNG image (2x matrix scale for optimal OCR quality) before passing it to the AI.

### 3. AI Data Extraction (Groq API)
- **Model:** `meta-llama/llama-4-scout-17b-16e-instruct`
- **Framework:** `openai` (Python SDK) configured for Groq's endpoint.
- **Functionality:** The rendered bill image is encoded into a Base64 string and sent to Groq's high-speed inference engine. We use a highly structured system prompt that commands the model to read the specific billing tables and the monthly consumption bar charts. The AI is strictly prompted to return only valid JSON containing exact keys (e.g., `consumer_name`, `monthly_data`).

### 4. Excel Generation & Formula Preservation
- **Framework:** `openpyxl`
- **Functionality:** Standard libraries like `pandas` would overwrite the complex formulas present in Energybae's proprietary Excel template. Instead, `openpyxl` is used to load the existing template (`Copy of Pranay HOME E-Bill Analysis.xlsx`). The script specifically targets and overwrites only the input cells (Consumer details and Monthly Unit rows), leaving the embedded formulas intact. This ensures the Excel file automatically calculates the optimal solar panel sizing and ROI immediately upon opening.

### 5. PDF Conversion
- **Framework:** `subprocess` running LibreOffice (`soffice`) headless.
- **Functionality:** Once the Excel file is generated, the app runs a background OS command utilizing LibreOffice in `--headless` mode. This perfectly renders the Excel workbook—preserving all visual formatting, colors, and calculated values—into a polished, client-ready PDF document.

---

## Part 2: Video Presentation Script (4–5 Minutes)

**[0:00 - 0:45] Introduction & The Problem**
*(Visual: Presenter looking at the camera, transitioning to a screen recording of someone manually typing data from a bill into an Excel sheet)*

**Presenter:** 
"Hello everyone! Today, I want to walk you through a project we've built for Energybae. At Energybae, our goal is to help businesses and homeowners transition to solar energy. 

But our sales process had a massive bottleneck. Every time a potential customer sent us an electricity bill, our team had to manually open it, read through the complex tables, interpret the bar charts for monthly consumption, and type all that data into an Excel spreadsheet. This spreadsheet then calculates the solar system size they need. 

This manual data entry was taking 15 to 30 minutes per customer. Multiply that by dozens of customers a week, and it's a massive drain on resources. We needed a way to automate this. And that's exactly what we did."

**[0:45 - 1:30] The Solution & Demo**
*(Visual: Screen recording showing the Streamlit UI. The user drags and drops a bill into the app, clicks extract, and the data pops up.)*

**Presenter:**
"Welcome to the Automated Solar Load Calculator. We built this entirely in Python, utilizing Streamlit for a clean, intuitive web interface.

Let's do a live run. I'm taking a standard customer electricity bill—this can be an image or a PDF—and dropping it right here into the app. On the left, we can tweak our parameters, like panel wattage. 

I hit 'Extract'. Right now, the magic is happening in the background. In less than ten seconds, the system has read the bill, pulled the consumer's name, their sanctioned load, and perfectly extracted the month-by-month consumption data from the bar chart. 

Instead of 20 minutes, this took seconds."

**[1:30 - 2:45] Technical Deep Dive: The AI Extraction Engine**
*(Visual: Cut to an architecture diagram or a code snippet of `extractor.py` highlighting the Groq API call and the system prompt)*

**Presenter:**
"So, how does this actually work under the hood? 

The core of our extraction engine is powered by Groq's high-speed inference platform. Specifically, we're using Meta's brand-new multimodal model: **Llama 4 Scout**. 

When a bill is uploaded, if it's a PDF, we use the `PyMuPDF` library to instantly render it into a high-resolution image. We encode that image into Base64 and send it to the Groq API. 

But the real secret sauce is our prompt engineering. We don't just ask the AI to 'read the text'. We explicitly instruct it to locate the historical consumption bar chart, estimate the Y-axis values for each month, and format the entire output as a strict JSON object. Because we use Groq, this heavy multimodal processing happens almost instantaneously, giving us structured, predictable data every single time."

**[2:45 - 3:45] Technical Deep Dive: Excel & Formula Preservation**
*(Visual: Show `excel_generator.py` code, then show the Excel template opening up with formulas auto-calculating)*

**Presenter:**
"Once we have that JSON data, we need to put it into Energybae's proprietary Excel template. 

This was a unique technical challenge. If we just dumped the data into a CSV or used standard dataframes, we would destroy all the complex formulas that Energybae uses to calculate Solar Capacity, ROI, and panel counts.

To solve this, we used the `openpyxl` library. Our script opens the existing Excel template, specifically navigates to the exact cells designated for user input, and injects our extracted data. It leaves the rest of the sheet entirely untouched. 

This means when the output file is generated, the embedded formulas instantly kick in, utilizing the AI-extracted data to automatically calculate the final solar system size."

**[3:45 - 4:30] PDF Generation & Conclusion**
*(Visual: Showing the UI download buttons, downloading the PDF, and opening it on screen to show the pristine formatting)*

**Presenter:**
"Finally, we wanted to make this completely frictionless for the sales team. Not only does the app generate the Excel file, but it uses a background subprocess running LibreOffice in headless mode to convert that calculated Excel file directly into a beautifully formatted, client-ready PDF. 

The user is presented with two simple download buttons: one for the raw Excel data, and one for the PDF report.

What used to take 30 minutes of tedious manual labor now takes 10 seconds of automated processing. It eliminates human error, speeds up the sales cycle, and allows the Energybae team to focus on what they do best—bringing clean energy to the world.

Thank you for watching!"
