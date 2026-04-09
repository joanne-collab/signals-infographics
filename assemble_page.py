import os
import glob
from bs4 import BeautifulSoup
import shutil

# Configuration
INPUT_HTML_DIR = 'input_html'
ARCHIVE_DIR = os.path.join(INPUT_HTML_DIR, 'archive')
MASTER_INDEX_FILE = 'index.html'

def get_latest_html_file(directory):
    """Finds the most recent .html file in the input directory."""
    html_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.html')]
    if not html_files:
        return None
    latest_file = max(html_files, key=os.path.getmtime)
    return latest_file

def extract_content(html_file_path):
    """Extracts CSS and Body content from the Claude HTML file."""
    with open(html_file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Capture all style tags
    style_content = ''
    for style_tag in soup.find_all('style'):
        style_content += str(style_tag)

    # Capture inner body content
    body_content = ''
    body_tag = soup.find('body')
    if body_tag:
        body_content = str(body_tag.decode_contents())

    return style_content, body_content

def inject_content_into_master(style_content, body_content, master_file_path):
    with open(master_file_path, 'r', encoding='utf-8') as f:
        master_soup = BeautifulSoup(f, 'html.parser')

    # 1. Surgical Style Injection
    head_tag = master_soup.find('head')
    if head_tag:
        # Delete any style tags that ARE NOT 'brand-styles'
        for style in head_tag.find_all('style'):
            if style.has_attr('id') and style['id'] == 'brand-styles':
                continue 
            style.decompose()
        
        # Add Claude's styles in a clean new block
        clean_css = style_content.replace('<style>', '').replace('</style>', '')
        new_style_tag = master_soup.new_tag("style")
        new_style_tag.string = clean_css
        head_tag.append(new_style_tag)

    # 2. Body Injection
    target = master_soup.find(id='infographic-content')
    if target:
        target.clear()
        content_soup = BeautifulSoup(body_content, 'html.parser')
        target.append(content_soup)
    
    with open(master_file_path, 'w', encoding='utf-8') as f:
        f.write(str(master_soup))

def main():
    """The main execution loop for finding, processing, and archiving files."""
    latest_file = get_latest_html_file(INPUT_HTML_DIR)
    if not latest_file:
        print(f"No HTML files found in {INPUT_HTML_DIR}")
        return

    print(f"Processing latest file: {latest_file}")
    style_content, body_content = extract_content(latest_file)
    inject_content_into_master(style_content, body_content, MASTER_INDEX_FILE)
    print(f"Content successfully injected into {MASTER_INDEX_FILE}")

    # --- FIX STARTS HERE ---
    # Ensure archive folder exists
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
    
    # Check if a file with the same name is already in the archive
    dest_path = os.path.join(ARCHIVE_DIR, os.path.basename(latest_file))
    if os.path.exists(dest_path):
        os.remove(dest_path) # Delete the old archived version to make room
    
    shutil.move(latest_file, ARCHIVE_DIR)
    # --- FIX ENDS HERE ---
    
    print(f"Moved {latest_file} to {ARCHIVE_DIR}")

if __name__ == '__main__':
    main()