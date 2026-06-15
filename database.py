import sqlite3
from datetime import datetime

DB_NAME = "expenses.db"

def get_connection():
    """Create and return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    """Create tables if they don't exist yet."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            currency    TEXT    NOT NULL DEFAULT 'INR',
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            notes       TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category    TEXT    NOT NULL UNIQUE,
            budget_limit REAL   NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ─── EXPENSES CRUD ────────────────────────────────────────────

def add_expense(title, amount, currency, category, date, notes=""):
    """Insert a new expense into the database."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO expenses (title, amount, currency, category, date, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, amount, currency, category, date, notes))
    conn.commit()
    conn.close()


def get_all_expenses():
    """Return all expenses as a list, newest first."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM expenses ORDER BY date DESC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_expense(expense_id, title, amount, currency, category, date, notes=""):
    """Update an existing expense by ID."""
    conn = get_connection()
    conn.execute("""
        UPDATE expenses
        SET title=?, amount=?, currency=?, category=?, date=?, notes=?
        WHERE id=?
    """, (title, amount, currency, category, date, notes, expense_id))
    conn.commit()
    conn.close()


def delete_expense(expense_id):
    """Delete an expense by ID."""
    conn = get_connection()
    conn.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()


# ─── BUDGETS CRUD ─────────────────────────────────────────────

def set_budget(category, limit):
    """Insert or update a budget limit for a category."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO budgets (category, budget_limit)
        VALUES (?, ?)
        ON CONFLICT(category) DO UPDATE SET budget_limit=excluded.budget_limit
    """, (category, limit))
    conn.commit()
    conn.close()


def get_budgets():
    """Return all category budgets as a dict {category: limit}."""
    conn = get_connection()
    rows = conn.execute("SELECT category, budget_limit FROM budgets").fetchall()
    conn.close()
    return {row["category"]: row["budget_limit"] for row in rows}


# ─── Quick test ───────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized successfully!")
    print("📁 File created: expenses.db")