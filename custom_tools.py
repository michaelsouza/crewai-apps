from crewai_tools import BaseTool
import requests
import urllib.parse

class ArXivAPITool(BaseTool):
    name = "ArXiv API Tool"
    description = "Fetches paper metadata from the ArXiv API based on complex search queries."

    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query?"

    def _construct_query(self, search_params):
        # Constructing the query part of the URL based on search_params
        # search_params is expected to be a dictionary where keys are metadata fields
        # and values are the search terms for those fields
        query_parts = []
        for field, term in search_params.items():
            query_parts.append(f"{field}:{urllib.parse.quote(term)}")
        return " AND ".join(query_parts)

    def _run(self, search_params: dict) -> str:
        query = self._construct_query(search_params)
        url = f"{self.base_url}search_query={query}&max_results=10"
        try:
            response = requests.get(url)
            response.raise_for_status()
            entries = response.json()['feed']['entry']
            results = []
            for entry in entries:
                paper_metadata = {
                    'title': entry['title'],
                    'authors': [author['name'] for author in entry['author']],
                    'abstract': entry['summary'],
                    'year': entry['published'][:4]
                }
                results.append(paper_metadata)
            return str(results)
        except requests.RequestException as e:
            return f"Failed to fetch data from ArXiv: {str(e)}"

if __name__ == "__main__":
    # Example usage
    arxiv_tool = ArXivAPITool()
    search_params = {"author": "Einstein", "title": "quantum"}
    print(arxiv_tool._run(search_params))
