"""Main application module for the Pandoc Converter."""

import streamlit as st
import magic
import os
import subprocess
from pathlib import Path

from pandoc_formats import PANDOC_FORMATS, FORMAT_CATEGORIES, get_output_formats, get_pandoc_format, is_supported_format
from file_utils import extract_local_references, setup_temp_directory, cleanup_temp_files, save_uploaded_file

# Set page config
st.set_page_config(
    page_title="Pandoc Converter",
    page_icon="📄",
    layout="centered"
)

# Title and description
st.title("Pandoc Converter")
st.markdown("Convert your documents between different formats using Pandoc")

# Initialize temporary directory
TEMP_DIR = Path("temp")
setup_temp_directory(TEMP_DIR)

def check_pandoc_installed():
    """Check if pandoc is installed and accessible."""
    try:
        subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

# Update the file uploader section
uploaded_file = st.file_uploader("Choose a file", type=None)

# Check if pandoc is installed
if not check_pandoc_installed():
    st.error("Pandoc is not installed. Please install Pandoc to use this converter. Visit https://pandoc.org/installing.html for installation instructions.")
    st.stop()

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
    
    # If it's a markdown file, check for local references
    if file_type in ['text/markdown', 'text/plain']:
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        local_refs = extract_local_references(content)
        
        if local_refs:
            st.warning("This document contains references to local files:")
            st.write(", ".join(local_refs))
            
            # Create a file uploader for each referenced file
            uploaded_refs = {}
            for ref in local_refs:
                ref_file = st.file_uploader(f"Upload referenced file: {ref}", key=ref)
                if ref_file:
                    # Save referenced file to temp directory with original path structure
                    ref_path = temp_path.parent / Path(ref)
                    ref_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(ref_path, "wb") as f:
                        f.write(ref_file.getbuffer())
                    uploaded_refs[ref] = True
            
            # Only enable conversion if all referenced files are uploaded
            if len(uploaded_refs) < len(local_refs):
                st.error("Please upload all referenced files before converting")
                st.stop()
    
    # Check if file type is supported
    if file_type in PANDOC_FORMATS:
        # Get available output formats
        output_formats = PANDOC_FORMATS[file_type]['output_formats']
        selected_format = st.selectbox("Select output format", output_formats)
        
        if st.button("Convert"):
            try:
                # Prepare output path with original filename
                original_name = Path(uploaded_file.name).stem
                output_path = temp_path.parent / f"{original_name}.{selected_format}"
                
                # Run pandoc conversion
                input_format = PANDOC_FORMATS[file_type]['pandoc_format']
                cmd = ['pandoc', str(temp_path), '-f', input_format, '-t', selected_format, 
                      '--resource-path', str(temp_path.parent), '-o', str(output_path)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    # Read the converted file
                    with open(output_path, 'rb') as f:
                        converted_data = f.read()
                    
                    # Create download button
                    st.download_button(
                        label="Download converted file",
                        data=converted_data,
                        file_name=f"{original_name}.{selected_format}",
                        mime=f"application/{selected_format}"
                    )

                    # Create HTML preview
                    preview_path = temp_path.parent / 'preview.html'
                    preview_cmd = ['pandoc', str(temp_path), '-f', input_format, '-t', 'html', 
                                  '--resource-path', str(temp_path.parent), '-o', str(preview_path)]
                    preview_result = subprocess.run(preview_cmd, capture_output=True, text=True)
                    
                    if preview_result.returncode == 0:
                        with open(preview_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        st.markdown("### Document Preview")
                        st.components.v1.html(html_content, height=500, scrolling=True)
                        os.remove(preview_path)
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
# Add conversion support table at the bottom
with st.expander("View Supported Conversions"):
    st.markdown("### Supported Format Conversions")
    
    # Create categories for better organization
    categories = {
        'Markup Formats': ['text/markdown', 'text/plain', 'text/x-rst', 'text/org'],
        'Document Formats': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.oasis.opendocument.text', 'text/rtf'],
        'Web Formats': ['text/html'],
        'eBook Formats': ['application/epub+zip'],
        'Notebook Formats': ['application/x-ipynb+json'],
        'Wiki Formats': ['text/x-wiki'],
        'LaTeX': ['text/x-tex']
    }
    
    # Create table for each category
    for category, mime_types in categories.items():
        st.markdown(f"#### {category}")
        
        # Create table headers
        table_header = "| Input Format | Supported Output Formats |"
        table_separator = "|-------------|----------------------|"
        table_rows = []
        
        # Add rows for each format in category
        for mime_type in mime_types:
            if mime_type in PANDOC_FORMATS:
                format_info = PANDOC_FORMATS[mime_type]
                input_format = format_info['ext'].lstrip('.')
                output_formats = ', '.join(format_info['output_formats'])
                table_rows.append(f"| {input_format} | {output_formats} |")
        
        # Display table if there are rows
        if table_rows:
            table_content = '\n'.join([table_header, table_separator] + table_rows)
            st.markdown(table_content)
            st.markdown("")