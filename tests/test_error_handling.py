from app.core.config_loader import get_config
from app.core.logger import logger

def test_error_handling():
    print("--- Testing Error Handling for Missing Knowledge Base ---")
    try:
        # Clear cache for testing
        get_config.cache_clear()
        
        config = get_config("config/settings_test_error.yaml")
        print("\nConfig loaded successfully even with missing knowledge base.")
        print(f"System Prompt: '{config.system_prompt}'")
        
        if "ADDITIONAL KNOWLEDGE BASE CONTEXT" not in config.system_prompt:
            print("\nSUCCESS: Application didn't crash and system prompt remained clean.")
        else:
            print("\nFAILURE: System prompt contains context injection even though file is missing?")
            
    except Exception as e:
        print(f"\nCRITICAL FAILURE: Application crashed: {e}")

if __name__ == "__main__":
    test_error_handling()
