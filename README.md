# dbt Certification Mentor

A Streamlit chat app that helps you prepare for the dbt Certified Developer exam. It searches the official study guide (vector store) and the web (dbt docs, best practices, Learn) to answer your questions with cited sources.

**Repo:** [github.com/phphoebe/dbt-certification-mentor](https://github.com/phphoebe/dbt-certification-mentor) · MIT License

## Setup

### 1. Create a Vector Store and Upload the Study Guide

The app expects a pre-configured OpenAI vector store containing the dbt study guide PDF.

**Option A: Using the setup script (recommended)**

1. Download the official study guide PDF from [dbt Learn](https://learn.getdbt.com/learn/article/analytics-engineering-exam-study-guide)
2. Place it in `study_guide/` in this project
3. Run:

```bash
# Add OPENAI_API_KEY to .env first
uv run python setup_vector_store.py "study_guide/dbt_Certificate Study Guide_Analytics_Engineer_Developer.pdf"
```

(Adjust the filename if yours differs after downloading.)

Copy the printed `vector_store_id` into your `.env` file.

**Option B: Using OpenAI Platform**

1. Go to [OpenAI Platform → Storage → Vector Stores](https://platform.openai.com/storage)
2. Create a new vector store and upload the study guide PDF
3. Copy the vector store ID

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY and vector_store_id
```

### 3. Run the App

```bash
uv run streamlit run app.py
```

Opens at http://localhost:8501

## Features

- **File Search:** Semantic search over the study guide PDF
- **Web Search:** Searches dbt docs, best practices, Learn, and community resources
- **Toggle controls:** Enable/disable each search source per session
- **Conversation memory:** Follow-up questions work naturally

## Example Questions

- What topics are covered on the dbt Certified Developer exam?
- Explain `ref()` and how it affects model execution order
- What are best practices for **incremental** models?
- How do I configure **tests** for a model?
- Suggest a study plan for the certification

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for visual flowcharts (Mermaid) showing how components work together — similar to no-code workflow diagrams.

## Project Structure

```
dbt-mentor-agent/
├── docs/
│   └── ARCHITECTURE.md   # Visual flowcharts (Mermaid)
├── app.py                # Streamlit + agent logic
├── prompt.txt            # System prompt (dbt mentor persona)
├── setup_vector_store.py # One-time script to create vector store
├── pyproject.toml
├── .env.example          # Copy to .env and fill in
└── README.md
```
