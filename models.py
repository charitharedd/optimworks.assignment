from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    _tablename_ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    balance = Column(Float, default=100000.0)
    loan = Column(Float, default=0.0)
    transactions = relationship("Transaction", back_populates="user")

class Stock(Base):
    _tablename_ = "stocks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    quantity = Column(Integer)
    current_price = Column(Float)
    history = relationship("StockPriceHistory", back_populates="stock")

class StockPriceHistory(Base):
    _tablename_ = "stock_price_history"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    price = Column(Float)
    stock = relationship("Stock", back_populates="history")

class Transaction(Base):
    _tablename_ = "transactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    type = Column(String)  # buy/sell
    quantity = Column(Integer)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="transactions")
