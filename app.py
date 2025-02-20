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

# Define supported Pandoc formats
PANDOC_FORMATS = {
    'text/markdown': {'ext': '.md', 'pandoc_format': 'markdown', 'output_formats': ['html', 'pdf', 'docx', 'odt']},
    'text/html': {'ext': '.html', 'pandoc_format': 'html', 'output_formats': ['md', 'pdf', 'docx', 'odt']},
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': {'ext': '.docx', 'pandoc_format': 'docx', 'output_formats': ['md', 'html', 'pdf', 'odt']},
    'application/vnd.oasis.opendocument.text': {'ext': '.odt', 'pandoc_format': 'odt', 'output_formats': ['md', 'html', 'pdf', 'docx']}
}

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
    
    # Check if file type is supported
    if file_type in PANDOC_FORMATS:
        # Get available output formats
        output_formats = PANDOC_FORMATS[file_type]['output_formats']
        selected_format = st.selectbox("Select output format", output_formats)
        
        if st.button("Convert"):
            try:
                # Prepare output path
                output_path = temp_path.parent / f"converted.{selected_format}"
                
                # Run pandoc conversion
                input_format = PANDOC_FORMATS[file_type]['pandoc_format']
                cmd = ['pandoc', str(temp_path), '-f', input_format, '-t', selected_format, '-o', str(output_path)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    # Read the converted file
                    with open(output_path, 'rb') as f:
                        converted_data = f.read()
                    
                    # Create download button
                    st.download_button(
                        label="Download converted file",
                        data=converted_data,
                        file_name=f"converted.{selected_format}",
                        mime=f"application/{selected_format}"
                    )
                else:
                    st.error(f"Conversion failed: {result.stderr}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                # Clean up output file
                if output_path.exists():
                    os.remove(output_path)
    else:
        st.error("Unsupported file type. Please upload a markdown, HTML, DOCX, or ODT file.")
    
    # Cleanup input file
    os.remove(temp_path)
    if temp_path.parent.exists() and not any(temp_path.parent.iterdir()):
        temp_path.parent.rmdir()