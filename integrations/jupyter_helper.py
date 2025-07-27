"""Jupyter helper functions for arXiv research analysis."""

import asyncio
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import networkx as nx
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ArxivResearchHelper:
    """Helper class for Jupyter notebook analysis of arXiv research."""
    
    def __init__(self):
        """Initialize the research helper."""
        self.papers_data = []
        self.search_history = []
    
    async def search_and_analyze(self, query: str, max_results: int = 10, 
                                years_back: int = 4, include_full_text: bool = True) -> Dict:
        """Search arXiv and return analysis-ready data."""
        
        try:
            # Import here to avoid circular imports
            from src.server import search_arxiv_papers_tool
            
            arguments = {
                "query": query,
                "max_results": max_results,
                "years_back": years_back,
                "include_full_text": include_full_text
            }
            
            result = await search_arxiv_papers_tool(arguments)
            
            if result and len(result) > 0:
                # Parse the results and extract structured data
                papers_data = self._parse_search_results(result[0].text)
                self.papers_data.extend(papers_data)
                self.search_history.append({
                    "query": query,
                    "results_count": len(papers_data),
                    "timestamp": pd.Timestamp.now()
                })
                
                return {
                    "papers": papers_data,
                    "query": query,
                    "total_papers": len(papers_data)
                }
            else:
                return {"papers": [], "query": query, "total_papers": 0}
                
        except Exception as e:
            logger.error(f"Error in search_and_analyze: {e}")
            return {"papers": [], "query": query, "error": str(e)}
    
    def _parse_search_results(self, results_text: str) -> List[Dict]:
        """Parse search results text into structured data."""
        papers = []
        
        # Simple parsing - in a real implementation, you'd want more robust parsing
        sections = results_text.split("## Paper")
        
        for section in sections[1:]:  # Skip the header
            try:
                paper_data = self._extract_paper_data(section)
                if paper_data:
                    papers.append(paper_data)
            except Exception as e:
                logger.warning(f"Error parsing paper section: {e}")
                continue
        
        return papers
    
    def _extract_paper_data(self, section: str) -> Optional[Dict]:
        """Extract paper data from a section."""
        try:
            lines = section.strip().split('\n')
            
            # Extract title (first line after ## Paper X:)
            title = ""
            for line in lines:
                if line.strip() and not line.startswith('**'):
                    title = line.strip()
                    break
            
            # Extract other fields using simple patterns
            authors = self._extract_field(section, r'\*\*Authors:\*\* (.*)')
            published = self._extract_field(section, r'\*\*Published:\*\* (.*)')
            arxiv_id = self._extract_field(section, r'\*\*arXiv ID:\*\* (.*)')
            categories = self._extract_field(section, r'\*\*Categories:\*\* (.*)')
            relevance_score = self._extract_field(section, r'\*\*Relevance Score:\*\* (.*)')
            url = self._extract_field(section, r'\*\*URL:\*\* (.*)')
            
            # Extract abstract
            abstract_start = section.find('**Abstract:**')
            abstract_end = section.find('**', abstract_start + 1)
            abstract = ""
            if abstract_start != -1 and abstract_end != -1:
                abstract = section[abstract_start + 12:abstract_end].strip()
            
            return {
                "title": title,
                "authors": authors,
                "published": published,
                "arxiv_id": arxiv_id,
                "categories": categories,
                "relevance_score": float(relevance_score) if relevance_score != "N/A" else 0.0,
                "url": url,
                "abstract": abstract
            }
            
        except Exception as e:
            logger.warning(f"Error extracting paper data: {e}")
            return None
    
    def _extract_field(self, text: str, pattern: str) -> str:
        """Extract a field using regex pattern."""
        import re
        match = re.search(pattern, text)
        return match.group(1) if match else "Unknown"
    
    def create_publication_timeline(self, figsize: tuple = (12, 6)) -> plt.Figure:
        """Create a publication timeline visualization."""
        if not self.papers_data:
            return None
        
        df = pd.DataFrame(self.papers_data)
        
        # Extract year from published date
        df['year'] = pd.to_datetime(df['published'], errors='coerce').dt.year
        
        plt.figure(figsize=figsize)
        year_counts = df['year'].value_counts().sort_index()
        
        plt.bar(year_counts.index, year_counts.values)
        plt.title('Publications by Year')
        plt.xlabel('Year')
        plt.ylabel('Number of Papers')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return plt.gcf()
    
    def create_relevance_distribution(self, figsize: tuple = (10, 6)) -> plt.Figure:
        """Create relevance score distribution."""
        if not self.papers_data:
            return None
        
        df = pd.DataFrame(self.papers_data)
        
        plt.figure(figsize=figsize)
        plt.hist(df['relevance_score'], bins=20, alpha=0.7, edgecolor='black')
        plt.title('Distribution of Relevance Scores')
        plt.xlabel('Relevance Score')
        plt.ylabel('Frequency')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return plt.gcf()
    
    def create_category_analysis(self, figsize: tuple = (12, 8)) -> plt.Figure:
        """Create category analysis visualization."""
        if not self.papers_data:
            return None
        
        df = pd.DataFrame(self.papers_data)
        
        # Split categories and count
        all_categories = []
        for categories_str in df['categories']:
            if categories_str != "Unknown":
                categories = [cat.strip() for cat in categories_str.split(',')]
                all_categories.extend(categories)
        
        category_counts = pd.Series(all_categories).value_counts().head(10)
        
        plt.figure(figsize=figsize)
        category_counts.plot(kind='barh')
        plt.title('Top 10 Research Categories')
        plt.xlabel('Number of Papers')
        plt.ylabel('Category')
        plt.tight_layout()
        
        return plt.gcf()
    
    def create_wordcloud(self, text_field: str = 'abstract', figsize: tuple = (12, 8)) -> plt.Figure:
        """Create wordcloud from text field."""
        if not self.papers_data:
            return None
        
        # Combine all text from specified field
        text = ' '.join([paper.get(text_field, '') for paper in self.papers_data])
        
        if not text.strip():
            return None
        
        wordcloud = WordCloud(width=800, height=400, background_color='white',
                            max_words=100, colormap='viridis').generate(text)
        
        plt.figure(figsize=figsize)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'Word Cloud from {text_field.title()}')
        plt.tight_layout()
        
        return plt.gcf()
    
    def create_author_network(self, min_papers: int = 2, figsize: tuple = (12, 8)) -> plt.Figure:
        """Create author collaboration network."""
        if not self.papers_data:
            return None
        
        # Build author-paper relationships
        author_papers = {}
        for paper in self.papers_data:
            authors = [author.strip() for author in paper['authors'].split(',')]
            for author in authors:
                if author not in author_papers:
                    author_papers[author] = []
                author_papers[author].append(paper['title'])
        
        # Filter authors with minimum papers
        active_authors = {author: papers for author, papers in author_papers.items() 
                         if len(papers) >= min_papers}
        
        if len(active_authors) < 2:
            return None
        
        # Create network
        G = nx.Graph()
        
        # Add nodes (authors)
        for author in active_authors:
            G.add_node(author, papers=len(active_authors[author]))
        
        # Add edges (collaborations)
        for paper in self.papers_data:
            authors = [author.strip() for author in paper['authors'].split(',')]
            active_paper_authors = [a for a in authors if a in active_authors]
            
            for i in range(len(active_paper_authors)):
                for j in range(i + 1, len(active_paper_authors)):
                    G.add_edge(active_paper_authors[i], active_paper_authors[j])
        
        plt.figure(figsize=figsize)
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, 
                              node_size=[G.nodes[node]['papers'] * 100 for node in G.nodes()],
                              node_color='lightblue', alpha=0.7)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, alpha=0.3)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=8)
        
        plt.title('Author Collaboration Network')
        plt.axis('off')
        plt.tight_layout()
        
        return plt.gcf()
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics of the research data."""
        if not self.papers_data:
            return {"error": "No papers data available"}
        
        df = pd.DataFrame(self.papers_data)
        
        stats = {
            "total_papers": len(df),
            "unique_authors": len(set([author.strip() for authors in df['authors'] 
                                     for author in authors.split(',')])),
            "date_range": {
                "earliest": df['published'].min(),
                "latest": df['published'].max()
            },
            "relevance_scores": {
                "mean": df['relevance_score'].mean(),
                "median": df['relevance_score'].median(),
                "std": df['relevance_score'].std(),
                "min": df['relevance_score'].min(),
                "max": df['relevance_score'].max()
            },
            "search_history": self.search_history
        }
        
        return stats
    
    def export_to_dataframe(self) -> pd.DataFrame:
        """Export papers data to pandas DataFrame."""
        if not self.papers_data:
            return pd.DataFrame()
        
        return pd.DataFrame(self.papers_data)


# Convenience functions for direct use in notebooks
async def search_papers(query: str, max_results: int = 10, 
                       years_back: int = 4, include_full_text: bool = True) -> ArxivResearchHelper:
    """Search papers and return a helper object for analysis."""
    helper = ArxivResearchHelper()
    await helper.search_and_analyze(query, max_results, years_back, include_full_text)
    return helper


def create_visualizations(helper: ArxivResearchHelper) -> Dict[str, plt.Figure]:
    """Create all available visualizations."""
    visualizations = {}
    
    # Timeline
    fig = helper.create_publication_timeline()
    if fig:
        visualizations['timeline'] = fig
    
    # Relevance distribution
    fig = helper.create_relevance_distribution()
    if fig:
        visualizations['relevance_dist'] = fig
    
    # Category analysis
    fig = helper.create_category_analysis()
    if fig:
        visualizations['categories'] = fig
    
    # Wordcloud
    fig = helper.create_wordcloud()
    if fig:
        visualizations['wordcloud'] = fig
    
    # Author network
    fig = helper.create_author_network()
    if fig:
        visualizations['author_network'] = fig
    
    return visualizations


# Example usage for Jupyter notebooks
def example_usage():
    """Example usage for Jupyter notebooks."""
    print("""
# Example usage in Jupyter notebook:

# 1. Search for papers
helper = await search_papers("machine learning", max_results=20)

# 2. Get summary statistics
stats = helper.get_summary_statistics()
print(stats)

# 3. Create visualizations
viz = create_visualizations(helper)
for name, fig in viz.items():
    plt.figure(fig.number)
    plt.show()

# 4. Export to DataFrame
df = helper.export_to_dataframe()
df.head()

# 5. Create custom analysis
fig = helper.create_wordcloud('title')  # Wordcloud from titles
plt.show()
    """)


if __name__ == "__main__":
    example_usage()
