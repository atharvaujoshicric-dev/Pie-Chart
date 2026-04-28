import streamlit as st
import pytesseract
from PIL import Image, ImageOps
import pandas as pd
import re
import matplotlib.pyplot as plt
import io

# Setup Streamlit page
st.set_page_config(page_title="2D Pie Chart Generator", layout="wide")

st.title("📊 Lead Pipeline Image Generator")
st.write("Upload your screenshot to generate a clean 2D Pie chart.")

uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # 1. Process Image
    img = Image.open(uploaded_file)
    # Convert to grayscale to help OCR read text more clearly
    img_gray = ImageOps.grayscale(img)
    
    col_in, col_out = st.columns(2)
    
    with col_in:
        st.subheader("1. Input Screenshot")
        st.image(img, use_container_width=True)
    
    # 2. Extract Data
    with st.spinner('Reading table data...'):
        # PSM 6 assumes a single uniform block of text
        custom_config = r'--oem 3 --psm 6'
        raw_text = pytesseract.image_to_string(img_gray, config=custom_config)
        
        lines = raw_text.split('\n')
        data = []
        
        for line in lines:
            # Skip the total line
            if "Total" in line or not line.strip():
                continue
            
            # Regex: Finds Text, then a Number, then a Percentage in brackets
            # Example: Location Mismatch 1 (16.67%)
            match = re.search(r'([a-zA-Z\s]+)\s+(\d+)\s*\(', line)
            
            if match:
                reason = match.group(1).strip()
                count = int(match.group(2))
                if reason:
                    data.append({"Reason": reason, "Leads": count})

    # 3. Handle Results
    if len(data) > 0:
        df = pd.DataFrame(data)
        
        with col_out:
            st.subheader("2. Generated 2D Chart")
            
            # Create Plot
            fig, ax = plt.subplots(figsize=(8, 8))
            colors = plt.cm.Paired.colors # High contrast 2D colors
            
            wedges, texts, autotexts = ax.pie(
                df['Leads'], 
                labels=df['Reason'], 
                autopct='%1.1f%%',
                startangle=140,
                colors=colors,
                wedgeprops={'edgecolor': 'white', 'linewidth': 2}
            )
            
            # Styling text
            plt.setp(autotexts, size=10, weight="bold", color="white")
            plt.setp(texts, size=11)
            ax.set_title("Lead Distribution", size=16, pad=20)
            
            # Save to buffer
            buf = io.BytesIO()
            plt.savefig(buf, format="png", bbox_inches='tight', dpi=150)
            st.image(buf, use_container_width=True)
            
            # Download Button
            st.download_button(
                label="Download Pie Chart Image",
                data=buf.getvalue(),
                file_name="lead_pie_chart.png",
                mime="image/png"
            )
    else:
        st.error("Could not find data in the image.")
        st.warning("Ensure the image is a clear screenshot of the table.")
        with st.expander("Show what the AI saw (Debug)"):
            st.code(raw_text)

else:
    st.info("Please upload an image to begin.")
