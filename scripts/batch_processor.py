#!/usr/bin/env python3
"""Batch processor for multiple research topics."""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.research_assistant import ResearchAssistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchProcessor:
    """Batch processor for research topics."""
    
    def __init__(self, server_path: str, output_dir: str = "batch_outputs"):
        self.server_path = server_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    async def process_topics(
        self,
        topics: List[str],
        max_results: int = 10,
        years_back: int = 4,
        include_full_text: bool = True
    ) -> Dict[str, Dict]:
        """Process multiple research topics."""
        
        results = {}
        total_topics = len(topics)
        
        logger.info(f"Processing {total_topics} topics")
        
        async with ResearchAssistant(self.server_path) as assistant:
            for i, topic in enumerate(topics, 1):
                logger.info(f"Processing topic {i}/{total_topics}: {topic}")
                
                try:
                    # Search for papers
                    papers = await assistant.search_papers(
                        query=topic,
                        max_results=max_results,
                        years_back=years_back,
                        include_full_text=include_full_text
                    )
                    
                    results[topic] = {
                        "status": "success",
                        "papers": papers,
                        "processed_at": datetime.now().isoformat(),
                        "params": {
                            "max_results": max_results,
                            "years_back": years_back,
                            "include_full_text": include_full_text
                        }
                    }
                    
                    # Save individual results
                    await self.save_topic_results(topic, results[topic])
                    
                except Exception as e:
                    logger.error(f"Error processing topic '{topic}': {e}")
                    results[topic] = {
                        "status": "error",
                        "error": str(e),
                        "processed_at": datetime.now().isoformat()
                    }
                
                # Small delay to be respectful to the API
                await asyncio.sleep(1)
        
        # Save combined results
        await self.save_combined_results(results)
        
        return results
    
    async def save_topic_results(self, topic: str, data: Dict):
        """Save results for a single topic."""
        filename = f"{topic.replace(' ', '_').replace('/', '_')}_results.json"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved results for topic: {topic}")
        except Exception as e:
            logger.error(f"Error saving results for topic '{topic}': {e}")
    
    async def save_combined_results(self, results: Dict):
        """Save combined results from all topics."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"batch_results_{timestamp}.json"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved combined results to: {filepath}")
        except Exception as e:
            logger.error(f"Error saving combined results: {e}")
    
    def generate_summary_report(self, results: Dict) -> str:
        """Generate a summary report of the batch processing."""
        
        total_topics = len(results)
        successful = len([r for r in results.values() if r["status"] == "success"])
        failed = total_topics - successful
        
        report = f"""
# Batch Processing Report

**Processing Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Topics:** {total_topics}
**Successful:** {successful}
**Failed:** {failed}
**Success Rate:** {(successful/total_topics)*100:.1f}%

## Topics Processed:

"""
        
        for topic, data in results.items():
            status = "✅" if data["status"] == "success" else "❌"
            report += f"- {status} {topic}\n"
            
            if data["status"] == "error":
                report += f"  Error: {data['error']}\n"
        
        return report
    
    async def save_summary_report(self, results: Dict):
        """Save a summary report."""
        report = self.generate_summary_report(results)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"batch_summary_{timestamp}.md"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Saved summary report to: {filepath}")
        except Exception as e:
            logger.error(f"Error saving summary report: {e}")


async def main():
    """Main function for batch processing."""
    
    # Default topics - you can modify these or load from a file
    default_topics = [
        "transformer models",
        "quantum machine learning",
        "federated learning",
        "graph neural networks",
        "reinforcement learning",
        "computer vision",
        "natural language processing",
        "automated machine learning",
        "explainable AI",
        "adversarial machine learning"
    ]
    
    # Configuration
    server_path = str(Path(__file__).parent / "run_server.py")
    output_dir = "batch_outputs"
    
    # Initialize processor
    processor = BatchProcessor(server_path, output_dir)
    
    # Process topics
    try:
        results = await processor.process_topics(
            topics=default_topics,
            max_results=5,  # Smaller number for batch processing
            years_back=2,   # More recent papers
            include_full_text=False  # Faster processing
        )
        
        # Generate and save summary report
        await processor.save_summary_report(results)
        
        # Print summary
        successful = len([r for r in results.values() if r["status"] == "success"])
        total = len(results)
        
        print(f"\n{'='*50}")
        print(f"BATCH PROCESSING COMPLETE")
        print(f"{'='*50}")
        print(f"Total topics: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        print(f"Success rate: {(successful/total)*100:.1f}%")
        print(f"Output directory: {output_dir}")
        print(f"{'='*50}")
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())