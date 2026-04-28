import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="Lead Pipeline Visualizer", layout="wide")

st.title("📊 Lead Pipeline Pie Chart Generator")
st.write("Upload a screenshot of your lead table to generate an interactive chart.")

uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Display the uploaded image
    img = Image.open(uploaded_file)
    st.image(img, caption='Uploaded Image', use_column_width=True)
    
    with st.spinner('Extracting data from image...'):
        # Perform OCR
        raw_text = pytesseract.image_to_string(img)
        
        # Logic to parse the specific format in your screenshot
        # We look for lines that contain a reason and a number/percentage
        lines = raw_text.split('\n')
        data = []
        
        for line in lines:
            # Matches text followed by a number and a percentage like (16.67%)
            match = re.search(r'^(.*?)\s+(\d+)\s*\((.*?)\%\)', line)
            if match:
                reason = match.group(1).strip()
                count = int(match.group(2))
                data.append({"Reason": reason, "Leads": count})

        if data:
            df = pd.DataFrame(data)
            
            # Create two columns for layout
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("Extracted Data")
                st.dataframe(df, use_container_width=True)
            
            with col2:
                st.subheader("Pie Chart Distribution")
                fig = px.pie(
                    df, 
                    values='Leads', 
                    names='Reason', 
                    hole=0.3,
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                fig.update_traces(textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Could not parse data. Please ensure the image is clear and follows the table format.")
            st.info("Debug: Raw text detected below:")
            st.code(raw_text)
