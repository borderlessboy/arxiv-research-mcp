"""Streamlit dashboard for the arXiv Research MCP Server."""

import asyncio
import logging
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re
from typing import Dict, List
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.research_assistant import ResearchAssistant

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit configuration
st.set_page_config(
    page_title="arXiv Research Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


class StreamlitResearchApp:
    """Streamlit application for arXiv research."""

    def __init__(self):
        self.server_path = str(
            Path(__file__).parent.parent / "scripts" / "run_server.py"
        )

        # Initialize session state
        if "search_results" not in st.session_state:
            st.session_state.search_results = {}
        if "search_history" not in st.session_state:
            st.session_state.search_history = []

    def run(self):
        """Run the Streamlit app."""

        # Title and description
        st.title("📚 arXiv Research Assistant")
        st.markdown(
            "Search and analyze recent academic papers from arXiv with AI-powered relevance ranking."
        )

        # Sidebar
        with st.sidebar:
            self.render_sidebar()

        # Main content
        self.render_main_content()

        # Footer
        st.markdown("---")
        st.markdown("*Powered by arXiv Research MCP Server*")

    def render_sidebar(self):
        """Render the sidebar with search controls."""

        st.header("🔍 Search Parameters")

        # Search form
        with st.form("search_form"):
            query = st.text_input(
                "Research Topic",
                value="transformer models",
                help="Enter your research topic (e.g., 'quantum computing', 'machine learning')",
            )

            col1, col2 = st.columns(2)
            with col1:
                max_results = st.slider("Max Papers", 1, 20, 10)
            with col2:
                years_back = st.slider("Years Back", 1, 10, 4)

            include_full_text = st.checkbox("Include Full Text", value=True)

            submitted = st.form_submit_button("🔍 Search Papers", type="primary")

            if submitted and query:
                with st.spinner("Searching arXiv..."):
                    try:
                        results = asyncio.run(
                            self.search_papers(
                                query, max_results, years_back, include_full_text
                            )
                        )

                        if results:
                            st.session_state.search_results[query] = {
                                "results": results,
                                "timestamp": datetime.now(),
                                "params": {
                                    "max_results": max_results,
                                    "years_back": years_back,
                                    "include_full_text": include_full_text,
                                },
                            }

                            # Add to search history
                            if query not in st.session_state.search_history:
                                st.session_state.search_history.append(query)

                            st.success(f"Found papers for: {query}")
                            st.rerun()

                    except Exception as e:
                        st.error(f"Error searching papers: {e}")

        # Search history
        if st.session_state.search_history:
            st.header("📝 Search History")
            for i, historical_query in enumerate(
                reversed(st.session_state.search_history[-5:])
            ):
                if st.button(f"📄 {historical_query}", key=f"history_{i}"):
                    st.session_state.selected_query = historical_query
                    st.rerun()

        # Cache management
        st.header("💾 Cache Management")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📊 Cache Stats"):
                with st.spinner("Getting cache stats..."):
                    try:
                        stats = asyncio.run(self.get_cache_stats())
                        st.text(stats)
                    except Exception as e:
                        st.error(f"Error: {e}")

        with col2:
            if st.button("🗑️ Clear Cache"):
                with st.spinner("Clearing cache..."):
                    try:
                        result = asyncio.run(self.clear_cache())
                        st.success(result)
                    except Exception as e:
                        st.error(f"Error: {e}")

    def render_main_content(self):
        """Render the main content area."""

        # Tab selection
        tab1, tab2, tab3 = st.tabs(["📄 Papers", "📊 Analytics", "🔬 Analysis"])

        with tab1:
            self.render_papers_tab()

        with tab2:
            self.render_analytics_tab()

        with tab3:
            self.render_analysis_tab()

    def render_papers_tab(self):
        """Render the papers display tab."""

        # Query selection
        if st.session_state.search_results:
            queries = list(st.session_state.search_results.keys())
            selected_query = st.selectbox(
                "Select Search Results",
                queries,
                index=len(queries) - 1 if queries else 0,
            )

            if selected_query:
                search_data = st.session_state.search_results[selected_query]
                results_text = search_data["results"]
                timestamp = search_data["timestamp"]

                # Display metadata
                st.info(
                    f"**Query:** {selected_query} | **Searched:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                )

                # Parse and display papers
                papers = self.parse_papers_from_results(results_text)

                if papers:
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Papers", len(papers))
                    with col2:
                        avg_relevance = sum(
                            p.get("relevance_score", 0) for p in papers
                        ) / len(papers)
                        st.metric("Avg Relevance", f"{avg_relevance:.3f}")
                    with col3:
                        recent_papers = len(
                            [
                                p
                                for p in papers
                                if self.is_recent_paper(p.get("date", ""))
                            ]
                        )
                        st.metric("Recent Papers", recent_papers)
                    with col4:
                        with_full_text = len(
                            [p for p in papers if p.get("has_full_text", False)]
                        )
                        st.metric("With Full Text", with_full_text)

                    # Display papers
                    for i, paper in enumerate(papers):
                        with st.expander(
                            f"📄 {paper.get('title', 'Unknown Title')[:100]}...",
                            expanded=i == 0,
                        ):
                            col1, col2 = st.columns([3, 1])

                            with col1:
                                st.write(
                                    f"**Authors:** {paper.get('authors', 'Unknown')}"
                                )
                                st.write(
                                    f"**Published:** {paper.get('date', 'Unknown')}"
                                )
                                st.write(
                                    f"**Categories:** {paper.get('categories', 'Unknown')}"
                                )

                            with col2:
                                st.metric(
                                    "Relevance",
                                    f"{paper.get('relevance_score', 0):.3f}",
                                )
                                if paper.get("url"):
                                    st.link_button("View on arXiv", paper["url"])

                            # Abstract
                            st.write("**Abstract:**")
                            st.write(paper.get("abstract", "No abstract available"))

                            # Full text preview
                            if paper.get("has_full_text") and paper.get("full_text"):
                                with st.expander("📖 Full Text Preview"):
                                    st.text_area(
                                        "Full Text",
                                        value=(
                                            paper["full_text"][:2000] + "..."
                                            if len(paper["full_text"]) > 2000
                                            else paper["full_text"]
                                        ),
                                        height=200,
                                        disabled=True,
                                    )

                else:
                    st.write("No papers found or results not parsed correctly.")

        else:
            st.info(
                "No search results available. Use the sidebar to search for papers."
            )

    def render_analytics_tab(self):
        """Render the analytics tab."""

        if not st.session_state.search_results:
            st.info("No search results available for analysis.")
            return

        # Query selection for analytics
        queries = list(st.session_state.search_results.keys())
        selected_queries = st.multiselect(
            "Select queries for analysis",
            queries,
            default=queries[-3:] if len(queries) >= 3 else queries,
        )

        if selected_queries:
            # Aggregate data from selected queries
            all_papers = []
            for query in selected_queries:
                papers = self.parse_papers_from_results(
                    st.session_state.search_results[query]["results"]
                )
                for paper in papers:
                    paper["query"] = query
                all_papers.extend(papers)

            if all_papers:
                # Create visualizations
                self.create_analytics_visualizations(all_papers)

    def render_analysis_tab(self):
        """Render the analysis tab."""

        if not st.session_state.search_results:
            st.info("No search results available for analysis.")
            return

        # Query selection
        queries = list(st.session_state.search_results.keys())
        selected_query = st.selectbox(
            "Select results to analyze", queries, key="analysis_query"
        )

        if selected_query:
            results_text = st.session_state.search_results[selected_query]["results"]

            # Analysis options
            analysis_type = st.selectbox(
                "Analysis Type",
                [
                    "Key Trends",
                    "Research Gaps",
                    "Methodological Analysis",
                    "Future Directions",
                ],
            )

            # Display formatted results for LLM analysis
            st.subheader("📋 Formatted Results for Analysis")

            analysis_prompt = f"""
Analyze the following research papers about "{selected_query}" and provide insights on {analysis_type.lower()}:

{results_text}

Please provide a comprehensive analysis focusing on {analysis_type.lower()}.
"""

            st.text_area(
                "Analysis Prompt",
                value=analysis_prompt,
                height=400,
                help="Copy this prompt and use it with your preferred LLM for analysis",
            )

            # Copy button (JavaScript)
            st.markdown(
                """
<script>
function copyToClipboard() {
    const textarea = document.querySelector('textarea[aria-label="Analysis Prompt"]');
    textarea.select();
    document.execCommand('copy');
}
</script>
""",
                unsafe_allow_html=True,
            )

    async def search_papers(
        self, query: str, max_results: int, years_back: int, include_full_text: bool
    ) -> str:
        """Search for papers using the MCP server."""
        async with ResearchAssistant(self.server_path) as assistant:
            return await assistant.search_papers(
                query=query,
                max_results=max_results,
                years_back=years_back,
                include_full_text=include_full_text,
            )

    async def clear_cache(self) -> str:
        """Clear the server cache."""
        async with ResearchAssistant(self.server_path) as assistant:
            return await assistant.clear_cache()

    async def get_cache_stats(self) -> str:
        """Get cache statistics."""
        async with ResearchAssistant(self.server_path) as assistant:
            return await assistant.get_cache_stats()

    def parse_papers_from_results(self, results_text: str) -> List[Dict]:
        """Parse papers from the formatted results text."""
        papers = []

        # Split by paper markers
        paper_sections = re.split(r"## Paper \d+:", results_text)

        for section in paper_sections[1:]:  # Skip the header
            paper = {}

            # Extract title
            title_match = re.search(r"^([^\n]+)", section.strip())
            if title_match:
                paper["title"] = title_match.group(1).strip()

            # Extract other fields
            paper["authors"] = self.extract_field(section, r"\*\*Authors:\*\* ([^\n]+)")
            paper["date"] = self.extract_field(section, r"\*\*Published:\*\* ([^\n]+)")
            paper["categories"] = self.extract_field(
                section, r"\*\*Categories:\*\* ([^\n]+)"
            )
            paper["url"] = self.extract_field(section, r"\*\*URL:\*\* ([^\n]+)")

            # Extract relevance score
            relevance_match = re.search(r"\*\*Relevance Score:\*\* ([0-9.]+)", section)
            if relevance_match:
                paper["relevance_score"] = float(relevance_match.group(1))
            else:
                paper["relevance_score"] = 0.0

            # Extract abstract
            abstract_match = re.search(
                r"\*\*Abstract:\*\*\n([^*]+?)(?=\*\*|$)", section, re.DOTALL
            )
            if abstract_match:
                paper["abstract"] = abstract_match.group(1).strip()

            # Check if full text is available
            paper["has_full_text"] = "**Full Text:**" in section

            # Extract full text preview
            if paper["has_full_text"]:
                full_text_match = re.search(
                    r"\*\*Full Text:\*\*\n(.*?)(?=\n\n---|\Z)", section, re.DOTALL
                )
                if full_text_match:
                    paper["full_text"] = full_text_match.group(1).strip()

            papers.append(paper)

        return papers

    def extract_field(self, text: str, pattern: str) -> str:
        """Extract a field using regex pattern."""
        match = re.search(pattern, text)
        return match.group(1) if match else "Unknown"

    def is_recent_paper(self, date_str: str, days_threshold: int = 30) -> bool:
        """Check if a paper is recent."""
        try:
            paper_date = datetime.strptime(date_str, "%B %d, %Y")
            return (datetime.now() - paper_date).days <= days_threshold
        except Exception:
            return False

    def create_analytics_visualizations(self, papers: List[Dict]):
        """Create analytics visualizations."""

        # Publication timeline
        st.subheader("📈 Publication Timeline")

        # Extract years from papers
        years = []
        for paper in papers:
            try:
                date_str = paper.get("date", "")
                if date_str and date_str != "Unknown":
                    year = datetime.strptime(date_str, "%B %d, %Y").year
                    years.append(year)
            except Exception:
                continue

        if years:
            year_counts = pd.Series(years).value_counts().sort_index()
            fig = px.bar(
                x=year_counts.index,
                y=year_counts.values,
                title="Papers by Publication Year",
                labels={"x": "Year", "y": "Number of Papers"},
            )
            st.plotly_chart(fig, use_container_width=True)

        # Relevance score distribution
        st.subheader("📊 Relevance Score Distribution")

        relevance_scores = [p.get("relevance_score", 0) for p in papers]
        if relevance_scores:
            fig = px.histogram(
                x=relevance_scores,
                nbins=20,
                title="Distribution of Relevance Scores",
                labels={"x": "Relevance Score", "y": "Count"},
            )
            st.plotly_chart(fig, use_container_width=True)

        # Query comparison
        if len(set(p.get("query", "") for p in papers)) > 1:
            st.subheader("🔍 Query Comparison")

            query_data = []
            for paper in papers:
                query_data.append(
                    {
                        "Query": paper.get("query", ""),
                        "Relevance": paper.get("relevance_score", 0),
                        "Year": years[0] if years else 2024,  # Fallback
                    }
                )

            df = pd.DataFrame(query_data)

            # Box plot of relevance scores by query
            fig = px.box(
                df,
                x="Query",
                y="Relevance",
                title="Relevance Score Distribution by Query",
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

        # Category analysis
        st.subheader("📚 Research Categories")

        all_categories = []
        for paper in papers:
            categories = paper.get("categories", "").split(", ")
            all_categories.extend([cat.strip() for cat in categories if cat.strip()])

        if all_categories:
            category_counts = pd.Series(all_categories).value_counts().head(10)
            fig = px.bar(
                x=category_counts.values,
                y=category_counts.index,
                orientation="h",
                title="Top 10 Research Categories",
            )
            st.plotly_chart(fig, use_container_width=True)


# Main execution
if __name__ == "__main__":
    app = StreamlitResearchApp()
    app.run()
