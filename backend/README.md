# Medintel – Day 1 Setup

This project is a RAG-based medical information assistant.

## Day 1 Progress

* GitHub repo created
* SSH setup completed
* Project cloned into PyCharm
* Initial folder structure planned

## How to run (Day 1)

1. **Create a virtual environment**

   * Windows:

     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   * Linux/macOS:

     ```bash
     python -m venv venv
     source venv/bin/activate
     ```

2. **Install dependencies**

   * If you have a `requirements.txt` file:

     ```bash
     pip install -r requirements.txt
     ```
   * Or install individually (example):

     ```bash
     pip install streamlit requests fastapi
     ```

3. **Run the project**

   * For Streamlit apps:

     ```bash
     streamlit run app.py
     ```
   * For FastAPI backend:

     ```bash
     uvicorn main:app --reload
     ```
