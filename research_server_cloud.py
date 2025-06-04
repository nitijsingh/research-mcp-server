import arxiv
import json
import os
from typing import List
from fastmcp import FastMCP

PAPER_DIR = "papers"

# Get port from environment variable (for cloud deployment) or default to 10000
PORT = int(os.environ.get('PORT', 10000))

# Initialize FastMCP server with dynamic port for cloud deployment
mcp = FastMCP("research", port=PORT)

@mcp.tool()
def search_papers(topic: str, max_results: int = 5) -> str:
    """Search for academic papers on arXiv"""
    try:
        # Create papers directory if it doesn't exist
        os.makedirs(PAPER_DIR, exist_ok=True)
        
        search = arxiv.Search(
            query=topic,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        papers = []
        for paper in search.results():
            paper_info = {
                "title": paper.title,
                "authors": [str(author) for author in paper.authors],
                "abstract": paper.summary,
                "published": paper.published.strftime('%Y-%m-%d'),
                "url": paper.pdf_url,
                "categories": paper.categories
            }
            papers.append(paper_info)
            
            # Save paper info to file
            filename = f"{PAPER_DIR}/{paper.get_short_id()}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(paper_info, f, indent=2, ensure_ascii=False)
        
        return f"Found {len(papers)} papers on '{topic}'. Papers saved to {PAPER_DIR}/ directory."
    
    except Exception as e:
        return f"Error searching papers: {str(e)}"

@mcp.tool()
def extract_info(paper_id: str, info_type: str = "summary") -> str:
    """Extract specific information from a downloaded paper"""
    try:
        filename = f"{PAPER_DIR}/{paper_id}.json"
        
        if not os.path.exists(filename):
            return f"Paper {paper_id} not found. Please search for papers first."
        
        with open(filename, 'r', encoding='utf-8') as f:
            paper = json.load(f)
        
        if info_type == "summary":
            return f"Title: {paper['title']}\nAuthors: {', '.join(paper['authors'])}\nAbstract: {paper['abstract']}"
        elif info_type == "authors":
            return f"Authors: {', '.join(paper['authors'])}"
        elif info_type == "abstract":
            return paper['abstract']
        elif info_type == "url":
            return paper['url']
        else:
            return f"Available info types: summary, authors, abstract, url"
    
    except Exception as e:
        return f"Error extracting info: {str(e)}"

@mcp.resource("papers://folders")
def list_paper_folders() -> str:
    """List all downloaded paper folders"""
    try:
        if not os.path.exists(PAPER_DIR):
            return "No papers directory found. Search for papers first."
        
        files = os.listdir(PAPER_DIR)
        json_files = [f for f in files if f.endswith('.json')]
        
        if not json_files:
            return "No papers found. Search for papers first."
        
        return f"Found {len(json_files)} papers: {', '.join(json_files)}"
    
    except Exception as e:
        return f"Error listing papers: {str(e)}"

@mcp.prompt("generate_search_prompt")
def create_search_prompt(topic: str) -> str:
    """Generate a research prompt for a given topic"""
    return f"""
Research Prompt for: {topic}

1. Search Strategy:
   - Primary keywords: {topic}
   - Related terms to explore
   - Timeline considerations

2. Key Questions to Investigate:
   - What are the current developments in {topic}?
   - Who are the leading researchers?
   - What are the main challenges?
   - What are the recent breakthroughs?

3. Analysis Framework:
   - Compare different approaches
   - Identify trends and patterns
   - Note controversial areas
   - Find gaps in current research

4. Output Goals:
   - Summarize key findings
   - Identify most influential papers
   - Create research roadmap
   - Suggest future directions
"""

if __name__ == "__main__":
    print(f"🚀 Starting Research MCP Server on port {PORT}")
    print(f"🌐 Server will be accessible via SSE transport")
    print(f"📡 Connect via: http://localhost:{PORT}/sse (local) or your cloud URL")
    
    # Run server with SSE transport for remote access
    # Bind to 0.0.0.0 for cloud deployment accessibility
    mcp.run(transport="sse", host="0.0.0.0", port=PORT)
