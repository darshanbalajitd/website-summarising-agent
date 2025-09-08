import streamlit as st
import requests
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

from functions import (
    scrape_gallery_blocks,
    scrape_images_with_following_caption,
    extract_title,
    extract_paragraph_chunks,
    extract_h1_headers,
    extract_time_tags,
    call_api
)

# --- CONFIG ---
API_MODE = "remote"  # change to "local" to use Ollama

st.set_page_config(page_title="Website Summarizer", layout="wide")

# --- URL Input ---
st.sidebar.markdown("### 🔗 Enter Website URL")
url = st.sidebar.text_input("Paste a URL to summarize")


# --- Scraping Workflow ---
def scrape_content(url):
    """Launch browser, scrape images and text, then summarize via API."""
    image_data = []
    text_chunks = []

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)

        # --- Anti-bot headers ---
        parsed = urlparse(url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": f"{parsed.scheme}://{parsed.netloc}/"
        }
        context = browser.new_context()
        page = context.new_page()

        # --- Navigate and trigger lazy loading ---
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.evaluate("""
            () => {
                let totalHeight = 0;
                const distance = 500;
                const timer = setInterval(() => {
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if (totalHeight >= document.body.scrollHeight) {
                        clearInterval(timer);
                    }
                }, 200);
            }
        """)

        # --- Scrape IMAGES ---
        st.subheader("📷 Images")
        with st.spinner("Loading images..."):
            figures = page.query_selector_all("figure:has(figcaption)")
            for figure in figures:
                img = figure.query_selector("img")
                caption = figure.query_selector("figcaption")
                if img:
                    src = img.get_attribute("src")
                    if src and src.startswith("//"):
                        src = "https:" + src
                    if src and src.startswith("http") and "svg" not in src:
                        caption_text = caption.inner_text().strip() if caption else ""
                        image_data.append({"src": src, "caption": caption_text})
            scrape_gallery_blocks(page, len(image_data) + 1)
            scrape_images_with_following_caption(page, len(image_data) + 1)

            # Display images 
            if image_data:
                cols = st.columns(3)  # 3 images per row
                for i, img in enumerate(image_data):
                    with cols[i % 3]:
                        st.image(img["src"], caption=img["caption"], width=300)


        # --- Scrape TEXT ---
        html = page.content()
        title = extract_title(html)
        title_chunk = {"Chunk": f"# Title\n{title}"}
        paragraphs = extract_paragraph_chunks(html)
        headers = extract_h1_headers(html)
        times = extract_time_tags(html)
        text_chunks = [title_chunk] + headers + times + paragraphs

        # --- Summarize TEXT via API ---
        context_text = "\n".join([c["Chunk"] for c in text_chunks])
        context_images = "\n".join([f"{img['caption']} ({img['src']})" for img in image_data])

        messages = [
             {
          "role": "system",
          "content": (
            "You are a highly skilled assistant that specializes in analyzing websites. "
            "You will be provided with scraped website content including text and images. "
            "Your task is to generate clear, accurate, and insightful summaries. "
            "Always focus on main ideas, context, and any key details the user should know. "
            "If there are images, incorporate their captions into the summary in a natural way. "
            "If the text contains times, dates, or locations, highlight them. "
            "Keep the summary factual and concise, while covering the most important points."
                )
            },
            {
          "role": "user",
          "content": (
            f"Here is the content scraped from the website:\n\n"
            f"--- TEXT CONTENT START ---\n{context_text}\n--- TEXT CONTENT END ---\n\n"
            f"--- IMAGE CAPTIONS START ---\n{context_images}\n--- IMAGE CAPTIONS END ---\n\n"
            "Now, please provide a structured summary that includes:\n"
            "1. 📌 Main topic and purpose of the website/article.\n"
            "2. 📰 Key facts and events mentioned.\n"
            "3. 🖼️ Important details from the images/captions.\n"
            "4. 📅 Any dates, names, or locations if available.\n"
            "5. ✅ A concise conclusion or takeaway.\n\n"
            "Format the response in clean markdown with short sections or bullet points."
                 )
            }
           ]


        with st.spinner("Summarizing text..."):
            summary = call_api(messages, mode=API_MODE)

        browser.close()

    return image_data, text_chunks, summary
    
# --- Main Chat Interface ---
st.title("🧠 Website Summarizer")

# --- Run Summarization ---
if url:
    with st.spinner("⏳ Scraping and summarizing website..."):
        try:
            image_data, text_chunks, summary = scrape_content(url)

            # --- Display summary ---
            st.subheader("📝 Website Summary")
            st.write(summary)

            # Save image/text arrays in session state for Q&A
            st.session_state.image_data = image_data
            st.session_state.text_chunks = text_chunks
            st.session_state.summary = summary

        except Exception as e:
            st.error(f"Failed to summarize: {e}")



# Show messages 
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Chat input for Q&A
user_input = st.chat_input("Ask about the website...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Build context from scraped content
    context_text = "\n".join([c["Chunk"] for c in st.session_state.get("text_chunks", [])])
    context_images = "\n".join([f"{img['caption']} ({img['src']})" for img in st.session_state.get("image_data", [])])
    messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful AI assistant that answers user questions "
            "based only on the provided website content (text and images). "
            "Do not make up information that is not present. "
            "If the answer cannot be found in the content, say so clearly. "
            "Always use a clear, structured explanation and reference both text and images if relevant. "
            "Format the response in markdown for readability."
        )
    },
    {
        "role": "user",
        "content": (
            f"Here is the scraped website content:\n\n"
            f"--- TEXT CONTENT START ---\n{context_text}\n--- TEXT CONTENT END ---\n\n"
            f"--- IMAGE CAPTIONS START ---\n{context_images}\n--- IMAGE CAPTIONS END ---\n\n"
            f"The user’s question is:\n❓ {user_input}\n\n"
            "Please answer in the following structured way:\n"
            "1. 📖 Direct answer to the question (based only on the content).\n"
            "2. 🔎 Supporting details from the text.\n"
            "3. 🖼️ If applicable, relevant details from the images/captions.\n"
            "4. ✅ Short concluding remark.\n"
        )
    }
]


    # Call API for response
    response = call_api(messages, mode=API_MODE)

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Display assistant message
    st.chat_message("assistant").markdown(response)

