import os

import requests
from bs4 import BeautifulSoup
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Set your OpenRouter API key without overwriting an environment value that may already exist.
os.environ.setdefault(
    "OPENROUTER_API_KEY",
    "openrouter key here", #replace with real key
)


def duckduckgo_search(query: str) -> str:
    """Search the web and return concise text results."""
    try:
        from ddgs import DDGS

        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)

        formatted_results = []
        for item in results:
            title = item.get("title", "")
            link = item.get("href", "")
            snippet = item.get("body", "")
            if title or link or snippet:
                formatted_results.append(f"{title}\n{link}\n{snippet}")

        return "\n\n".join(formatted_results) if formatted_results else "No search results found."
    except Exception as exc:
        return f"Search failed: {exc}"


# 1. Search Tool
search_tool = Tool(
    name="DuckDuckGo_Search",
    func=duckduckgo_search,
    description="Useful for finding URLs and general information on the internet. Input should be a search query.",
)


# 2. Scraping Tool
def scrape_website(url: str) -> str:
    """Scrapes the text content of a given URL."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text(separator=" ", strip=True)

        # Truncate text to avoid overwhelming the LLM context window
        return text[:8000]
    except Exception as exc:
        return f"Error scraping {url}: {exc}"


scrape_tool = Tool(
    name="Website_Scraper",
    func=scrape_website,
    description="Useful for scraping the text content of a specific URL. Input must be a valid URL.",
)


# Initialize the LLM via OpenRouter (OpenAI-compatible endpoint).
llm = ChatOpenAI(
    temperature=0,
    model="openai/gpt-4o-mini",  # OpenRouter model slug
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

# Modern LangChain/LangGraph agent API
agent = create_react_agent(model=llm, tools=[search_tool, scrape_tool])


def command_centre():
    print("--- AI Web Research Agent ---")
    print("Type 'exit' to quit.\n")

    while True:
        user_command = input("Enter your command: ")

        if user_command.lower() in ["exit", "quit"]:
            break

        if not user_command.strip():
            continue

        try:
            # The agent will plan, search, scrape, and synthesize.
            result = agent.invoke({"messages": [("user", user_command)]})
            messages = result.get("messages", [])
            final_message = messages[-1] if messages else None
            output = final_message.content if final_message is not None else str(result)
            print("\n--- FINAL RESULT ---")
            print(output)
            print("--------------------\n")
        except Exception as exc:
            print(f"An error occurred: {exc}\n")


if __name__ == "__main__":
    command_centre()