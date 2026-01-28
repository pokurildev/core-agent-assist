import pytest
from pydantic import ValidationError
from app.services.tools_registry import get_dynamic_tool_schema

def test_schema_generation_valid_fields():
    """
    Test that valid fields generate a correct OpenAI-compatible schema.
    """
    # Input mimicking admin config
    fields = {
        "user_name": "Name of the client",
        "service_type": "Type of haircut"
    }
    
    schema = get_dynamic_tool_schema(fields)
    
    # Assertions
    assert isinstance(schema, dict)
    assert schema["type"] == "function"
    assert "function" in schema
    
    func_data = schema["function"]
    assert func_data["name"] == "collect_customer_data"
    assert "description" in func_data
    
    parameters = func_data["parameters"]
    assert parameters["type"] == "object"
    
    properties = parameters["properties"]
    assert "user_name" in properties
    assert "service_type" in properties
    assert len(properties) == 2
    
    # Verify descriptions match
    assert properties["user_name"]["description"] == "Name of the client"
    assert properties["service_type"]["description"] == "Type of haircut"

def test_schema_structure_vapi_compliance():
    """
    Verify the strict VAPI structure compliance.
    """
    fields = {"customer_email": "Official email"}
    schema = get_dynamic_tool_schema(fields)
    
    params = schema["function"]["parameters"]
    assert params["type"] == "object"
    
    # Check that required contains the generated fields
    assert "customer_email" in params["required"]
    assert len(params["required"]) == 1

def test_schema_generation_empty_config():
    """
    Ensure the generator handles an empty configuration gracefully.
    """
    schema = get_dynamic_tool_schema({})
    
    assert isinstance(schema, dict)
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "collect_customer_data"
    
    # Expected behavior: valid schema with empty properties
    assert schema["function"]["parameters"]["properties"] == {}
    assert schema["function"]["parameters"]["required"] == []

def test_snake_case_preservation():
    """
    Verify that snake_case keys are preserved correctly in the schema.
    """
    fields = {"first_name": "User's first name", "Last_Name": "User's last name"}
    schema = get_dynamic_tool_schema(fields)
    
    properties = schema["function"]["parameters"]["properties"]
    
    # Our to_snake_case in utils.py might modify "Last_Name" to "last_name"
    # Let's check what actually happens based on our implementation
    assert "first_name" in properties
    assert "last_name" in properties  # "Last_Name" becomes "last_name" in to_snake_case
