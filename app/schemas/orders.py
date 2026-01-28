from pydantic import BaseModel
from datetime import datetime

class Order(BaseModel):
    id: str
    customer_name: str
    phone: str
    status: str
    created_at: datetime
