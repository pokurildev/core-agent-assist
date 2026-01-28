from typing import Any, Dict
from app.core.config_loader import get_config
from app.core.utils import create_dynamic_model

def get_dynamic_tool_schema(fields: Dict[str, str]) -> Dict[str, Any]:
    """
    Генерирует схему инструмента OpenAI-совместимого формата 
    на основе словаря полей.
    """
    if not fields:
        # Возвращаем структуру с пустыми параметрами, если полей нет
        return {
            "type": "function",
            "function": {
                "name": "collect_customer_data",
                "description": "Call this function only when ALL requested fields are gathered from the user.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }

    DynamicModel = create_dynamic_model("CollectedData", fields)
    schema = DynamicModel.model_json_schema()
    
    return {
        "type": "function",
        "function": {
            "name": "collect_customer_data",
            "description": "Call this function only when ALL requested fields are gathered from the user.",
            "parameters": {
                "type": "object",
                "properties": schema.get("properties", {}),
                "required": schema.get("required", [])
            }
        }
    }

def generate_vapi_tool_schema() -> Dict[str, Any]:
    """
    Генерирует схему на основе полей из текущей конфигурации.
    """
    settings = get_config()
    fields = settings.data_collection_fields
    
    if not fields:
        return {}

    return get_dynamic_tool_schema(fields)
