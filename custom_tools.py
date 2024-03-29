from crewai_tools import BaseTool
import requests
import xml.etree.ElementTree as ET  # Import missing in original code

class ArXivAPITool(BaseTool):
    name: str = "ArXiv API Tool"
    description: str = "Fetches paper metadata from the ArXiv API based on complex search queries."
    base_url: str = "http://export.arxiv.org/api/query?"

    def _run(self, search_query: str, max_results: int=5) -> str:
        # Directly use the search_query in the URL
        url = f"{self.base_url}search_query={search_query}&max_results={max_results}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse the XML response
            root = ET.fromstring(response.content)
            results = []
            for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                title = entry.find('.//{http://www.w3.org/2005/Atom}title').text
                published = entry.find('.//{http://www.w3.org/2005/Atom}published').text[:4]  # Extract the year
                summary = entry.find('.//{http://www.w3.org/2005/Atom}summary').text
                
                authors = [author.find('.//{http://www.w3.org/2005/Atom}name').text for author in entry.findall('.//{http://www.w3.org/2005/Atom}author')]
                
                paper_metadata = {
                    'title': title.strip(),
                    'authors': authors,
                    'abstract': summary.strip(),
                    'year': published
                }
                results.append(paper_metadata)
                
            return str(results)
        
        except requests.RequestException as e:
            return f"Failed to fetch data from ArXiv: {str(e)}"
        except ET.ParseError:
            return "Failed to parse XML response from ArXiv"

if __name__ == "__main__":
    arxiv_tool = ArXivAPITool()

    # Queries are now passed directly as strings
    query_examples = [
        # 'au:"Stephen Hawking"',
        # 'ti:"Black Hole Information Paradox"',
        # 'au:"Leonard Susskind" AND abs:"quantum entanglement"',
        # 'cat:quant-ph',
        # 'au:"Edward Witten" OR au:"Juan Maldacena"',
        # 'abs:"dark energy" ANDNOT abs:"cosmological constant"',
        # 'submittedDate:[20200101 TO 20201231]',
        # 'abs:"neural networks" AND cat:cs.LG',
        # 'ti:"machine learning" OR abs:"deep learning"',
        # '(au:"Albert Einstein" AND ti:"General Relativity") OR (abs:"spacetime" AND cat:gr-qc)',
        "abs:\"history of AI\" AND (submittedDate:[20200101 TO 20240329])",
    ]

    # Iterate over the query examples and execute them
    for i, query in enumerate(query_examples, start=1):
        print(f"Query {i}:{query}")
        print(arxiv_tool._run(query))
        print("-" * 40)  # Separator for readability
