# Architecture: dbt Certification Mentor Agent

Visual flow of how components work together — similar to no-code workflow diagrams (e.g. n8n).

---

## Main Flow: From Question to Answer

```mermaid
flowchart TB
    subgraph Step1["1. User Input"]
        A[User types question]
    end

    subgraph Step2["2. Memory"]
        B["Append to st.session_state.messages"]
    end

    subgraph Step3["3. App Logic (app.py)"]
        C["get_mentor_response: build context from history"]
        D["create_mentor_agent: assemble Agent + Tools"]
    end

    subgraph Step4["4. Agent (OpenAI)"]
        E["Receives prompt.txt + context + question"]
        F["Decides which tools to call"]
    end

    subgraph Step5["5. Tools"]
        G["FileSearchTool<br/>Vector store"]
        H["WebSearchTool<br/>Web / docs"]
    end

    subgraph Step6["6. Response"]
        I["Synthesize from tool results"]
        J["Append response & display"]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    F --> H
    G --> I
    H --> I
    I --> J
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
