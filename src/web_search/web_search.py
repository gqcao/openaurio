# /// script
# dependencies = ["ddgs", "requests", "typing_extensions"]
# ///

import requests
import argparse
import json
import os

def simple_web_search(
        query: str,
        region: str = "us-en",
        timelimit: str | None = None,
        max_results: int = 20,
    ) -> str:
    """Web search by Dux Distributed Global Search.

    A metasearch library that aggregates results from diverse web search services. The retrieved results are presented in simple sentences.

    Args:
        query: The query terms or sentences
        region: us-en, cn-zh (for Chinese search in mainland China), etc. Defaults to us-en
        timelimit: d, w, m, y. It searches the results in the last day, week, month, or year, respectively. Defaults to None.
        max_result: The number of results to be retrieved.

    Return:
        response: List of dictionaries with search results.
    """
    from ddgs import DDGS
    return DDGS().text(query, region=region, timelimit=timelimit, max_results=max_results)

# Define LangSearch Web Search tool
def semantic_web_search(query: str, freshness: str = "noLimit", count: int = 10) -> str:
    """
    Perform web search using LangSearch Web Search API.

    Parameters:
    - query: Search keywords
    - freshness: Search time range, e.g., "oneDay", "oneWeek", "oneMonth", "oneYear", "noLimit"
    - count: Number of search results to return

    Returns:
    - Detailed information of search results, including web page title, web page URL, web page content, web page publication time, etc.
    """

    url = "https://api.langsearch.com/v1/web-search"
    api_key = os.environ.get("LANGSEARCH_API_KEY", "")
    if not api_key:
        return "Error: LANGSEARCH_API_KEY environment variable not set. Please set it to use advanced search."
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "query": query,
        "freshness": freshness,  # Search time range, e.g., "oneDay", "oneWeek", "oneMonth", "oneYear", "noLimit"
        "summary": True,          # Whether to return a long text summary
        "count": count
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        json_response = response.json()
        try:
            if json_response["code"] != 200 or not json_response["data"]:
                return f"Search API request failed, reason: {response.msg or 'Unknown error'}"

            webpages = json_response["data"]["webPages"]["value"]
            if not webpages:
                return "No relevant results found."
            formatted_results = ""
            for idx, page in enumerate(webpages, start=1):
                formatted_results += (
                    f"Citation: {idx}\n"
                    f"Title: {page['name']}\n"
                    f"URL: {page['url']}\n"
                    f"Content: {page['summary']}\n"
                )
            return formatted_results.strip()
        except Exception as e:
            return f"Search API request failed, reason: Failed to parse search results {str(e)}"
    else:
        return f"Search API request failed, status code: {response.status_code}, error message: {response.text}"

def web_search(query: str, freshness: str = "noLimit", search_depth: str ="basic"):
    """
    Perform web search using either ddgs or langsearch.

    Parameters:
    - query: Search keywords
    - freshness: Search time range, e.g., "oneDay", "oneWeek", "oneMonth", "oneYear", "noLimit"
    - search_depth: Depth of the search. "basic" for simple queries, or "advanced" for in-depth analysis.

    Returns:
    - response: List of dictionaries with search results.
    """
    if search_depth == "basic":
        map_freshness_to_timelimit = {"oneDay": "d", "oneWeek": "w", "oneMonth": "m", "oneYear": "y", "noLimit": None}
        timelimit = map_freshness_to_timelimit[freshness]
        return simple_web_search(query, timelimit=timelimit)
    else:
        return semantic_web_search(query, freshness=freshness)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Perform web searches using DuckDuckGo (basic) or LangSearch API (advanced)."
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        required=True,
        help="Search query terms"
    )
    parser.add_argument(
        "--depth", "-d",
        type=str,
        choices=["basic", "advanced"],
        default="basic",
        help="Search depth: 'basic' for DuckDuckGo, 'advanced' for LangSearch API"
    )
    parser.add_argument(
        "--freshness", "-f",
        type=str,
        choices=["oneDay", "oneWeek", "oneMonth", "oneYear", "noLimit"],
        default="noLimit",
        help="Time range for search results"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Get LangSearch API key from environment if using advanced search
    if args.depth == "advanced":
        os.environ.setdefault("LANGSEARCH_API_KEY", "")

    try:
        results = web_search(
            query=args.query,
            freshness=args.freshness,
            search_depth=args.depth
        )

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            if isinstance(results, list):
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result.get('title', 'N/A')}")
                    print(f"   URL: {result.get('href', 'N/A')}")
                    print(f"   {result.get('body', 'N/A')[:200]}...\n")
            else:
                print(results)
    except Exception as e:
        print(f"Error: {e}", file=__import__('sys').stderr)
        __import__('sys').exit(1)
