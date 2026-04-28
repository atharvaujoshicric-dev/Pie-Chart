import streamlit as st
import pytesseract
from PIL import Image, ImageOps
import pandas as pd
import re
import matplotlib.pyplot as plt
import io

# ... (keep your page config and title) ...

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    
    # IMPROVEMENT 1: Pre-process image for better OCR
    # Convert to Grayscale and increase contrast
    img_gray = ImageOps.grayscale(img)
    
    with st.spinner('Extracting data...'):
        # IMPROVEMENT 2: Use "Assume single column/block" configuration
        custom_config = r'--oem 3 --psm 6' 
        raw_text = pytesseract.image_to_string(img_gray, config=custom_config)
        
        lines = raw_text.split('\n')
        data = []
        
        for line in lines:
            # IMPROVEMENT 3: Flexible Regex
            # This looks for: Any Text + A Number + optional (Percentage)
            # It ignores "Total" lines automatically
            if "Total" in line:
                continue
                
            match = re.search(r'([a-zA-Z\s]+)\s+(\d+)', line)
            if match:
                reason = match.group(1).strip()
                count = int(match.group(2))
                
                # Filter out noise (only keep rows where reason isn't empty)
                if len(reason) > 3:
                    data.append({"Reason": reason, "Leads": count})

    if data:
        # ... (keep your DataFrame and Matplotlib code) ...
    else:
        st.error("Could not parse data.")
        st.info("The OCR saw the following text. If this looks messy, the image quality might be too low:")
        st.code(raw_text) # This helps you see exactly what the AI is seeing
