from app.core.config_loader import get_config
import json

def test_loading():
    print("--- Testing Config Loading ---")
    try:
        config = get_config()
        print(f"Project Settings Loaded: {config.voice_settings.provider} - {config.voice_settings.voice_id}")
        
        print("\n--- System Prompt with Context Injection ---")
        print(config.system_prompt)
        
        if "ADDITIONAL KNOWLEDGE BASE CONTEXT" in config.system_prompt:
            print("\nSUCCESS: Context Injection verified!")
        else:
            print("\nFAILURE: Context Injection missing!")
            
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    test_loading()
