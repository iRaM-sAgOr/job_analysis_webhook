# Main analyzer class that uses LLM and scraping

from app.services.llm_service import LLMProviderFactory
from app.services.job_scraper import JobScraper


class MultiLLMJobAnalyzer:
    def __init__(self, llm_provider: str, api_key: str, model_name: str = None):
        self.llm = LLMProviderFactory(llm_provider, api_key, model_name)
        self.scraper = JobScraper()

    def analyze_job_post(self, content: str, question: str = None) -> str:
        if not self.llm.api_key:
            return f"Please configure your {self.llm.provider.upper()} API key to use AI analysis."
        try:
            if question:
                prompt = f"""
                Based on the following job post content, please answer this question: {question}
                
                Job Post Content:
                {content}
                
                Please provide a helpful and accurate answer based on the job post information.
                """
            else:
                prompt = f"""
                Analyze the following job post and extract the relevant information. 
                Respond ONLY with a valid JSON object, without any code block formatting or extra text. 
                The "summary" field must be a nested JSON object.

                JSON format:
                {{
                  "job_title": "",
                  "company_name": "",
                  "key_responsibilities": [],
                  "required_qualifications": [],
                  "preferred_skills": [],
                  "salary_compensation": "",
                  "location_remote_options": "",
                  "other_important_details": "",
                  "potential_red_flags": "",
                  "overall_impression": "",
                  "summary": {{
                    "salary": "",
                    "remote_or_onsite": "",
                    "skills": [],
                    "experience_years": "",
                    "main_responsibility": ""
                  }}
                }}

                - Fill each field with the relevant information from the job post.
                - For lists, use JSON arrays.
                - If a field is not mentioned, leave it as an empty string or empty array.

                Job Post Content:
                {content}
                """
            return self.llm.call_llm(prompt)
        except Exception as e:
            return f"Error analyzing content with {self.llm.provider}: {str(e)}"
