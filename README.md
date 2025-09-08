# 🧠 Website Summarising Agent

A web-based tool that scrapes text and images from websites, generates summaries, and allows interactive Q&A.  
Built with **Streamlit** as the frontend, **Playwright** for scraping, and either a **remote LLM API** (e.g., Hyperbolic) or a **local LLM** via [Ollama](https://ollama.com/).

---

## 🚀 Demo

<video src="https://private-user-images.githubusercontent.com/209789676/486899263-279ec9c6-02a7-47ad-89c7-b24e683dbd2b.webm?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTczNTQ1NTMsIm5iZiI6MTc1NzM1NDI1MywicGF0aCI6Ii8yMDk3ODk2NzYvNDg2ODk5MjYzLTI3OWVjOWM2LTAyYTctNDdhZC04OWM3LWIyNGU2ODNkYmQyYi53ZWJtP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MDkwOCUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTA5MDhUMTc1NzMzWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9NWQ2OWRlMmM1YzlmMTQ2MzM4ZjMyOWFjZmRmNzYxMzBkYzJkYzFhYTc2M2M4NzJiMmJlYTE4MzRlOWI0MmI1OSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.TnAcdQpqoMBxgr6YHuK-xv7tJsBuT7PDkmSzzjg0ZII" controls width="100%">
  Your browser does not support the video tag.
</video>

## ⚙️ Requirements

- Python 3.9+
- The following Python libraries (see `requirements.txt`):
  - `streamlit`
  - `requests`
  - `playwright`
  - `beautifulsoup4`
  - `pandas`

Install all with:

```bash
pip install -r requirements.txt
```

Then install Playwright browser dependencies:

```bash
playwright install
```

---

## 🏗️ Architecture

- **Frontend (UI)**:  
  Built with **Streamlit**. Provides URL input, displays scraped images in a gallery/grid, shows summaries, and supports Q&A chat.

- **Agent (Scraper & Orchestrator)**:  
  Uses **Playwright** for browser simulation.  
  - Extracts text (`<title>`, `<h1>`, `<p>`, `<time>`).  
  - Extracts images with captions/alt text.  
  - Prepares structured content for summarisation.

- **AI / API Backend**:  
  - Can call a **remote LLM API** (e.g., Hyperbolic’s Meta-Llama 3).  
  - Or run locally with **Ollama** (`llama3` model or compatible).  
  - Generates summaries and answers user questions in context.

---

## 📝 Note

You can run your own **local AI** using [Ollama](https://ollama.com) (guide: [Install Ollama](https://github.com/ollama/ollama)).  
Alternatively, you can use any external API provider. If you use a remote API, **update the API key and endpoint** in the code (`functions.py` or `app.py`) with your provider’s details.

---

## 🚀 Quickstart

Clone the repository:

```bash
git clone https://github.com/darshanbalajitd/website-summarising-agent.git
cd website-summarising-agent
```

Install dependencies:

```bash
pip install -r requirements.txt
playwright install
```

Run the app:

```bash
streamlit run app.py
```

---

## 💡 Usage Tips

- Works best with **static websites** that do not use heavy protection layers.  
- Avoid sites behind:
  - Cloudflare or Google Captcha  
  - Paywalls  
- Works well on:
  - Wikipedia  
  - News websites  
  - Informational blogs  

Enter a URL → The agent scrapes text & images → AI generates a structured summary → You can ask follow-up questions in chat.  

---

## 📌 Repository

[GitHub Repo](https://github.com/darshanbalajitd/website-summarising-agent)
