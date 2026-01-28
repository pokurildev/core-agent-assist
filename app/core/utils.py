import re
from typing import Any, Dict, Type
from pydantic import create_model, Field

def to_snake_case(name: str) -> str:
    """Конвертирует строку в snake_case, удаляя лишние пробелы и символы."""
    # Заменяем пробелы и дефисы на подчеркивания
    name = re.sub(r'[\s-]+', '_', name)
    # Вставляем подчеркивание перед заглавными буквами (CamelCase -> snake_case)
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    # Заменяем множественные подчеркивания на одно
    return re.sub(r'_+', '_', s2).strip('_')

def create_dynamic_model(model_name: str, fields: Dict[str, str]) -> Type:
    """
    Динамически создает Pydantic-модель на основе словаря полей.
    fields: { field_name: description }
    """
    pydantic_fields = {}
    for name, description in fields.items():
        snake_name = to_snake_case(name)
        # Все поля по умолчанию строковые и обязательные для вызова функции LLM
        pydantic_fields[snake_name] = (str, Field(..., description=description))
    
    return create_model(model_name, **pydantic_fields)
