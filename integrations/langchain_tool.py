"""LangChain integration for the arXiv Research MCP Server."""

import asyncio
import logging
from typing import Dict, List, Optional, Type

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool
from langchain.schema import AgentAction, AgentFinish
from langchain.agents import AgentType, initialize_agent
from langchain.llms.base import BaseLLM
from langchain_openai import OpenAI
from pydantic import BaseModel, Field
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.research_assistant import ResearchAssistant

logger = logging.getLogger(__name__)


class ArxivSearchInput(BaseModel):
    """Input schema for arXiv search tool."""
    query: str = Field(description="Research query to search for")
    max_results: int = Field(default=10, description="Maximum number of papers to return")
    years_back: int = Field(default=4, description="Number of years back to search")
    include_full_text: bool = Field(default=True, description="Whether to include full paper text")


class ArxivResearchTool(BaseTool):
    """LangChain tool for searching arXiv papers."""
    
    name: str = "arxiv_research"
    description: str = """
    Search for recent academic papers on arXiv with AI-powered relevance ranking.
    
    This tool searches arXiv for papers matching your query and returns:
    - Papers from the specified time period (default: last 4 years)
    - Relevance-ranked results using TF-IDF similarity
    - Full paper text when available
    - Abstracts, authors, publication dates, and arXiv links
    
    Input should be a JSON object with:
    - query: research topic (required)
    - max_results: number of papers to return (default: 10)
    - years_back: years to search back (default: 4)
    - include_full_text: whether to extract full text (default: true)
    """
    
    args_schema: Type[BaseModel] = ArxivSearchInput
    return_direct: bool = False
    
    def __init__(self, server_path: str = None):
        super().__init__()
        self.server_path = server_path or str(Path(__file__).parent.parent / "scripts" / "run_server.py")
    
    def _run(
        self,
        query: str,
        max_results: int = 10,
        years_back: int = 4,
        include_full_text: bool = True,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the tool synchronously."""
        try:
            return asyncio.run(self._arun(query, max_results, years_back, include_full_text, run_manager))
        except Exception as e:
            logger.error(f"Error in ArxivResearchTool._run: {e}")
            return f"Error searching arXiv: {str(e)}"
    
    async def _arun(
        self,
        query: str,
        max_results: int = 10,
        years_back: int = 4,
        include_full_text: bool = True,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the tool asynchronously."""
        try:
            if run_manager:
                run_manager.on_tool_start(
                    serialized={"name": self.name},
                    input_str=f"Searching arXiv for: {query}",
                )
            
            async with ResearchAssistant(self.server_path) as assistant:
                results = await assistant.search_papers(
                    query=query,
                    max_results=max_results,
                    years_back=years_back,
                    include_full_text=include_full_text
                )
            
            if run_manager:
                run_manager.on_tool_end(results)
            
            return results
            
        except Exception as e:
            error_msg = f"Error searching arXiv: {str(e)}"
            logger.error(error_msg)
            
            if run_manager:
                run_manager.on_tool_error(e)
            
            return error_msg


class ArxivCacheManagementTool(BaseTool):
    """LangChain tool for managing arXiv search cache."""
    
    name: str = "arxiv_cache_management"
    description: str = """
    Manage the cache for arXiv search results.
    
    Available actions:
    - 'stats': Get cache statistics
    - 'clear': Clear all cached results
    
    Input should be either 'stats' or 'clear'.
    """
    
    def __init__(self, server_path: str = None):
        super().__init__()
        self.server_path = server_path or str(Path(__file__).parent.parent / "scripts" / "run_server.py")
    
    def _run(
        self,
        action: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the tool synchronously."""
        try:
            return asyncio.run(self._arun(action, run_manager))
        except Exception as e:
            logger.error(f"Error in ArxivCacheManagementTool._run: {e}")
            return f"Error with cache management: {str(e)}"
    
    async def _arun(
        self,
        action: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the tool asynchronously."""
        try:
            async with ResearchAssistant(self.server_path) as assistant:
                if action.lower() == 'stats':
                    result = await assistant.get_cache_stats()
                elif action.lower() == 'clear':
                    result = await assistant.clear_cache()
                else:
                    result = f"Unknown action: {action}. Use 'stats' or 'clear'."
            
            return result
            
        except Exception as e:
            error_msg = f"Error with cache management: {str(e)}"
            logger.error(error_msg)
            return error_msg


class ResearchAgent:
    """Research agent with arXiv search capabilities."""
    
    def __init__(self, llm: BaseLLM = None, server_path: str = None, verbose: bool = True):
        """Initialize the research agent."""
        
        self.llm = llm or OpenAI(temperature=0.1)
        self.server_path = server_path or str(Path(__file__).parent.parent / "scripts" / "run_server.py")
        
        # Initialize tools
        self.tools = [
            ArxivResearchTool(server_path=self.server_path),
            ArxivCacheManagementTool(server_path=self.server_path)
        ]
        
        # Initialize agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=verbose,
            max_iterations=5,
            early_stopping_method="generate"
        )
    
    def research_topic(self, research_question: str, detailed: bool = True) -> str:
        """Research a topic using arXiv papers."""
        
        if detailed:
            prompt = f"""
Research Question: {research_question}

Please conduct a comprehensive research analysis by:

1. First, search for relevant recent papers on arXiv
2. Analyze the key findings and methodologies
3. Identify current trends and innovations
4. Highlight any research gaps or limitations
5. Suggest future research directions

Use the arxiv_research tool to gather papers, then provide a detailed analysis.
Include specific examples and citations from the papers you find.
"""
        else:
            prompt = f"""
Research Question: {research_question}

Please search for recent papers on this topic and provide a brief summary of:
1. Main research directions
2. Key recent developments
3. Notable methodologies

Use the arxiv_research tool to gather relevant papers.
"""
        
        return self.agent.run(prompt)
    
    def compare_topics(self, topics: List[str], focus_area: str = None) -> str:
        """Compare multiple research topics."""
        
        focus_clause = f" with a focus on {focus_area}" if focus_area else ""
        
        prompt = f"""
Compare the following research topics{focus_clause}:
{', '.join(topics)}

For each topic:
1. Search for recent papers using the arxiv_research tool
2. Identify key characteristics and methodologies
3. Note similarities and differences
4. Assess maturity and research activity

Provide a comparative analysis highlighting:
- Shared methodologies or approaches
- Unique aspects of each topic
- Cross-pollination opportunities
- Relative research maturity
"""
        
        return self.agent.run(prompt)
    
    def trend_analysis(self, topic: str, years_back: int = 2) -> str:
        """Analyze trends in a research topic."""
        
        prompt = f"""
Analyze recent trends in: {topic}

Search for papers from the last {years_back} years and analyze:
1. Evolution of methodologies
2. Emerging sub-topics or applications
3. Key research groups or authors
4. Technological advances
5. Future trajectory

Use the arxiv_research tool to gather recent papers and provide insights into how this field is evolving.
"""
        
        return self.agent.run(prompt)
    
    def literature_review(self, topic: str, max_papers: int = 15) -> str:
        """Conduct a literature review on a topic."""
        
        prompt = f"""
Conduct a literature review on: {topic}

Search for up to {max_papers} recent papers and provide:

1. **Background**: Current state of the field
2. **Key Contributions**: Major findings and innovations
3. **Methodologies**: Common approaches and techniques
4. **Challenges**: Current limitations and problems
5. **Future Work**: Promising research directions
6. **Conclusion**: Overall assessment and recommendations

Use the arxiv_research tool to gather comprehensive information.
Organize your review with clear sections and cite specific papers.
"""
        
        return self.agent.run(prompt)
    
    def find_research_gaps(self, topic: str) -> str:
        """Identify research gaps in a topic."""
        
        prompt = f"""
Identify research gaps in: {topic}

Search for recent papers and analyze:
1. What problems are being solved
2. What methodologies are commonly used
3. What limitations are frequently mentioned
4. What future work is often suggested
5. What areas seem under-explored

Use the arxiv_research tool to gather papers and identify specific gaps or opportunities for new research.
"""
        
        return self.agent.run(prompt)


class MultiTopicResearchAgent:
    """Advanced research agent for handling multiple topics and complex analyses."""
    
    def __init__(self, llm: BaseLLM = None, server_path: str = None):
        self.base_agent = ResearchAgent(llm=llm, server_path=server_path, verbose=False)
    
    def interdisciplinary_analysis(self, topics: List[str], focus_question: str) -> str:
        """Analyze how multiple topics relate to a specific question."""
        
        results = {}
        
        # Research each topic
        for topic in topics:
            print(f"Researching: {topic}")
            result = self.base_agent.research_topic(
                f"{topic} related to {focus_question}",
                detailed=False
            )
            results[topic] = result
        
        # Synthesize findings
        synthesis_prompt = f"""
Based on the research findings below, provide an interdisciplinary analysis of how these topics relate to: {focus_question}

Research Findings:
"""
        
        for topic, result in results.items():
            synthesis_prompt += f"\n## {topic}:\n{result}\n"
        
        synthesis_prompt += """
Provide a synthesis that:
1. Identifies connections between the topics
2. Highlights complementary approaches
3. Suggests interdisciplinary opportunities
4. Proposes novel research directions
"""
        
        return self.base_agent.agent.run(synthesis_prompt)
    
    def research_roadmap(self, main_topic: str, related_topics: List[str]) -> str:
        """Create a research roadmap for a main topic considering related areas."""
        
        # Research main topic deeply
        main_research = self.base_agent.literature_review(main_topic)
        
        # Research related topics
        related_research = {}
        for topic in related_topics:
            related_research[topic] = self.base_agent.trend_analysis(topic, years_back=3)
        
        # Create roadmap
        roadmap_prompt = f"""
Create a research roadmap for: {main_topic}

Based on the following comprehensive research:

## Main Topic Analysis:
{main_research}

## Related Topics Analysis:
"""
        
        for topic, analysis in related_research.items():
            roadmap_prompt += f"\n### {topic}:\n{analysis}\n"
        
        roadmap_prompt += """
Create a research roadmap that includes:
1. **Current State**: Where the field stands now
2. **Short-term Goals** (1-2 years): Immediate research priorities
3. **Medium-term Goals** (3-5 years): Key milestones and developments
4. **Long-term Vision** (5+ years): Future possibilities and breakthrough potential
5. **Resource Requirements**: What's needed to achieve these goals
6. **Risk Assessment**: Potential challenges and mitigation strategies

Format as a structured roadmap with clear timelines and priorities.
"""
        
        return self.base_agent.agent.run(roadmap_prompt)


# Example usage and testing
if __name__ == "__main__":
    # Example 1: Basic research agent
    agent = ResearchAgent()
    
    print("=== Basic Research Example ===")
    result = agent.research_topic("quantum machine learning")
    print(result)
    
    print("\n=== Topic Comparison Example ===")
    result = agent.compare_topics(
        ["transformer models", "graph neural networks", "reinforcement learning"],
        focus_area="computer vision"
    )
    print(result)
    
    print("\n=== Trend Analysis Example ===")
    result = agent.trend_analysis("federated learning", years_back=2)
    print(result)
    
    # Example 2: Multi-topic research agent
    multi_agent = MultiTopicResearchAgent()
    
    print("\n=== Interdisciplinary Analysis Example ===")
    result = multi_agent.interdisciplinary_analysis(
        ["quantum computing", "machine learning", "cryptography"],
        "data privacy and security"
    )
    print(result)