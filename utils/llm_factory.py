from utils.models.open_router.openrouter_config import get_smart_openrouter_model, get_fast_openrouter_model
from utils.models.groq.groq_config import get_smart_groq_model, get_fast_groq_model
from dotenv import load_dotenv

load_dotenv()

# --- OPTION A: All Groq (Ultra Fast) ---
SMART_MODEL = get_smart_groq_model()
FAST_MODEL = get_fast_groq_model()

# --- OPTION B: Hybrid (Best of both worlds) ---
# SMART_MODEL = get_smart_openrouter_model() # Use Claude 3.5 for the heavy lifting
# FAST_MODEL = get_fast_groq_model()          # Use Groq for the quick syntax checks

# --- OPTION C: All OpenRouter ---
# SMART_MODEL = get_smart_openrouter_model()
# FAST_MODEL = get_fast_openrouter_model() 