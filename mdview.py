import streamlit as st
from io import StringIO
import sys
import re

@st.cache_data
def read_file(filename):
    # Reads the content of a file
    try:
        with open(filename, "r") as f:
            content = f.read()
    except FileNotFoundError:
        # Handles the case where the file is not found
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    return content

@st.cache_data
def read_file_from_session():
    # Retrieves the uploaded file from session state
    return st.session_state.uploaded_file

# Function to split based on a regular expression
def split_by_regex(regex, text):
    parts = []
    current_part = ""
    for line in text.splitlines():
        if re.match(regex, line):
            if current_part:
                parts.append(current_part)
                current_part = ""
            current_part += line + "\n"
        else:
            current_part += line + "\n"
    if current_part:
        parts.append(current_part)
    return parts

@st.cache_data
def split_content(text):
    # Attempt to split by the primary separator "---"
    pages = text.split("---\n")
    if len(pages) > 1:
        return pages

    # Attempt to split by headings (e.g., "# Heading")
    parts = split_by_regex(r'^(#+)\s+(.*)', text)
    if len(parts) > 1:
        return parts

    # Attempt to split by "** ~ **\n"
    parts = split_by_regex(r'^\*\*(.*?)\*\*$', text)
    if len(parts) > 1:
        return parts

    # If no splitting occurred, return the original text as a single element list
    return [text]

def remove_decorators(text):
    # Removes leading hashes from a string (typically a heading)
    if text.startswith('#'):
        i = 0
        while i < len(text) and text[i] == '#':
            i += 1
        text = text[i:].lstrip()
    
    if text.startswith("**") and text.endswith("**"):
        text = text[2:-2]

    if text.endswith(":"):
        text = text[:-1]
    return text

@st.cache_data
def make_index(pages):
    # Creates an index of page titles from the first line of each page
    index = []
    for i, page in enumerate(pages):
        first_line = page.strip().split('\n')[0]
        first_line = remove_decorators(first_line)
        first_line = first_line[:30] + "..." if len(first_line) > 30 else first_line
        first_line = f"{i+1}. {first_line}"
        index.append(first_line)
    return index

def display_page(page_content):
    # Displays a page's content in Markdown format with a divider
    st.markdown(page_content, unsafe_allow_html=True)
    st.divider()

def find_index(lst, target):
    # Finds the index of a target item in a list
    for i, str in enumerate(lst):
        if str == target:
            return i
    return -1

def show_content(content):
    # Handles the display and navigation of content pages
    pages = split_content(content)
    toc = make_index(pages)

    # Initialize session state for page navigation
    if "current_page" not in st.session_state:
        st.session_state.current_page = 0
    if 'sidebar_state' not in st.session_state:
        st.session_state.sidebar_state = False

    # Show table of contents in the sidebar if enabled
    if st.session_state.sidebar_state:
        with st.sidebar:
            st.subheader(st.session_state.file_name, divider='rainbow')
            idx = st.session_state.current_page
            selected = st.radio("Contents:", toc, index=idx)
            if selected is not None:
                idx = find_index(toc, selected)
                if idx != -1 and st.session_state.current_page != idx:
                    st.session_state.current_page = idx
                    st.rerun()

    # Display the current page content
    display_page(pages[st.session_state.current_page])

    # Navigation slider and buttons
    col1, col2, col3, col4, col5 = st.columns([1, 1, 7, 1, 1])

    with col1:
        # Previous page button
        if st.button("◀", disabled=(st.session_state.current_page == 0)):
            st.session_state.current_page -= 1
            st.rerun()

    with col2:
        # Toggle table of contents sidebar
        if st.button(":compass:"):
            st.session_state.sidebar_state = not st.session_state.sidebar_state
            st.rerun()

    with col3:
        # Slider to navigate to a specific page
        if len(pages) > 1:
            page = st.slider("Go to", min_value=1, max_value=len(pages),
                             value=st.session_state.current_page + 1,
                             label_visibility="collapsed")
            page -= 1
            if page != st.session_state.current_page:
                st.session_state.current_page = page
                st.rerun()

    with col4:
        # Show Markdown source
        with st.popover(":page_with_curl:"):
            st.code(pages[st.session_state.current_page], language="markdown")

    with col5:
        # Next page button
        if st.button("▶", disabled=(st.session_state.current_page == len(pages)-1)):
            st.session_state.current_page += 1
            st.rerun()

def main():
    # Main function to control the app flow
    content = None
    st.set_page_config(page_title="Markdown Viewer", page_icon=":book:")
    if len(sys.argv) == 2:
        # Read file from command line argument
        st.session_state.file_name = file_name = sys.argv[1]
        content = read_file(file_name)
    elif 'uploaded_file' not in st.session_state:
        st.header("Markdown Viewer", divider='rainbow')
        
        # Text input interface
        form = st.form(key="box")
        text = form.text_area("Input Text here")
        submit = form.form_submit_button("Submit")
        if submit:
            st.cache_data.clear()
            st.session_state.uploaded_file = text
            st.session_state.file_name = "" 
            st.rerun()
            
        # File upload interface
        uploaded_file = st.file_uploader("Upload a Markdown file", type=['md'])
        if uploaded_file is not None:
            st.cache_data.clear()
            st.session_state.uploaded_file = uploaded_file.getvalue().decode("utf-8")
            st.session_state.file_name = uploaded_file.name
            st.success("File uploaded successfully!")
            if st.button("Show me the Markdown"):
                st.rerun()       
    else:
        # Read file from session state
        content = read_file_from_session()

    if content is not None:
        show_content(content)

if __name__ == "__main__":
    main()
