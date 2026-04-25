from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=2, min=4, max=20),
    reraise=True
)
def safe_agent_call(structured_llm, prompt_messages):
    """
    Ensures that if a provider fails or rate limits, the agent 
    waits and retries up to 3 times.
    """
    try:
        return structured_llm.invoke(prompt_messages)
    except Exception as e:
        logger.error(f"❌ LLM Call Failed: {e}. Retrying...")
        raise e