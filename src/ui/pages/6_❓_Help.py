"""
Help & Documentation - View all project documentation with interactive navigation
"""
import streamlit as st
import os
import sys
import logging
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Help & Documentation",
    page_icon="❓",
    layout="wide"
)

# Get the Documents directory path
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "Documents")
INDEX_FILE = os.path.join(DOCS_DIR, "INDEX.md")


def read_markdown_file(file_path: str) -> str:
    """Read a markdown file and return its contents"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return f"Error reading file: {e}"


def convert_relative_links_for_display(content: str, current_file: str = "INDEX.md") -> str:
    """
    Convert relative markdown links to be compatible with Streamlit display.
    This makes links point to actual file locations that can be opened.
    """
    # Pattern to match markdown links: [text](path)
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'

    def replace_link(match):
        text = match.group(1)
        path = match.group(2)

        # Skip external links (http/https)
        if path.startswith('http://') or path.startswith('https://'):
            return f'[{text}]({path})'

        # Handle relative paths
        if path.startswith('./'):
            # Remove ./ prefix
            path = path[2:]
        elif path.startswith('../'):
            # Go up one directory
            path = path[3:]

        # Create a session state key for this link
        # We'll use this to track which document to display
        doc_name = path.split('/')[-1] if '/' in path else path

        # Return the link as-is for markdown rendering
        # We'll handle clicks separately
        return f'[{text}]({path})'

    return re.sub(link_pattern, replace_link, content)


def extract_document_links(content: str) -> list:
    """Extract all document links from markdown content"""
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    links = []

    for match in re.finditer(link_pattern, content):
        text = match.group(1)
        path = match.group(2)

        # Only include .md files, skip external links
        if path.endswith('.md') and not path.startswith('http'):
            # Clean up the path
            if path.startswith('./'):
                path = path[2:]
            elif path.startswith('../'):
                path = path[3:]

            links.append({
                'text': text,
                'path': path,
                'filename': os.path.basename(path)
            })

    return links


def display_document_viewer():
    """Display a document viewer with navigation"""
    st.title("❓ Help & Documentation")
    st.markdown("Browse and search through all project documentation")

    # Initialize session state for document viewing
    if 'current_doc' not in st.session_state:
        st.session_state.current_doc = 'INDEX.md'
    if 'doc_history' not in st.session_state:
        st.session_state.doc_history = []

    # Create two columns for navigation
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        if st.button("🏠 Home", use_container_width=True, help="Return to INDEX.md"):
            st.session_state.current_doc = 'INDEX.md'
            st.session_state.doc_history = []
            st.rerun()

    with col2:
        st.info(f"📄 **Current Document:** {st.session_state.current_doc}")

    with col3:
        if len(st.session_state.doc_history) > 0:
            if st.button("⬅️ Back", use_container_width=True, help="Go back to previous document"):
                if st.session_state.doc_history:
                    st.session_state.current_doc = st.session_state.doc_history.pop()
                    st.rerun()

    st.markdown("---")

    # Read and display the current document
    current_file_path = os.path.join(DOCS_DIR, st.session_state.current_doc)

    if not os.path.exists(current_file_path):
        st.error(f"❌ Document not found: {st.session_state.current_doc}")
        st.info("Click 🏠 Home to return to the documentation index")
        return

    # Read the document
    doc_content = read_markdown_file(current_file_path)

    # Create a sidebar with document links if viewing INDEX.md
    if st.session_state.current_doc == 'INDEX.md':
        with st.sidebar:
            st.markdown("### 📚 Quick Navigation")
            st.markdown("Click any document below to view it:")

            # Extract all document links
            links = extract_document_links(doc_content)

            # Group by category (simple approach - based on order)
            categories = {
                "🚀 Getting Started": [],
                "🏗️ Core Features": [],
                "🔌 MCP Integration": [],
                "🎨 UI Components": [],
                "⚡ Performance": [],
                "🔧 Troubleshooting": [],
                "📋 Project Context": []
            }

            current_category = None
            for link in links:
                filename = link['filename']

                # Categorize based on filename
                if any(x in filename for x in ['SETUP', 'MONGODB_SETUP', 'GITHUB_SETUP', 'PROJECT_CONTEXT', 'IMPLEMENTATION']):
                    current_category = "🚀 Getting Started"
                elif any(x in filename for x in ['DYNAMIC', 'STREAMLIT', 'AI_', 'SETTINGS']):
                    current_category = "🏗️ Core Features"
                elif 'MCP' in filename:
                    current_category = "🔌 MCP Integration"
                elif 'UI' in filename or 'HOME_ICON' in filename:
                    current_category = "🎨 UI Components"
                elif 'OPTIMIZATION' in filename or 'PERFORMANCE' in filename or 'SPLIT' in filename or 'CLEANUP' in filename:
                    current_category = "⚡ Performance"
                elif any(x in filename for x in ['TROUBLESHOOTING', 'FIX', 'ERROR']):
                    current_category = "🔧 Troubleshooting"
                elif 'CONTEXT' in filename or 'SUMMARY' in filename or 'REORGANIZATION' in filename:
                    current_category = "📋 Project Context"

                if current_category:
                    categories[current_category].append(link)

            # Display categorized links
            # Track seen documents to avoid duplicates
            seen_docs = set()

            for category, cat_links in categories.items():
                if cat_links:
                    st.markdown(f"**{category}**")
                    for idx, link in enumerate(cat_links):
                        # Skip if already displayed
                        if link['filename'] in seen_docs:
                            continue
                        seen_docs.add(link['filename'])

                        # Create a button for each document
                        button_label = link['text'].replace('**', '').strip()
                        # Truncate long labels
                        if len(button_label) > 40:
                            button_label = button_label[:37] + "..."

                        # Use category + filename for unique key
                        unique_key = f"nav_{category.replace(' ', '_')}_{link['filename']}"

                        if st.button(button_label, key=unique_key, use_container_width=True):
                            # Save current doc to history
                            if st.session_state.current_doc != link['filename']:
                                st.session_state.doc_history.append(st.session_state.current_doc)
                            # Use filename only (not full path) since all docs are in Documents root
                            st.session_state.current_doc = link['filename']
                            st.rerun()
                    st.markdown("")  # Add spacing

    # Display the document content
    # Split into two columns for better readability on wide screens
    col_main = st.container()

    with col_main:
        # Add a search box
        if st.session_state.current_doc == 'INDEX.md':
            search_query = st.text_input("🔍 Search documentation", placeholder="Enter keywords to search...", key="doc_search")

            if search_query:
                # Filter content based on search
                lines = doc_content.split('\n')
                matching_lines = []
                for i, line in enumerate(lines):
                    if search_query.lower() in line.lower():
                        # Include some context (3 lines before and after)
                        start = max(0, i - 3)
                        end = min(len(lines), i + 4)
                        matching_lines.extend(lines[start:end])
                        matching_lines.append("---")

                if matching_lines:
                    st.success(f"Found {len([l for l in matching_lines if search_query.lower() in l.lower()])} matches")
                    filtered_content = '\n'.join(matching_lines)
                    st.markdown(filtered_content, unsafe_allow_html=True)
                else:
                    st.warning("No matches found")
            else:
                # Display full content
                st.markdown(doc_content, unsafe_allow_html=True)
        else:
            # For non-index files, display full content
            st.markdown(doc_content, unsafe_allow_html=True)

    # Add a download button
    st.markdown("---")
    col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])

    with col_dl2:
        st.download_button(
            label=f"📥 Download {st.session_state.current_doc}",
            data=doc_content,
            file_name=st.session_state.current_doc,
            mime="text/markdown",
            use_container_width=True
        )


def main():
    """Main help page"""

    # Check if Documents directory exists
    if not os.path.exists(DOCS_DIR):
        st.error(f"❌ Documents directory not found: {DOCS_DIR}")
        st.info("Please ensure the Documents folder exists in the project root directory")
        return

    # Check if INDEX.md exists
    if not os.path.exists(INDEX_FILE):
        st.error(f"❌ INDEX.md not found: {INDEX_FILE}")
        st.info("Please ensure INDEX.md exists in the Documents folder")
        return

    # Display the document viewer
    display_document_viewer()

    # Add footer with helpful info
    st.markdown("---")
    with st.expander("💡 How to Use This Help Page"):
        st.markdown("""
        ### Navigation
        - **🏠 Home** - Return to the documentation index
        - **⬅️ Back** - Go back to the previous document
        - **Sidebar** - Quick access to all documentation files (on INDEX.md)

        ### Search
        - Use the search box (on INDEX.md) to find specific topics
        - Search is case-insensitive
        - Results show matching sections with context

        ### Viewing Documents
        - Click any link in the sidebar to view a document
        - Use the Back button to return to previous documents
        - Download any document using the download button

        ### Categories
        - 🚀 Getting Started - Setup and installation guides
        - 🏗️ Core Features - Main functionality documentation
        - 🔌 MCP Integration - Model Context Protocol docs
        - 🎨 UI Components - User interface guides
        - ⚡ Performance - Optimization documentation
        - 🔧 Troubleshooting - Fix guides and solutions
        - 📋 Project Context - High-level project information

        ### Tips
        - Bookmark frequently used documents by opening them first
        - Use search to quickly find specific information
        - Check "Recent Updates" in INDEX.md for latest changes
        """)


if __name__ == "__main__":
    main()
