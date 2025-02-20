"""Module containing Pandoc format definitions and related utilities."""

from typing import Dict, List

# Define supported Pandoc formats
PANDOC_FORMATS: Dict[str, Dict[str, str | List[str]]] = {
    # Lightweight markup formats
    'text/markdown': {'ext': '.md', 'pandoc_format': 'markdown', 'output_formats': ['html', 'pdf', 'docx', 'odt', 'pptx', 'epub', 'latex', 'rst', 'org', 'textile', 'mediawiki', 'dokuwiki']},
    'text/plain': {'ext': '.md', 'pandoc_format': 'markdown', 'output_formats': ['html', 'pdf', 'docx', 'odt', 'pptx', 'epub', 'latex', 'rst', 'org', 'textile', 'mediawiki', 'dokuwiki']},
    'text/x-rst': {'ext': '.rst', 'pandoc_format': 'rst', 'output_formats': ['md', 'html', 'pdf', 'docx', 'odt', 'pptx', 'epub', 'latex']},
    'text/org': {'ext': '.org', 'pandoc_format': 'org', 'output_formats': ['md', 'html', 'pdf', 'docx', 'odt', 'pptx', 'epub', 'latex']},
    
    # HTML formats
    'text/html': {'ext': '.html', 'pandoc_format': 'html', 'output_formats': ['md', 'pdf', 'docx', 'odt', 'pptx', 'epub', 'latex', 'rst', 'org', 'textile']},
    
    # Word processor formats
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': {'ext': '.docx', 'pandoc_format': 'docx', 'output_formats': ['md', 'html', 'pdf', 'odt', 'pptx', 'epub', 'latex', 'rst']},
    'application/vnd.oasis.opendocument.text': {'ext': '.odt', 'pandoc_format': 'odt', 'output_formats': ['md', 'html', 'pdf', 'docx', 'pptx', 'epub', 'latex', 'rst']},
    'text/rtf': {'ext': '.rtf', 'pandoc_format': 'rtf', 'output_formats': ['md', 'html', 'pdf', 'docx', 'odt', 'pptx', 'epub', 'latex']},
    
    # Ebooks
    'application/epub+zip': {'ext': '.epub', 'pandoc_format': 'epub', 'output_formats': ['md', 'html', 'pdf', 'docx', 'odt', 'latex']},
    
    # Interactive notebooks
    'application/x-ipynb+json': {'ext': '.ipynb', 'pandoc_format': 'ipynb', 'output_formats': ['md', 'html', 'pdf', 'docx', 'odt', 'latex']},
    
    # Wiki formats
    'text/x-wiki': {'ext': '.wiki', 'pandoc_format': 'mediawiki', 'output_formats': ['md', 'html', 'pdf', 'docx', 'odt', 'latex']},
    
    # LaTeX
    'text/x-tex': {'ext': '.tex', 'pandoc_format': 'latex', 'output_formats': ['md', 'html', 'pdf', 'docx', 'odt', 'pptx', 'epub']}
}

# Format categories for UI organization
FORMAT_CATEGORIES = {
    'Markup Formats': ['text/markdown', 'text/plain', 'text/x-rst', 'text/org'],
    'Document Formats': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.oasis.opendocument.text', 'text/rtf'],
    'Web Formats': ['text/html'],
    'eBook Formats': ['application/epub+zip'],
    'Notebook Formats': ['application/x-ipynb+json'],
    'Wiki Formats': ['text/x-wiki'],
    'LaTeX': ['text/x-tex']
}

def get_output_formats(mime_type: str) -> List[str]:
    """Get available output formats for a given MIME type.

    Args:
        mime_type: The MIME type of the input file.

    Returns:
        List of supported output formats for the given MIME type.
    """
    return PANDOC_FORMATS.get(mime_type, {}).get('output_formats', [])

def get_pandoc_format(mime_type: str) -> str:
    """Get the Pandoc format name for a given MIME type.

    Args:
        mime_type: The MIME type of the input file.

    Returns:
        The Pandoc format name for the given MIME type.
    """
    return PANDOC_FORMATS.get(mime_type, {}).get('pandoc_format', '')

def is_supported_format(mime_type: str) -> bool:
    """Check if a given MIME type is supported.

    Args:
        mime_type: The MIME type to check.

    Returns:
        True if the MIME type is supported, False otherwise.
    """
    return mime_type in PANDOC_FORMATS