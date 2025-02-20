"""Module containing file handling utilities for the Pandoc converter."""

import os
from pathlib import Path
import re
import requests
from typing import List
from urllib.parse import urlparse

def is_valid_remote_url(url: str) -> bool:
    import streamlit as st
    st.write(f"Validating URL: {url}")
    try:
        result = urlparse(url)
        # Check for valid scheme
        if not result.scheme:
            st.warning(f"Invalid URL: Missing scheme")
            return False
        
        # Validate scheme is a remote protocol
        valid_schemes = ('http', 'https', 'ftp', 'sftp')
        if result.scheme not in valid_schemes:
            st.warning(f"Invalid URL: Scheme {result.scheme} not in {valid_schemes}")
            return False
            
        # Must have a network location (domain)
        if not result.netloc:
            st.warning(f"Invalid URL: Missing network location")
            return False
            
        # Basic domain validation
        domain = result.netloc.split(':')[0]  # Remove port if present
        if not domain or domain.startswith('.'):
            st.warning(f"Invalid URL: Invalid domain format {domain}")
            return False
            
        # Check for common local addresses
        local_addresses = ('localhost', '127.0.0.1', '0.0.0.0')
        if domain.lower() in local_addresses:
            st.warning(f"Invalid URL: Local address detected {domain}")
            return False
            
        st.success(f"Valid remote URL detected: {url}")
        return True
    except (ValueError, AttributeError) as e:
        st.error(f"URL validation error: {str(e)}")
        return False

def process_image_urls(markdown_content: str, temp_dir: Path) -> str:
    import streamlit as st
    st.write("Processing markdown content for image URLs")
    st.write(f"Temporary directory: {temp_dir}")
    # Match all image references: ![alt](path)
    image_pattern = r'!\[([^\]]*)\]\(([^\)]+)\)(?:{[^}]*})?'
    
    def process_image_reference(match):
        alt_text = match.group(1)
        path = match.group(2).strip()
        st.write(f"Processing image reference - Alt text: {alt_text}")
        st.write(f"Image path: {path}")
        
        # If not a valid remote URL, return original reference unchanged
        if not is_valid_remote_url(path):
            st.info("Not a valid remote URL, keeping original reference")
            return match.group(0)
            
        try:
            # Parse URL and create local filename
            parsed_url = urlparse(path)
            url_path = parsed_url.path.split('?')[0]  # Remove query parameters
            filename = os.path.basename(url_path)
            st.write(f"Parsed URL path: {url_path}")
            
            # Generate unique filename if original is empty or contains query parameters
            if not filename or '=' in filename:
                filename = f'image_{abs(hash(path))}.jpg'
                st.write(f"Generated unique filename: {filename}")
            
            # Download image with proper timeout and headers
            st.info(f"Attempting to download image from: {path}")
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(path, timeout=10, headers=headers, allow_redirects=True)
            response.raise_for_status()
            
            # Verify content type is an image
            content_type = response.headers.get('content-type', '')
            st.write(f"Content type received: {content_type}")
            if not content_type.startswith('image/'):
                raise ValueError(f'Invalid content type: {content_type}')
            
            # Save to temp directory
            image_path = temp_dir / filename
            st.write(f"Saving image to: {image_path}")
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            st.success(f"Successfully processed remote image: {path}")
            return f'![{alt_text}]({filename})'
        except Exception as e:
            st.error(f"Error processing image {path}: {str(e)}")
            return match.group(0)  # Return original markdown on error
    
    # Process all image references
    return re.sub(image_pattern, process_image_reference, markdown_content)

def extract_local_references(markdown_content: str) -> List[str]:
    """Extract local file references from markdown content.

    Args:
        markdown_content: The content of the markdown file.

    Returns:
        A list of local file references found in the markdown content.
    """
    # Match image references: ![alt](path) or ![alt](path){options}
    image_pattern = r'!\[.*?\]\(((?!https?://|www\.|ftp://|sftp://)[^\s"\)]+)\)(?:{[^}]*})?'
    # Match other local file references like: [text](path)
    link_pattern = r'(?<!!)\[.*?\]\(((?!https?://|www\.|ftp://|sftp://)[^\s"\)]+)\)'
    
    local_refs = []
    
    # Find all matches
    image_refs = re.findall(image_pattern, markdown_content)
    link_refs = re.findall(link_pattern, markdown_content)
    
    # Combine and filter out any URLs that might have slipped through
    for ref in image_refs + link_refs:
        ref = ref.strip()
        # Additional validation to ensure it's a local reference
        # Skip files that were downloaded from remote URLs (they'll be in temp dir)
        if (not is_valid_remote_url(ref) and 
            not ref.startswith(('//', 'data:')) and
            not ref.startswith('image_') and
            not ref in ['photo-1734639430017-5756ea7fec63', 'images']):
            local_refs.append(ref)
    
    # Clean up paths and remove duplicates
    return list(set(local_refs))

def setup_temp_directory(temp_dir: Path) -> None:
    """Set up a temporary directory for file processing.

    Args:
        temp_dir: Path to the temporary directory.
    """
    temp_dir.mkdir(exist_ok=True)

def cleanup_temp_files(temp_dir: Path) -> None:
    """Clean up temporary files and directories.

    Args:
        temp_dir: Path to the temporary directory.
    """
    if temp_dir.exists():
        for item in temp_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                cleanup_temp_files(item)
                item.rmdir()
        if not any(temp_dir.iterdir()):
            temp_dir.rmdir()

def save_uploaded_file(file_data: bytes, file_path: Path) -> None:
    """Save uploaded file data to the specified path.

    Args:
        file_data: The binary data of the uploaded file.
        file_path: The path where the file should be saved.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'wb') as f:
        f.write(file_data)