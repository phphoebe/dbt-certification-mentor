# Architecture: dbt Certification Mentor Agent

Visual flow of how components work together — similar to no-code workflow diagrams (e.g. n8n).

---

## Main Flow: From Question to Answer

```mermaid
flowchart TB
    subgraph UI["🖥️ Streamlit UI"]
        A[User types question]
        B[Chat input]
        C[Display response]
    end

    subgraph Memory["📦 Memory"]
        D["st.session_state.messages<br/>(chat history)"]
    end

    subgraph AppLogic["⚙️ App Logic (app.py)"]
        E["get_mentor_response()<br/>Builds context from history"]
        F["create_mentor_agent()<br/>Assembles Agent + Tools"]
    end

    subgraph Agent["🧠 Agent (OpenAI)"]
        G["Receives: prompt.txt + context + question"]
        H["Decides which tools to call"]
        I["Synthesizes response from tool results"]
    end

    subgraph Tools["🔧 Tools"]
        J["FileSearchTool<br/>→ Vector store (study guide)"]
        K["WebSearchTool<br/>→ Web (docs, Learn)"]
    end

    A --> B
    B --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> J
    H --> K
    J --> I
    K --> I
    I --> D
    D --> C
```

---

## Data Flow: Context & Memory

```mermaid
flowchart LR
    subgraph EachTurn["Each user message"]
        A["user: ..."]
        B["assistant: ..."]
        C["user: ..."]
    end

    subgraph Storage["Storage"]
        D["st.session_state.messages<br/>list of role/content dicts"]
    end

    subgraph ToAgent["Passed to Agent"]
        E["Context string:<br/>user: ... assistant: ...<br/>Current question: ..."]
    end

    A --> D
    B --> D
    C --> D
    D --> E
```

---

## Tool Selection (User Toggles)

```mermaid
flowchart TB
    subgraph Sidebar["Sidebar toggles"]
        T1["☑️ Web Search"]
        T2["☑️ Study Guide"]
    end

    subgraph SessionState["Session state"]
        S1["use_web_search"]
        S2["use_file_search"]
    end

    subgraph Tools["Tools passed to Agent"]
        W["WebSearchTool"]
        F["FileSearchTool"]
    end

    T1 --> S1
    T2 --> S2
    S1 -->|if true| W
    S2 -->|if true| F
    W --> Agent["Agent receives only<br/>enabled tools"]
    F --> Agent
```

---

## Setup: Vector Store & .env

```mermaid
flowchart LR
    subgraph OneTime["One-time setup"]
        A["Download study guide PDF"]
        B["Run setup_vector_store.py"]
        C["OpenAI creates vector store"]
        D["Upload PDF → embeddings"]
        E["Print vector_store_id"]
    end

    subgraph Persistent["Persists"]
        F[".env file<br/>OPENAI_API_KEY<br/>vector_store_id"]
        G["Vector store in<br/>OpenAI account"]
    end

    subgraph Runtime["Each app run"]
        H["app.py loads .env"]
        I["FileSearchTool uses<br/>vector_store_id"]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> H
    G --> I
    H --> I
```

---

## File Map

| File | Role |
|------|------|
| `app.py` | Streamlit UI, session state, agent orchestration |
| `prompt.txt` | System prompt (agent instructions) |
| `setup_vector_store.py` | One-time: create vector store, upload PDF |
| `.env` | Secrets: API key, vector_store_id |
