from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas
from utils import update_stock_prices, simulate_users
from fastapi_utils.tasks import repeat_every

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Stock Trading Simulator")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/stocks/register")
def register_stock(stock: schemas.StockCreate, db: Session = Depends(get_db)):
    db_stock = models.Stock(name=stock.name, quantity=stock.quantity, current_price=stock.current_price)
    db.add(db_stock)
    db.commit()
    return {"msg": "Stock registered"}

@app.get("/stocks/history")
def stock_history(db: Session = Depends(get_db)):
    return db.query(models.StockPriceHistory).all()

@app.post("/users/loan")
def take_loan(loan: schemas.LoanRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.name == loan.user_name).first()
    if not user: return {"error": "User not found"}
    if user.loan + loan.amount > 100000:
        return {"error": "Loan limit exceeded"}
    user.loan += loan.amount
    user.balance += loan.amount
    db.commit()
    return {"msg": "Loan granted"}

@app.post("/users/buy")
def buy_stock(trade: schemas.TradeRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.name == trade.user_name).first()
    stock = db.query(models.Stock).filter(models.Stock.name == trade.stock_name).first()
    cost = stock.current_price * trade.quantity
    if user.balance >= cost and stock.quantity >= trade.quantity:
        user.balance -= cost
        stock.quantity -= trade.quantity
        db.add(models.Transaction(user_id=user.id, stock_id=stock.id, type="buy", quantity=trade.quantity, price=stock.current_price))
        db.commit()
        return {"msg": "Stock purchased"}
    return {"error": "Insufficient balance or stock"}

@app.post("/users/sell")
def sell_stock(trade: schemas.TradeRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.name == trade.user_name).first()
    stock = db.query(models.Stock).filter(models.Stock.name == trade.stock_name).first()
    user.balance += stock.current_price * trade.quantity
    stock.quantity += trade.quantity
    db.add(models.Transaction(user_id=user.id, stock_id=stock.id, type="sell", quantity=trade.quantity, price=stock.current_price))
    db.commit()
    return {"msg": "Stock sold"}

@app.get("/users/report")
def user_report(db: Session = Depends(get_db)):
    result = []
    users = db.query(models.User).all()
    for user in users:
        profit = 0
        for t in user.transactions:
            if t.type == "sell":
                profit += t.price * t.quantity
            else:
                profit -= t.price * t.quantity
        result.append({"user": user.name, "profit_loss": profit})
    return result

@app.get("/stocks/report")
def stock_report(db: Session = Depends(get_db)):
    result = []
    stocks = db.query(models.Stock).all()
    for stock in stocks:
        prices = [h.price for h in stock.history]
        if len(prices) >= 2:
            trend = prices[-1] - prices[0]
            result.append({"stock": stock.name, "trend": trend})
    return result

@app.get("/users/top")
def top_users(db: Session = Depends(get_db)):
    report = user_report(db)
    return sorted(report, key=lambda x: x["profit_loss"], reverse=True)[:5]

@app.get("/stocks/top")
def top_stocks(db: Session = Depends(get_db)):
    report = stock_report(db)
    return sorted(report, key=lambda x: x["trend"], reverse=True)[:5]

@app.get("/simulate")
def simulate(db: Session = Depends(get_db)):
    simulate_users(SessionLocal)
    return {"msg": "Simulation started"}

@app.on_event("startup")
@repeat_every(seconds=300)  # every 5 minutes
def periodic_price_update():
    db = SessionLocal()
    update_stock_prices(db)
    db.close()
