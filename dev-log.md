# Development Log

## 2024-02-21
### Remote Image Support
- Implemented automatic handling of remote image URLs in Markdown documents
- Added functionality to download and process remote images during conversion
- Enhanced document processing to maintain image references integrity

### UI Enhancements
- Added prominent feature highlights section in the interface
- Improved visual feedback for file type detection and processing
- Enhanced user guidance for handling remote and local resources

## 2024-01-09
- Added support for text/plain MIME type to handle Markdown files that are detected as plain text
- Updated error message to be more specific about supported file types
- Fixed issue with Markdown files not being recognized properly due to MIME type detection
- Tested and verified Markdown to PDF/HTML/DOCX/ODT conversion paths

## Next Steps
- Consider adding support for more Pandoc formats (RST, ORG, EPUB, etc.)
- Add support for PowerPoint (PPTX) as output format
- Implement better error handling for PDF conversion when LaTeX is not installed
- Consider adding format-specific options (e.g., template selection, metadata)

## 2024-02-19

### Project Initialization
- Set up basic project structure
- Created requirements.txt with essential dependencies:
  - streamlit for the web interface
  - pandoc for document conversion
  - python-magic for file type detection

### Initial Application Setup
- Created app.py with basic Streamlit UI
- Implemented file upload functionality
- Added file type detection using python-magic
- Set up temporary file handling with cleanup

### Next Steps
- Implement pandoc format detection
- Add conversion options based on input file type
- Add conversion functionality
- Implement file download feature

### Technical Decisions
1. Using python-magic for reliable file type detection instead of relying on file extensions
2. Implementing temporary file storage with automatic cleanup to handle file uploads safely
3. Chose Streamlit for rapid UI development and easy deployment
4. Removed python-magic-bin dependency in favor of system libmagic for better compatibility

## 2024-02-20

### Feature Implementation
- Implemented comprehensive support for LaTeX-based PDF conversion
- Added support for multiple Pandoc formats including RST, ORG, EPUB, and PPTX
- Implemented local file reference detection and handling in Markdown documents
- Added support for image and link references in Markdown files

### UI Improvements
- Added a detailed conversion support table with categorized format listings
- Implemented an expandable view for supported format conversions
- Enhanced file type detection feedback
- Added clear error messages for missing referenced files

### Technical Enhancements
- Implemented robust temporary file handling with automatic cleanup
- Added resource path handling for referenced files in conversions
- Enhanced error handling for conversion failures
- Improved MIME type detection and format mapping

### Code Refactoring
- Separated format definitions into pandoc_formats.py for better maintainability
- Created file_utils.py for centralized file handling operations
- Improved code organization and modularity in app.py
- Enhanced type hints and documentation
- Implemented better temporary file management

### User Experience Improvements
- Modified conversion process to preserve original filenames in converted files
- Enhanced file handling to maintain consistent naming between input and output files

### Next Steps
- Add format-specific conversion options (templates, metadata)
- Implement batch conversion functionality
- Add preview functionality for supported formats
- Consider adding custom styling options for output formats