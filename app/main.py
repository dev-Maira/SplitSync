from fastapi import FastAPI
from app.api import auth, groups
from app.api import auth, groups, expenses, balances, settlements

app = FastAPI(
    title="Finance",
    description="Asynchronous RESTful API for Expense Splitting",
    version="1.0.0"
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(groups.router, prefix="/groups", tags=["Groups"])
app.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
app.include_router(balances.router, prefix="/balances", tags=["Balances"])
app.include_router(settlements.router, prefix="/settlements", tags=["Settlements"])

@app.get("/")
def main():
    return {"SplitSync — Expense Splitter API"}