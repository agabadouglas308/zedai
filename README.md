# ZedAI — AI Web Research Agent

A LangGraph ReAct agent that searches the web with DuckDuckGo, scrapes the pages it finds, and synthesizes an answer. Model calls go through [OpenRouter](https://openrouter.ai), so you can swap between OpenAI, Anthropic, Google, Meta, and others without changing code.

## Features

- **ReAct agent loop** built on LangGraph — plans, calls tools, observes results, repeats until it has an answer.
- **DuckDuckGo search tool** — finds relevant URLs and snippets. No API key required.
- **Website scraper tool** — fetches a URL and extracts readable text (scripts and styles stripped, truncated to 8,000 chars to fit the model's context window).
- **OpenRouter backend** — one API key, many models. Change a single string to switch providers.
- **Interactive CLI** — type a question, get an answer; type `exit` or `quit` to stop.

## Requirements

- Python 3.11 or 3.12 recommended (3.13+ may work; some dependencies lag behind the newest releases)
- An [OpenRouter account](https://openrouter.ai) and API key

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/agabadouglas308/zedai.git
cd zedai
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install requests beautifulsoup4 langchain langchain-openai langgraph ddgs
```

### 4. Get an OpenRouter API key

1. Sign in at https://openrouter.ai
2. Go to https://openrouter.ai/settings/keys
3. Click **Create Key**, copy the value (it starts with `sk-or-v1-`)

### 5. Export the key

**Linux / macOS:**

```bash
export OPENROUTER_API_KEY='sk-or-v1-...your-key...'
```

**Windows PowerShell:**

```powershell
$env:OPENROUTER_API_KEY="sk-or-v1-...your-key..."
```

To make it permanent, add the `export` line to `~/.bashrc` (or `~/.zshrc`) and run `source ~/.bashrc`.

> The agent reads the key from the environment at runtime. It is never written to disk or committed to the repo.

## Usage

```bash
python backend/agent.py
```

You'll see:

```
--- AI Web Research Agent ---
Type 'exit' to quit.

Enter your command:
```

Try a prompt like:

```
What are the best universities in the world right now?
Compare the pricing of the top 3 cloud providers.
Summarize the latest Python release notes.
```

The agent will decide when to search, when to scrape, and when it has enough to answer. The final response is printed between `--- FINAL RESULT ---` banners.

Type `exit` or `quit` to stop.

## Project structure

```
.
├── README.md
├── .gitignore
├── app.py                 # alternate entry point
└── backend/
    └── agent.py           # agent definition + CLI loop
```

## Configuration

To change the model, edit the `ChatOpenAI` block in `backend/agent.py`:

```python
llm = ChatOpenAI(
    temperature=0,
    model="openai/gpt-4o-mini",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
```

Set `model` to any slug from https://openrouter.ai/models. Examples:

| Model | Slug |
|---|---|
| OpenAI GPT-4o mini | `openai/gpt-4o-mini` |
| Anthropic Claude 3.5 Sonnet | `anthropic/claude-3.5-sonnet` |
| Google Gemini 2.0 Flash | `google/gemini-2.0-flash` |
| Meta Llama 3.3 70B | `meta-llama/llama-3.3-70b-instruct` |

The `base_url` line is what points the client at OpenRouter instead of OpenAI's servers. Removing it will cause a 401 — the two services don't accept each other's keys.

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `401 Incorrect API key provided: sk-or-v1...` | Request went to OpenAI with an OpenRouter key | Add `base_url="https://openrouter.ai/api/v1"` to `ChatOpenAI` |
| `401 Missing Authentication header` | `OPENROUTER_API_KEY` is empty in the current shell | Re-run the `export` command; verify with `echo $OPENROUTER_API_KEY` |
| `401 User not found` | Key was revoked or belongs to a deleted account | Generate a new key at https://openrouter.ai/settings/keys |
| `ModuleNotFoundError: No module named 'requests'` | venv not activated, or deps not installed | `source .venv/bin/activate` then `pip install ...` |
| `LangGraphDeprecatedSinceV10: create_react_agent has been moved` | LangGraph V1.0 deprecation warning | Harmless for now; migrate to `from langchain.agents import create_agent` when ready |

## Security

- API keys are read from environment variables only.
- `.gitignore` excludes `.env`, `.venv/`, and `__pycache__/`.
- GitHub push protection is enabled on this repo and will reject any commit containing a key.

If you ever commit a key by accident: revoke it at OpenRouter immediately, create a replacement, then rewrite history with `git filter-repo` or `git commit --amend` before pushing.

## License

MIT — see `LICENSE`
