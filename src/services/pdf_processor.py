"""PDF processing service for extracting full text."""

import asyncio
import io
import logging
from typing import Optional

import httpx
import PyPDF2
import pdfplumber
from asyncio_throttle import Throttler

from config.settings import settings

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Service for downloading and processing PDF files."""
    
    def __init__(self):
        self.timeout = settings.PDF_TIMEOUT
        self.max_concurrent = settings.MAX_CONCURRENT_DOWNLOADS
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        self.throttler = Throttler(rate_limit=1/settings.REQUEST_RATE_LIMIT)
        
    async def extract_text_from_url(self, pdf_url: str) -> Optional[str]:
        """Download and extract text from a PDF URL."""
        
        async with self.semaphore:
            try:
                async with self.throttler:
                    logger.debug(f"Downloading PDF: {pdf_url}")
                    
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.get(pdf_url)
                        response.raise_for_status()
                
                # Try multiple extraction methods
                text = await self._extract_text_multiple_methods(response.content)
                
                if text and len(text.strip()) > 100:  # Minimum text threshold
                    # Truncate if too long
                    if len(text) > settings.MAX_FULL_TEXT_LENGTH:
                        text = text[:settings.MAX_FULL_TEXT_LENGTH] + "\n\n[Text truncated due to length limit]"
                    
                    logger.debug(f"Successfully extracted {len(text)} characters from PDF")
                    return text.strip()
                else:
                    logger.warning(f"Insufficient text extracted from PDF: {pdf_url}")
                    return None
                    
            except Exception as e:
                logger.warning(f"Failed to process PDF {pdf_url}: {e}")
                return None
    
    async def _extract_text_multiple_methods(self, pdf_content: bytes) -> Optional[str]:
        """Try multiple PDF text extraction methods."""
        
        # Method 1: PyPDF2
        try:
            text = await self._extract_with_pypdf2(pdf_content)
            if text and len(text.strip()) > 100:
                return text
        except Exception as e:
            logger.debug(f"PyPDF2 extraction failed: {e}")
        
        # Method 2: pdfplumber
        try:
            text = await self._extract_with_pdfplumber(pdf_content)
            if text and len(text.strip()) > 100:
                return text
        except Exception as e:
            logger.debug(f"pdfplumber extraction failed: {e}")
        
        return None
    
    async def _extract_with_pypdf2(self, pdf_content: bytes) -> str:
        """Extract text using PyPDF2."""
        
        def extract():
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = ""
            for page in pdf_reader.pages[:20]:  # Limit to first 20 pages
                text_content += page.extract_text() + "\n"
            
            return text_content.strip()
        
        # Run in thread pool to avoid blocking
        return await asyncio.to_thread(extract)
    
    async def _extract_with_pdfplumber(self, pdf_content: bytes) -> str:
        """Extract text using pdfplumber."""
        
        def extract():
            pdf_file = io.BytesIO(pdf_content)
            text_content = ""
            
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages[:20]:  # Limit to first 20 pages
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
            
            return text_content.strip()
        
        # Run in thread pool to avoid blocking
        return await asyncio.to_thread(extract)
    
    async def process_papers_batch(self, papers: list) -> list:
        """Process multiple papers concurrently."""
        
        async def process_single_paper(paper):
            """Process a single paper."""
            full_text = await self.extract_text_from_url(paper.pdf_url)
            paper.full_text = full_text
            return paper
        
        # Process papers concurrently
        tasks = [process_single_paper(paper) for paper in papers]
        processed_papers = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful results
        successful_papers = [
            paper for paper in processed_papers 
            if not isinstance(paper, Exception)
        ]
        
        logger.info(f"Successfully processed {len(successful_papers)}/{len(papers)} papers")
        return successful_papers