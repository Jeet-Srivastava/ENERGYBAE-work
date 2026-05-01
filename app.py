"""
app.py — Solar Load Calculator (Streamlit UI)

Upload an electricity bill → AI extracts data → Download filled Excel template.
"""

import os
import subprocess
import streamlit as st
from datetime import datetime

from extractor import extract_bill_data, extract_from_pdf
from excel_generator import generate_excel

# --- Page Config ---
st.set_page_config(
    page_title="Solar Load Calculator — Energybae",
    page_icon="☀️",
    layout="centered",
)

# --- App Header ---
st.title("☀️ Solar Load Calculator")
st.caption("Energybae — Electricity Bill to Solar Sizing in Seconds")
st.divider()

# --- Sidebar Settings ---
with st.sidebar:
    st.header("⚙️ Settings")
    solar_panel_wattage = st.number_input(
        "Solar Panel Wattage (W)",
        min_value=100,
        max_value=1000,
        value=600,
        step=50,
        help="Wattage of each solar panel used for calculation",
    )
    fixed_charges = st.number_input(
        "Fixed Charges (₹)",
        min_value=0.0,
        max_value=1000.0,
        value=130.0,
        step=10.0,
        help="Monthly fixed charges for the electricity connection",
    )
    st.divider()
    st.markdown("**How it works:**")
    st.markdown(
        """
        1. Upload a bill image or PDF
        2. AI reads and extracts data
        3. Data fills the Excel template
        4. Download the result
        """
    )

# --- File Upload ---
st.subheader("📄 Upload Electricity Bill")
uploaded_file = st.file_uploader(
    "Choose a bill image or PDF",
    type=["jpg", "jpeg", "png", "pdf"],
    help="Supported: JPEG, PNG, PDF — works best with MSEDCL (Maharashtra) bills",
)

if uploaded_file is not None:
    # Show uploaded file preview
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    is_pdf = file_ext == ".pdf"

    if not is_pdf:
        st.image(uploaded_file, caption="Uploaded Bill", use_container_width=True)

    # Save uploaded file temporarily
    os.makedirs("uploads", exist_ok=True)
    temp_path = os.path.join("uploads", uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # --- Extract Data ---
    if st.button("🔍 Extract & Generate Excel", type="primary", use_container_width=True):
        with st.spinner("🤖 AI is reading the bill... please wait"):
            try:
                # Run extraction
                if is_pdf:
                    bill_data = extract_from_pdf(temp_path)
                else:
                    bill_data = extract_bill_data(temp_path)

                st.success("✅ Data extracted successfully!")

                # --- Display Extracted Data ---
                st.subheader("📊 Extracted Data")

                # Consumer info
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Consumer Name", bill_data.get("consumer_name", "N/A"))
                    st.metric("Sanctioned Load", bill_data.get("sanctioned_load", "N/A"))
                with col2:
                    st.metric("Consumer No", bill_data.get("consumer_no", "N/A"))
                    st.metric("Connection Type", bill_data.get("connection_type", "N/A"))

                # Current bill
                if bill_data.get("current_units") or bill_data.get("current_bill_amount"):
                    st.divider()
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Current Month", bill_data.get("current_month", "N/A"))
                    with col2:
                        st.metric("Units Consumed", bill_data.get("current_units", "N/A"))
                    with col3:
                        amount = bill_data.get("current_bill_amount")
                        st.metric("Bill Amount", f"₹{amount}" if amount else "N/A")

                # Monthly data table
                monthly = bill_data.get("monthly_data", [])
                if monthly:
                    st.divider()
                    st.markdown("**Monthly Consumption History**")
                    table_data = []
                    for entry in monthly:
                        table_data.append({
                            "Month": entry.get("month", ""),
                            "Units": entry.get("units", 0),
                        })
                    st.dataframe(table_data, use_container_width=True, hide_index=True)

                # --- Generate Excel ---
                st.divider()
                os.makedirs("output", exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                consumer_name = bill_data.get("consumer_name", "customer").replace(" ", "_")[:20]
                output_filename = f"{consumer_name}_Solar_Analysis_{timestamp}.xlsx"
                output_path = os.path.join("output", output_filename)

                generate_excel(
                    bill_data=bill_data,
                    output_path=output_path,
                    solar_panel_wattage=solar_panel_wattage,
                    fixed_charges=fixed_charges,
                )

                # --- Convert to PDF ---
                pdf_path = None
                with st.spinner("📄 Converting to PDF..."):
                    try:
                        libreoffice = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
                        if not os.path.exists(libreoffice):
                            libreoffice = "libreoffice"
                        
                        subprocess.run(
                            [libreoffice, "--headless", "--convert-to", "pdf", output_path, "--outdir", "output"],
                            check=True, capture_output=True
                        )
                        expected_pdf = os.path.splitext(output_path)[0] + ".pdf"
                        if os.path.exists(expected_pdf):
                            pdf_path = expected_pdf
                    except Exception as e:
                        st.warning("⚠️ Could not generate PDF. Only Excel will be available.")

                # --- Download Buttons ---
                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="📥 Download Excel (.xlsx)",
                            data=f.read(),
                            file_name=output_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                        )
                
                with col_dl2:
                    if pdf_path:
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                label="📄 Download PDF",
                                data=f.read(),
                                file_name=os.path.basename(pdf_path),
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True,
                            )

                st.info("💡 Open the downloaded file in Excel or Google Sheets to see the solar sizing calculations.")

            except Exception as e:
                st.error(f"❌ Extraction failed: {str(e)}")
                st.markdown("**Possible fixes:**")
                st.markdown("- Check that your `GROQ_API_KEY` is set in the `.env` file")
                st.markdown("- Ensure the bill image is clear and readable")
                st.markdown("- Try with a different bill image")

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
else:
    # Empty state
    st.info("👆 Upload an electricity bill to get started")
