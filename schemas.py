from pydantic import BaseModel
from typing import List
from datetime import datetime

class StockCreate(BaseModel):
    name: str
    quantity: int
    current_price: float

class LoanRequest(BaseModel):
    user_name: str
    amount: float

class TradeRequest(BaseModel):
    user_name: str
    stock_name: str
    quantity: int

class UserReport(BaseModel):
    user: str
    profit_loss: float

class StockReport(BaseModel):
    stock: str
    trend: float

class StockPrice(BaseModel):
    timestamp: datetime
    price: float
