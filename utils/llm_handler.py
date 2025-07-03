# utils/llm_handler.py
import logging
import os
from typing import Dict, Optional, List
import litellm

logger = logging.getLogger(__name__)

# Configure litellm logging
litellm.set_verbose = False

class LLMConfig:
    """Configuration class for LLM settings"""
    
    def __init__(self):
        self.model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL")  # For local models or custom endpoints
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1000"))
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    
    def is_configured(self) -> bool:
        """Check if LLM is properly configured"""
        # For local models (like Ollama), we don't need an API key
        if self.model.startswith("ollama/"):
            return True
        # For OpenAI-compatible models, we need an API key
        return self.api_key is not None and not self.api_key.startswith("YOUR_PLACEHOLDER")

def get_available_models() -> List[str]:
    """
    Get list of commonly available models across different providers.
    
    Returns:
        List of model names that can be used with litellm
    """
    return [
        # OpenAI models
        "gpt-4o",
        "gpt-4o-mini", 
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        
        # Anthropic models
        "claude-3-5-sonnet-20241022",
        "claude-3-haiku-20240307",
        
        # Local models via Ollama (requires Ollama to be running)
        "ollama/llama3.2",
        "ollama/llama3.1",
        "ollama/mistral",
        "ollama/codellama",
        "ollama/phi3",
        
        # Hugging Face models (some may require specific setup)
        "huggingface/microsoft/DialoGPT-medium",
        "huggingface/google/flan-t5-base",
    ]

def create_summarization_prompt(text_content: str, content_type: str = "transcript") -> str:
    """
    Create an effective prompt for summarizing content.
    
    Args:
        text_content: The content to summarize
        content_type: Type of content (transcript, article, etc.)
    
    Returns:
        Formatted prompt string
    """
    if content_type == "transcript":
        prompt = f"""Please provide a clear and concise summary of this YouTube video transcript. 
Focus on the main points, key insights, and actionable information. 

Structure your summary as:
1. **Main Topic**: Brief description of what the video is about
2. **Key Points**: 3-5 bullet points of the most important information
3. **Notable Insights**: Any interesting facts, statistics, or unique perspectives
4. **Conclusion**: Brief wrap-up of the main takeaway

Transcript:
{text_content}

Summary:"""
    else:
        prompt = f"""Please provide a clear and concise summary of the following content:

{text_content}

Summary:"""
    
    return prompt

def summarize_text_with_llm(text_to_summarize: str, llm_config: Optional[LLMConfig] = None, content_type: str = "transcript") -> Dict:
    """
    Summarize text using various LLM providers through litellm.
    
    Args:
        text_to_summarize: Text content to summarize
        llm_config: LLM configuration object (if None, creates default)
        content_type: Type of content being summarized
    
    Returns:
        Dictionary with summary result and metadata
    """
    logger.info("Attempting to summarize text with LLM...")

    if not text_to_summarize or not text_to_summarize.strip():
        logger.warning("No text provided for summarization.")
        return {
            "success": False,
            "error": "No text provided for summarization",
            "summary": None,
            "model_used": None,
            "tokens_used": None
        }

    # Use provided config or create default
    if llm_config is None:
        llm_config = LLMConfig()
    
    if not llm_config.is_configured():
        logger.warning("LLM not properly configured, using placeholder.")
        return {
            "success": False,
            "error": "LLM not configured (missing API key or invalid model)",
            "summary": f"[PLACEHOLDER] Summary would be generated for content starting with: '{text_to_summarize[:100]}...'",
            "model_used": llm_config.model,
            "tokens_used": None
        }

    try:
        # Create the prompt
        prompt = create_summarization_prompt(text_to_summarize, content_type)
        
        # Prepare arguments for litellm
        llm_args = {
            "model": llm_config.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": llm_config.max_tokens,
            "temperature": llm_config.temperature
        }
        
        # Add API key if available (not needed for local models)
        if llm_config.api_key and not llm_config.model.startswith("ollama/"):
            llm_args["api_key"] = llm_config.api_key
        
        # Add base URL if specified (for local models or custom endpoints)
        if llm_config.base_url:
            llm_args["api_base"] = llm_config.base_url
        
        logger.info(f"Calling LLM model: {llm_config.model}")
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        # Make the API call
        response = litellm.completion(**llm_args)
        
        # Extract the summary
        summary = response.choices[0].message.content.strip()
        
        # Get token usage if available
        tokens_used = None
        if hasattr(response, 'usage') and response.usage:
            tokens_used = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        
        logger.info(f"LLM summarization complete. Summary length: {len(summary)} characters")
        if tokens_used:
            logger.info(f"Tokens used: {tokens_used['total_tokens']} total ({tokens_used['prompt_tokens']} prompt + {tokens_used['completion_tokens']} completion)")
        
        return {
            "success": True,
            "error": None,
            "summary": summary,
            "model_used": llm_config.model,
            "tokens_used": tokens_used
        }
        
    except Exception as e:
        logger.error(f"An error occurred during LLM summarization: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "summary": None,
            "model_used": llm_config.model,
            "tokens_used": None
        }

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG) # Setup basic logging for direct script run
    logger.info("Testing llm_handler.py module...")
    sample_text = (
        "Update 1: Channel A uploaded a new video titled 'Exploring the Mountains'. It's about a recent hiking trip. "
        "Update 2: Channel B posted 'Q&A Session next week! Send your questions.' "
        "Update 3: Channel C released a short 'Behind the Scenes of our latest project.'"
    )

    generated_summary = summarize_text_with_llm(sample_text)
    logger.info(f"Generated Summary:\n{generated_summary}")

    empty_text_summary = summarize_text_with_llm("")
    logger.info(f"Summary for empty text:\n{empty_text_summary}")
