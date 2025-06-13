# job_scraper.py
# ---------------------------------------------
# This module provides the JobScraper class for scraping and extracting job post content from a given URL.
#
# Responsibilities:
# - Fetches the HTML content of a job post web page using requests.
# - Cleans the HTML by removing scripts, styles, navigation, and other non-content elements.
# - Attempts to extract job-specific content using a set of common CSS selectors for popular job boards (LinkedIn, Indeed, Glassdoor, etc.).
# - If job-specific content is not found, falls back to extracting general content by filtering lines with job-related keywords.
# - Cleans and normalizes the extracted text, removing noise and extra whitespace.
# - Returns a dictionary with the extraction result, including the title, content, and URL, or an error message if scraping fails.
#
# Usage:
#   scraper = JobScraper()
#   result = scraper.scrape_url("https://example.com/job-post")
#   if result["success"]:
#       print(result["content"])
# ---------------------------------------------

# Scrapes and extracts job post content from URLs

import requests
from bs4 import BeautifulSoup
import re


class JobScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_url(self, url: str) -> dict:
        """Scrapes the given URL and extracts job post content.

        Args:
            url (str): The URL of the job post to scrape.

        Returns:
            dict: A dictionary containing the extraction result, with keys:
                - success (bool): Indicates if the scraping was successful.
                - title (str): The title of the job post.
                - content (str): The extracted content of the job post (truncated to 6000 characters).
                - url (str): The URL of the job post.
                - error (str, optional): An error message if scraping fails.
        """
        try:
            # Send HTTP GET request to the job post URL with custom headers
            response = requests.get(url, headers=self.headers, timeout=10)
            # Raise an exception if the response status is not 200 OK
            response.raise_for_status()
            # Parse the HTML content using BeautifulSoup
            content_data = BeautifulSoup(response.content, 'html.parser')
            # Remove unwanted elements (script, style, nav, etc.) from the soup
            for element in content_data(["script", "style", "nav", "header", "footer", "aside", "advertisement"]):
                element.decompose()
            # Try to extract job-specific content using CSS selectors
            job_content = self._extract_job_content(content_data)
            # If job-specific content is not found, extract general content
            if not job_content:
                job_content = self._extract_general_content(content_data)
            # Get the page title, or use a default if not found
            title = content_data.title.string if content_data.title else "No title found"
            # Return the result dictionary with extracted content (truncated to 6000 chars)
            return {
                "success": True,
                "title": title.strip(),
                "content": job_content[:6000],
                "url": url
            }
        except Exception as e:
            # Return error information if scraping fails
            return {
                "success": False,
                "error": str(e),
                "url": url
            }

    def _extract_job_content(self, content_data) -> str:
        """Extracts job-specific content from the soup object using common CSS selectors.

        Args:
            content_data (BeautifulSoup): The BeautifulSoup object containing the parsed HTML of the job post.

        Returns:
            str: The extracted job content, or an empty string if no content is found.
        """
        # List of CSS selectors for common job post containers (LinkedIn, Indeed, Glassdoor, etc.)
        job_selectors = [
            '.jobs-search__job-details--container', '.job-details', '.jobs-description',
            '.jobsearch-jobDescriptionText', '.jobsearch-JobComponent-description',
            '.jobDescriptionContent', '.desc',
            '[class*="job-description"]', '[class*="job-details"]', '[class*="description"]',
            '[id*="job-description"]', '[id*="job-details"]',
            'article', '.content', '.main-content', '[role="main"]'
        ]
        for selector in job_selectors:
            # Select elements matching the current selector
            elements = content_data.select(selector)
            if elements:
                # Get text from the first matching element, joining with spaces
                content = elements[0].get_text(strip=True, separator=' ')
                # Only return if the content is substantial (over 200 chars)
                if len(content) > 200:
                    return self._clean_text(content)
        return ""

    def _extract_general_content(self, content_data) -> str:
        """Extracts general content from the soup object by filtering lines with job-related keywords.

        Args:
            content_data (BeautifulSoup): The BeautifulSoup object containing the parsed HTML of the job post.

        Returns:
            str: The extracted general content, or an empty string if no content is found.
        """
        # Get all text from the HTML
        text = content_data.get_text()
        # Split text into lines
        lines = text.split('\n')
        filtered_lines = []
        # List of keywords relevant to job posts
        job_keywords = [
            'responsibilities', 'requirements', 'qualifications', 'experience',
            'skills', 'salary', 'benefits', 'location', 'remote', 'hybrid',
            'position', 'role', 'job', 'career', 'employment', 'apply'
        ]
        for line in lines:
            line = line.strip()
            # Skip very short lines
            if len(line) > 10:
                # Keep lines containing job-related keywords
                if any(keyword in line.lower() for keyword in job_keywords):
                    filtered_lines.append(line)
                # Also keep longer descriptive lines
                elif len(line) > 50:
                    filtered_lines.append(line)
        # Join filtered lines and clean the text
        return self._clean_text(' '.join(filtered_lines))

    def _clean_text(self, text: str) -> str:
        """Cleans and normalizes the given text by removing noise and extra whitespace.

        Args:
            text (str): The text to clean and normalize.

        Returns:
            str: The cleaned and normalized text.
        """
        # Replace multiple whitespace with a single space
        text = re.sub(r'\s+', ' ', text)
        # Patterns of common noise to remove from job posts
        noise_patterns = [
            r'Accept all cookies', r'Cookie preferences', r'Sign in to save',
            r'Create alert', r'Share this job', r'Report this job',
            r'Skip to main content', r'Navigation menu',
        ]
        for pattern in noise_patterns:
            # Remove each noise pattern (case-insensitive)
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text.strip()
