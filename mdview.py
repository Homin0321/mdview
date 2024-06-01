import streamlit as st
import sys

@st.cache_data
def read_file(filename):
    try:
        with open(filename, "r") as f:
            markdown_content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    return markdown_content.split("---\n")

def remove_leading_hashes(text):
  if text.startswith('#'):
    i = 0
    while i < len(text) and text[i] == '#':
      i += 1
    text = text[i:].lstrip()
  return text

@st.cache_data
def make_index(pages):
  index = []
  for page in pages:
    first_line = page.split('\n')[0]
    first_line = remove_leading_hashes(first_line)
    index.append(first_line)
  return index

def display_page(page_content):
    #st.divider()
    st.markdown(page_content, unsafe_allow_html=True)
    st.divider()

def find_index(list, target):
  for i, str in enumerate(list):
    if str == target:
      return i
  return -1

def main():
    if len(sys.argv) != 2:
        print("Usage: streamlit run md.py <filename>")
        sys.exit(1)

    pages = read_file(sys.argv[1])
    toc = make_index(pages)

    # Initialize session state for page navigation
    if "current_page" not in st.session_state:
        st.session_state.current_page = 0
    if 'sidebar_state' not in st.session_state:
        st.session_state.sidebar_state = False

    if st.session_state.sidebar_state == True:
        with st.sidebar:
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
    col1, col2, col3, col4 = st.columns([1, 1, 7, 1])

    with col1:
        if st.button("Prev", disabled=(st.session_state.current_page == 0)):
            st.session_state.current_page -= 1
            st.rerun()

    with col2:
        if st.button("ToC"):
            st.session_state.sidebar_state = True if st.session_state.sidebar_state == False else False
            st.rerun()

    with col3:
        page = st.slider("Go to", min_value=1, max_value=len(pages), 
            value=st.session_state.current_page + 1, 
            label_visibility="collapsed")
        page -= 1
        if page != st.session_state.current_page:
            st.session_state.current_page = page 
            st.rerun()

    with col4:
        if st.button("Next", disabled=(st.session_state.current_page == len(pages)-1)):
            st.session_state.current_page += 1
            st.rerun()

if __name__ == "__main__":
    main()