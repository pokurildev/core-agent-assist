import re
from typing import Any, Dict, Type
from pydantic import create_model, Field

def to_snake_case(name: str) -> str:
    """
    Конвертирует строку в snake_case, удаляя лишние пробелы и символы.
    Гарантирует, что результат является валидным идентификатором Python.
    """
    # 1. Заменяем любые символы, кроме букв, цифр и подчеркиваний, на подчеркивания
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    
    # 2. Вставляем подчеркивание перед заглавными буквами (CamelCase -> snake_case)
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    # 3. Заменяем множественные подчеркивания на одно
    result = re.sub(r'_+', '_', s2).strip('_')
    
    # 4. Если строка начинается с цифры, добавляем подчеркивание в начало
    if result and result[0].isdigit():
        result = f'_{result}'
        
    return result or "field"

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
