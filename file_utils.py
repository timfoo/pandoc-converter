"""Module containing file handling utilities for the Pandoc converter."""

import os
from pathlib import Path
import re
import requests
from typing import List
from urllib.parse import urlparse

def process_image_urls(markdown_content: str, temp_dir: Path) -> str:
    """Process image URLs in markdown content by downloading them to temp directory.

    Args:
        markdown_content: The content of the markdown file.
        temp_dir: Path to the temporary directory.

    Returns:
        Updated markdown content with local references to downloaded images.
    """
    # Match all image references: ![alt](path)
    image_pattern = r'!\[([^\]]*)\]\(([^\)]+)\)(?:{[^}]*})?'
    
    def is_url(path):
        """Check if the path is a URL."""
        try:
            result = urlparse(path)
            # Consider both http(s) and other valid URL schemes
            valid_schemes = ('http', 'https', 'ftp', 'sftp')
            return result.scheme in valid_schemes and bool(result.netloc)
        except ValueError:
            return False
    
    def process_image_reference(match):
        alt_text = match.group(1)
        path = match.group(2).strip()
        
        # If not a URL, return original reference unchanged
        if not is_url(path):
            return match.group(0)
            
        try:
            # Parse URL and create local filename
            parsed_url = urlparse(path)
            url_path = parsed_url.path.split('?')[0]  # Remove query parameters
            filename = os.path.basename(url_path)
            
            # Generate unique filename if original is empty or contains query parameters
            if not filename or '=' in filename:
                filename = f'image_{abs(hash(path))}.jpg'
            
            # Download image
            response = requests.get(path, timeout=10)
            response.raise_for_status()
            
            # Save to temp directory
            image_path = temp_dir / filename
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            # Return markdown with local reference
            return f'![{alt_text}]({filename})'
        except Exception as e:
            print(f"Failed to process image {path}: {str(e)}")
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
    image_pattern = r'!\[.*?\]\(((?!https?://|www\.)[^\s")]+)\)(?:{[^}]*})?'
    # Match other local file references like: [text](path)
    link_pattern = r'(?<!!)\[.*?\]\(((?!https?://|www\.)[^\s")]+)\)'
    
    local_refs = []
    
    # Find all matches
    image_refs = re.findall(image_pattern, markdown_content)
    link_refs = re.findall(link_pattern, markdown_content)
    
    # Combine and filter out any web URLs that might have slipped through
    local_refs.extend([ref for ref in image_refs if not ref.startswith(('http://', 'https://', 'www.', '//'))])
    local_refs.extend([ref for ref in link_refs if not ref.startswith(('http://', 'https://', 'www.', '//'))])
    
    # Clean up paths and remove duplicates
    local_refs = list(set(ref.strip() for ref in local_refs))
    return local_refs

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