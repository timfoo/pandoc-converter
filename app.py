import streamlit as st
import magic
import os
import subprocess
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Pandoc Converter",
    page_icon="📄",
    layout="centered"
)

# Title and description
st.title("Pandoc Converter")
st.markdown("Convert your documents between different formats using Pandoc")

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=None)

if uploaded_file is not None:
    # Save uploaded file temporarily
    temp_path = Path("temp") / uploaded_file.name
    temp_path.parent.mkdir(exist_ok=True)
    
    # Write uploaded file
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Detect file type
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(str(temp_path))
    st.write(f"Detected file type: {file_type}")
    
    # TODO: Add pandoc format detection and conversion options
    # TODO: Add conversion functionality
    
    # Cleanup
    os.remove(temp_path)
    if temp_path.parent.exists() and not any(temp_path.parent.iterdir()):
        temp_path.parent.rmdir()