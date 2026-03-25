import asyncio
import base64
import os

import streamlit as st
from dotenv import load_dotenv
from openai import NotFoundError

# Local dev: .env. Streamlit Community Cloud: Advanced settings → Secrets (TOML).
load_dotenv(override=False)

st.set_page_config(page_title="dbt Certification Mentor", layout="wide")


def _config_value(key: str) -> str | None:
    v = os.environ.get(key)
    if v:
        return v
    try:
        if key in st.secrets:
            return st.secrets[key]
    except (FileNotFoundError, KeyError, RuntimeError, TypeError):
        pass
    return None


OPENAI_API_KEY = _config_value("OPENAI_API_KEY")
vector_store_id = _config_value("vector_store_id")
# Explicit chat model (Responses API). Default matches Agents SDK default; override if your key 404s.
_raw_model = _config_value("OPENAI_AGENT_MODEL") or os.getenv("OPENAI_AGENT_MODEL") or "gpt-4.1"
AGENT_MODEL = _raw_model.strip()
# The Agents SDK uses os.environ["OPENAI_DEFAULT_MODEL"] whenever agent.model is None. Streamlit or
# copied secrets sometimes set that var to an invalid internal id (e.g. o4m-sonic-o-api-ev3) → 404.
os.environ["OPENAI_DEFAULT_MODEL"] = AGENT_MODEL
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# SDK reads OPENAI_API_KEY from the environment at client creation time.
from agents import Agent, FileSearchTool, Runner, WebSearchTool  # noqa: E402
from agents.model_settings import ModelSettings  # noqa: E402

CONFIG_OK = bool(OPENAI_API_KEY and vector_store_id)

_APP_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(_APP_DIR, "assets", "dbt.svg")

# Load system prompt from file
PROMPT_PATH = os.path.join(_APP_DIR, "prompt.txt")
with open(PROMPT_PATH, "r") as f:
    SYSTEM_PROMPT = f.read()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "use_web_search" not in st.session_state:
    st.session_state.use_web_search = True
if "use_file_search" not in st.session_state:
    st.session_state.use_file_search = True


def create_mentor_agent():
    """Create agent with selected tools."""
    tools = []
    if st.session_state.use_web_search:
        tools.append(WebSearchTool())
    if st.session_state.use_file_search:
        tools.append(
            FileSearchTool(
                max_num_results=3,
                vector_store_ids=[vector_store_id],
            )
        )
    return Agent(
        name="dbt Certification Mentor",
        instructions=SYSTEM_PROMPT,
        tools=tools,
        model=AGENT_MODEL,
        model_settings=ModelSettings(),
    )


def _svg_data_uri(svg_path: str) -> str:
    with open(svg_path, "rb") as f:
        b64 = base64.standard_b64encode(f.read()).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


async def get_mentor_response(question: str, history: list[dict]) -> str:
    """Run agent with conversation context."""
    agent = create_mentor_agent()
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    prompt = f"Context of our conversation:\n{context}\n\nCurrent question: {question}"
    try:
        result = await Runner.run(agent, prompt)
    except NotFoundError as exc:
        err_s = str(exc)
        model_hint = ""
        if "model" in err_s.lower() and "not found" in err_s.lower():
            model_hint = (
                "- **Wrong model id:** Remove **`OPENAI_DEFAULT_MODEL`** from Streamlit secrets (or set it to "
                f"`{AGENT_MODEL}`). The Agents SDK uses that env var when no model is set; a stray value like "
                "`o4m-sonic-o-api-ev3` causes this error.\n"
            )
        return (
            "**Something was not found on OpenAI** (HTTP 404). Typical causes:\n\n"
            + model_hint
            + "- **`vector_store_id`** must belong to the **same** OpenAI organization as **`OPENAI_API_KEY`** "
            "(recreate the store with this key or copy the correct `vs_…` ID from "
            "[Vector stores](https://platform.openai.com/storage/vector_stores)).\n"
            "- **Model** not enabled for your key; set **`OPENAI_AGENT_MODEL`** (e.g. `gpt-4o` if `gpt-4.1` fails). "
            f"**Currently:** `{AGENT_MODEL}`.\n\n"
            f"_Details: {exc!s}_"
        )
    return result.final_output


# --- Streamlit UI ---
# Flex header avoids extra gutter from st.columns; title size between default h1 and h2.
_logo_uri = _svg_data_uri(LOGO_PATH)
st.markdown(
    f"""
    <div style="display:flex;align-items:center;gap:0.5rem;margin:0 0 0.35rem 0;">
        <img src="{_logo_uri}" width="32" height="32" alt=""
            style="flex-shrink:0;display:block;margin:0;padding:0;" />
        <span style="font-size:1.45rem;font-weight:600;line-height:1.25;margin:0;color:var(--text-color, inherit);">dbt Certification Mentor</span>
    </div>
    """,
    unsafe_allow_html=True,
)
if not CONFIG_OK:
    st.error(
        "Missing **OPENAI_API_KEY** or **vector_store_id**. "
        "Locally: copy `.env.example` → `.env` and fill both. "
        "On Streamlit Community Cloud: App settings → Secrets (TOML keys OPENAI_API_KEY, vector_store_id)."
    )
    st.stop()
st.write(
    "Ask exam-prep questions. I search the study guide and dbt docs to help you prepare."
)

# Sidebar
st.sidebar.title("Search Settings")
st.sidebar.subheader("Select Search Sources")
web_search = st.sidebar.checkbox(
    "Web Search", value=st.session_state.use_web_search, key="web_search_toggle"
)
file_search = st.sidebar.checkbox(
    "Study Guide (Vector Store)",
    value=st.session_state.use_file_search,
    key="file_search_toggle",
)

if web_search != st.session_state.use_web_search:
    st.session_state.use_web_search = web_search
if file_search != st.session_state.use_file_search:
    st.session_state.use_file_search = file_search

if not st.session_state.use_web_search and not st.session_state.use_file_search:
    st.sidebar.warning("Please select at least one search source")

st.sidebar.subheader("Conversation")
if st.sidebar.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()

with st.sidebar.expander("Example Questions"):
    st.markdown("""
    - What topics are covered on the dbt Certified Developer exam?
    - Compare snapshots vs incremental models for slowly changing dimensions
    - What are best practices for incremental models?
    - How do I configure tests for a model?
    - Suggest a study plan for the certification
    """)

st.sidebar.markdown("---")
st.sidebar.markdown("🐰 Made by Pheebs")

# Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_question = st.chat_input("Ask your dbt certification question")

if user_question:
    if not st.session_state.use_web_search and not st.session_state.use_file_search:
        st.error("Please select at least one search source in the sidebar")
    else:
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)
        with st.chat_message("assistant"):
            with st.spinner("Searching study guide and docs..."):
                response = asyncio.run(
                    get_mentor_response(user_question, st.session_state.messages)
                )
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
