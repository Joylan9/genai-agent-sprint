# app/tools/web_search_tool.py

import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any

from app.tools.tools import BaseTool

load_dotenv()


class WebSearchTool(BaseTool):

    name = "web_search"

    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")

        if not self.api_key:
            raise ValueError("SERPAPI_KEY not found in environment variables.")

        self.base_url = "https://serpapi.com/search.json"

    def search(self, query: str, num_results: int = 3):

        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
            "num": num_results
        }

        response = requests.get(self.base_url, params=params, timeout=10)

        if response.status_code != 200:
            return f"Search API error: {response.status_code}"

        data = response.json()

        results = []

        for item in data.get("organic_results", [])[:num_results]:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            results.append(f"{title}\n{snippet}\nSource: {link}")

        if not results:
            return "No relevant web results found."

        return "\n\n".join(results)

    def execute(self, step: Dict[str, Any]) -> Dict[str, Any]:

        raw_query = step.get("query")

        if not isinstance(raw_query, str) or not raw_query.strip():
            return {
                "status": "error",
                "data": None,
                "metadata": {"error": "Invalid or missing query string."}
            }

        query: str = raw_query.strip()

        try:
            result = self.search(query)

            return {
                "status": "success",
                "data": result,
                "metadata": {}
            }

        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "metadata": {"error": str(e)}
            }
