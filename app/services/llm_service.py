# Handles LLM provider setup and API calls
import openai
import google.generativeai as genai


class LLMProviderFactory:
    """Factory for creating LLM provider clients (OpenAI, Gemini, Anthropic)"""

    def __init__(self, provider: str, api_key: str, model_name: str = None):
        self.provider = provider.lower()
        self.api_key = api_key
        self.model_name = model_name
        self.client = None
        self.default_model = None
        self._setup_llm()

    def _setup_llm(self):
        try:
            if self.provider == "openai":
                self.client = openai.OpenAI(api_key=self.api_key)
                self.default_model = self.model_name or "gpt-3.5-turbo"
            elif self.provider == "gemini":
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(
                    self.model_name or 'gemini-1.5-flash')
                self.default_model = self.model_name or 'gemini-1.5-flash'
            elif self.provider == "anthropic":
                try:
                    import anthropic
                    self.client = anthropic.Anthropic(api_key=self.api_key)
                    self.default_model = self.model_name or "claude-3-sonnet-20240229"
                except ImportError:
                    raise Exception(
                        "Please install anthropic package: pip install anthropic")
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        except Exception as e:
            raise Exception(f"Failed to setup {self.provider}: {str(e)}")

    def call_llm(self, prompt: str) -> str:
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.default_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.3
                )
                return response.choices[0].message.content
            elif self.provider == "gemini":
                response = self.client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=1000,
                        temperature=0.3,
                    )
                )
                return response.text
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.default_model,
                    max_tokens=1000,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            else:
                return f"LLM provider {self.provider} not implemented yet"
        except Exception as e:
            return f"Error calling {self.provider}: {str(e)}"
