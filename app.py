import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import re
import matplotlib.pyplot as plt
import io

# Setup Streamlit page
st.set_page_config(page_title="2D Pie Chart Generator", layout="wide")

st.title("📊 Lead Pipeline Image Generator")
st.write("Upload a screenshot. This app generates a static 2D Pie chart image from the data.")

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # 1. Input Image Display
    img = Image.open(uploaded_file)
    
    col_in, col_out = st.columns(2)
    
    with col_in:
        st.subheader("1. Input Screenshot")
        st.image(img, use_column_width=True)
    
    # 2. OCR and Data Parsing
    with st.spinner('Extracting data from image...'):
        # Convert image to string
        raw_text = pytesseract.image_to_string(img)
        
        # Regex parsing specific to the user's table format
        lines = raw_text.split('\n')
        data = []
        
        for line in lines:
            # Matches: Reason, Number, (Percentage%)
            match = re.search(r'^(.*?)\s+(\d+)\s*\((.*?)\%\)', line)
            if match:
                reason = match.group(1).strip()
                count = int(match.group(2))
                data.append({"Reason": reason, "Leads": count})

    if data:
        # 3. Create DataFrame
        df = pd.DataFrame(data)
        
        # 4. Generate the 2D Pie Chart Image using Matplotlib
        with st.spinner('Generating 2D image...'):
            fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
            
            # Matplotlib Pie settings for a clean 2D look
            wedges, texts, autotexts = ax.pie(
                df['Leads'], 
                labels=df['Reason'], 
                autopct='%1.1f%%',
                startangle=140,
                colors=plt.cm.Pastel1.colors, # Use a nice flat color palette
                textprops=dict(color="black"),
                pctdistance=0.85, # Move percentages slightly inwards
                explode=[0.02] * len(df) # Add tiny gaps between slices for clarity
            )
            
            # Clean up the appearance
            plt.setp(texts, size=10, weight="bold")
            plt.setp(autotexts, size=9, weight="bold", color="white")
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.tight_layout()
            
            # 5. Save the Matplotlib figure to a buffer (rendering it as an image)
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=150)
            buf.seek(0)
            generated_image = Image.open(buf)
            
            # Clean up matplotlib figure from memory
            plt.close(fig)

        # 6. Display the Output Image
        with col_out:
            st.subheader("2. Generated 2D Chart Image")
            st.image(generated_image, use_column_width=True, caption="Generated Static PNG Image")
            
            # Optional: Add a download button for the generated image
            st.download_button(
                label="Download Chart Image",
                data=buf,
                file_name="pipeline_chart.png",
                mime="image/png"
            )

    else:
        st.error("Could not parse data. Please ensure the image follows the exact table format.")
        st.info("Debug: Raw text detected:")
        st.code(raw_text)
