from app.core.utils import create_dynamic_model
from app.services.tools_registry import generate_vapi_tool_schema
import json

def test_dynamic_tools():
    print("--- Testing Dynamic Tool Factory ---")
    
    # 1. Тест создания динамической модели
    fields = {
        "User Name": "The full name of the user",
        "orderNumber": "The ID of the order"
    }
    DynamicModel = create_dynamic_model("TestModel", fields)
    print(f"Model created: {DynamicModel.__name__}")
    
    # Проверка имен полей (должны быть в snake_case)
    instance = DynamicModel(user_name="John Doe", order_number="12345")
    print(f"Instance created: {instance}")
    assert hasattr(instance, "user_name")
    assert hasattr(instance, "order_number")

    # 2. Тест генерации схемы для VAPI
    schema = generate_vapi_tool_schema()
    print("\n--- Generated Tool Schema ---")
    print(json.dumps(schema, indent=2, ensure_ascii=False))
    
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "submit_collected_data"
    assert "customer_name" in schema["function"]["parameters"]["properties"]
    assert "customer_email" in schema["function"]["parameters"]["properties"]
    
    print("\nSUCCESS: Dynamic Tool Factory verified!")

if __name__ == "__main__":
    test_dynamic_tools()
