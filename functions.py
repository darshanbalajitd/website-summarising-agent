# 📦 Import necessary libraries
import os
import time
import requests
import pandas as pd
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# 🔗 Target page URL (to be filled in)
TARGET_URL = ""
parsed = urlparse(TARGET_URL)

# 🧩 Scrape images from gallery-style containers
def scrape_gallery_blocks(page, start_index):
    gallery_blocks = page.query_selector_all("div.phtwrp, div.gallery, div.carousel, div[data-gallery]")
    if not gallery_blocks:
        return start_index
    print(f"\n🖼️ Found {len(gallery_blocks)} gallery blocks. Downloading gallery images...\n")

    seen_sources = set()
    index = start_index

    for block in gallery_blocks:
        img = block.query_selector("img")
        caption = block.query_selector("figcaption") or block.query_selector(".phtdesc") or block.query_selector(".caption")
        if img:
            src = img.get_attribute("src")
            if src and src.startswith("//"):
                src = "https:" + src
            if src and src.startswith("http") and "svg" not in src and src not in seen_sources:
                seen_sources.add(src)
                caption_text = caption.inner_text().strip() if caption else ""
                download_image(src, index, caption_text)
                index += 1
    return index

# 🧩 Scrape images followed by caption-like siblings inside article blocks
def scrape_images_with_following_caption(page, start_index):
    article_blocks = page.query_selector_all("div[class^='Article']")
    if not article_blocks:
        return start_index
    print(f"\n🖼️ Found {len(article_blocks)} <div class^='Article'> blocks. Scanning for images with following captions...\n")

    index = start_index
    seen_sources = set()

    for block in article_blocks:
        img_elements = block.query_selector_all("img")
        for img in img_elements:
            src = img.get_attribute("src")
            if not src or "svg" in src or src in seen_sources:
                continue
            if src.startswith("//"):
                src = "https:" + src
            if not src.startswith("http"):
                continue

            # 🚫 Skip images inside 'Author-' class containers
            ancestors = img.evaluate_handle("""
                node => {
                    const matches = [];
                    let current = node.parentElement;
                    while (current) {
                        if (current.className && current.className.includes('Author-')) {
                            matches.push(current.className);
                        }
                        current = current.parentElement;
                    }
                    return matches;
                }
            """)
            has_author_ancestor = ancestors.evaluate("matches => matches.length > 0")
            if has_author_ancestor:
                continue

            # 📝 Check next sibling for caption-like content
            caption = img.evaluate_handle("node => node.nextElementSibling")
            caption_text = ""
            is_element = caption.evaluate("node => node && node.nodeType === 1")
            if is_element:
                class_name = caption.evaluate("node => node.className || ''")
                if any(kw in class_name.lower() for kw in ["caption", "credit", "wrapper"]):
                    caption_text = caption.evaluate("node => node.innerText").strip()

            # Combine alt text and caption
            description = img.get_attribute("alt") or ""
            full_text = f"{description}\n\n{caption_text}".strip()
            seen_sources.add(src)
            download_image(src, index, full_text)
            index += 1
    return index

# 🧠 Extract <title> from HTML
def extract_title(html):
    soup = BeautifulSoup(html, 'html.parser')
    title_tag = soup.find('title')
    return title_tag.get_text(" ", strip=True) if title_tag else ""

# 🧠 Extract paragraph chunks from main content
def extract_paragraph_chunks(html):
    soup = BeautifulSoup(html, 'html.parser')
    content_root = soup.find(id='mw-content-text') or soup.find('body')
    if not content_root:
        return []
    chunks = []
    for p in content_root.find_all('p'):
        for sup in p.find_all('sup'):
            sup.decompose()
        text = p.get_text(" ", strip=True)
        if text:
            chunks.append({"Chunk": f"# Paragraph\n{text}"})
    return chunks

# 🧠 Extract all <h1> headers
def extract_h1_headers(html):
    soup = BeautifulSoup(html, 'html.parser')
    headers = []
    for div in soup.find_all('div'):
        for h in div.find_all('h1'):
            text = h.get_text(" ", strip=True)
            if text:
                headers.append({"Chunk": f"# Header h1\n{text}"})
    return headers

# 🧠 Extract all <time> tags
def extract_time_tags(html):
    soup = BeautifulSoup(html, 'html.parser')
    times = []
    for div in soup.find_all('div'):
        for t in div.find_all('time'):
            text = t.get_text(" ", strip=True)
            if text:
                times.append({"Chunk": f"# Time\n{text}"})
    return times

# --- API Helper ---
def call_api(messages, mode="remote"):
    """Call the LLM API (remote Hyperbolic or local Ollama)."""
    try:
        if mode == "remote":
            url = "https://api.hyperbolic.xyz/v1/chat/completions" # replace with desired api endpoint
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer API_KEY"  # replace with real key
            }
            data = {
                "messages": messages,
                "model": "meta-llama/Meta-Llama-3-70B-Instruct",
                "max_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.9
            }
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

        elif mode == "local":
            url = "http://localhost:11434/api/chat"
            data = {
                "model": "llama3.1",  # adjust to your Ollama model name
                "messages": messages,
                "stream": False
            }
            response = requests.post(url, json=data, timeout=60)
            response.raise_for_status()
            return response.json()["message"]["content"]

    except Exception as e:
        return f"❌ API call failed: {e}"
