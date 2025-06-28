from sqlalchemy.orm import Session
from models import Stock, StockPriceHistory
import random
from datetime import datetime
from threading import Thread
import time

def update_stock_prices(db: Session):
    stocks = db.query(Stock).all()
    for stock in stocks:
        new_price = round(random.uniform(1, 100), 2)
        stock.current_price = new_price
        db.add(StockPriceHistory(stock_id=stock.id, price=new_price))
    db.commit()

def simulate_users(db_factory):
    def simulate():
        from models import User, Stock, Transaction
        db = db_factory()
        users = db.query(User).all()
        stocks = db.query(Stock).all()

        for _ in range(10):  # simulate 10 rounds
            for user in users:
                stock = random.choice(stocks)
                action = random.choice(["buy", "sell"])
                qty = random.randint(1, 5)

                if action == "buy" and user.balance >= stock.current_price * qty:
                    user.balance -= stock.current_price * qty
                    db.add(Transaction(user_id=user.id, stock_id=stock.id, type="buy", quantity=qty, price=stock.current_price))
                elif action == "sell":
                    user.balance += stock.current_price * qty
                    db.add(Transaction(user_id=user.id, stock_id=stock.id, type="sell", quantity=qty, price=stock.current_price))
        db.commit()
        db.close()
    Thread(target=simulate).start()
