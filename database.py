"""
Database module for Expense Tracker.
Handles SQLite operations, data persistence, transactions CRUD,
budget management, search/filter queries, and financial report calculations.
"""

import sqlite3
import os
from datetime import datetime, timedelta

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.db")

def get_connection(db_path=DEFAULT_DB_PATH):
    """Establish connection to SQLite database with row factory enabled."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(db_path=DEFAULT_DB_PATH, seed_if_empty=True):
    """Initialize database tables and indexes."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Transactions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                date TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Budgets Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT UNIQUE NOT NULL,
                monthly_limit REAL NOT NULL CHECK(monthly_limit > 0),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Indexes for fast querying
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trans_date ON transactions(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trans_type ON transactions(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trans_category ON transactions(category)")
        
        conn.commit()

        # Seed sample data if empty
        if seed_if_empty:
            cursor.execute("SELECT COUNT(*) FROM transactions")
            if cursor.fetchone()[0] == 0:
                seed_default_data(db_path)

def seed_default_data(db_path=DEFAULT_DB_PATH):
    """
    Seed sample data matching the exact Problem Statement example:
    Monthly Income: ₹40,000
    Expenses:
      - Food: ₹6,000
      - Transportation: ₹3,000
      - Shopping: ₹5,000
      - Bills: ₹7,000
      - Entertainment: ₹2,000
    Total Expenses = ₹23,000
    Remaining Balance = ₹17,000
    """
    today = datetime.now()
    current_month = today.strftime("%Y-%m")
    
    sample_transactions = [
        # Income
        ("income", "Salary", 40000.0, f"{current_month}-01", "Monthly Salary Deposit"),
        # Expenses as specified in problem statement
        ("expense", "Food", 6000.0, f"{current_month}-04", "Groceries, Supermarket & Dining"),
        ("expense", "Transportation", 3000.0, f"{current_month}-07", "Metro pass, Fuel & Cab rides"),
        ("expense", "Shopping", 5000.0, f"{current_month}-12", "Clothes & Electronic accessories"),
        ("expense", "Bills", 7000.0, f"{current_month}-15", "Electricity, High-speed Internet & Water"),
        ("expense", "Entertainment", 2000.0, f"{current_month}-18", "Movie night & Streaming subscriptions")
    ]
    
    sample_budgets = [
        ("Overall", 30000.0),
        ("Food", 7000.0),
        ("Transportation", 4000.0),
        ("Shopping", 6000.0),
        ("Bills", 8000.0),
        ("Entertainment", 3000.0),
        ("Healthcare", 2500.0)
    ]
    
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        for t_type, cat, amt, dt, desc in sample_transactions:
            cursor.execute("""
                INSERT INTO transactions (type, category, amount, date, description)
                VALUES (?, ?, ?, ?, ?)
            """, (t_type, cat, amt, dt, desc))
            
        for cat, limit in sample_budgets:
            cursor.execute("""
                INSERT OR REPLACE INTO budgets (category, monthly_limit)
                VALUES (?, ?)
            """, (cat, limit))
            
        conn.commit()

# --- Transaction CRUD Operations ---

def add_transaction(t_type, category, amount, date=None, description="", db_path=DEFAULT_DB_PATH):
    """Insert a new transaction."""
    t_type = t_type.lower().strip()
    if t_type not in ('income', 'expense'):
        raise ValueError("Transaction type must be 'income' or 'expense'")
    amount = float(amount)
    if amount <= 0:
        raise ValueError("Amount must be greater than zero")
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
        
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (type, category, amount, date, description)
            VALUES (?, ?, ?, ?, ?)
        """, (t_type, category.strip(), amount, date.strip(), description.strip()))
        conn.commit()
        return cursor.lastrowid

def update_transaction(tx_id, t_type, category, amount, date, description="", db_path=DEFAULT_DB_PATH):
    """Update an existing transaction."""
    t_type = t_type.lower().strip()
    if t_type not in ('income', 'expense'):
        raise ValueError("Transaction type must be 'income' or 'expense'")
    amount = float(amount)
    if amount <= 0:
        raise ValueError("Amount must be greater than zero")
        
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE transactions
            SET type = ?, category = ?, amount = ?, date = ?, description = ?
            WHERE id = ?
        """, (t_type, category.strip(), amount, date.strip(), description.strip(), tx_id))
        conn.commit()
        return cursor.rowcount > 0

def delete_transaction(tx_id, db_path=DEFAULT_DB_PATH):
    """Delete a transaction by ID."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_transaction(tx_id, db_path=DEFAULT_DB_PATH):
    """Fetch a single transaction by ID."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_transactions(
    t_type=None,
    category=None,
    search=None,
    start_date=None,
    end_date=None,
    min_amount=None,
    max_amount=None,
    sort_by="date",
    order="DESC",
    limit=None,
    offset=0,
    db_path=DEFAULT_DB_PATH
):
    """Search, filter, and paginate transactions."""
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []
    
    if t_type and t_type.lower() != 'all':
        query += " AND type = ?"
        params.append(t_type.lower())
        
    if category and category.lower() != 'all':
        query += " AND category = ?"
        params.append(category)
        
    if search:
        query += " AND (description LIKE ? OR category LIKE ?)"
        search_param = f"%{search.strip()}%"
        params.extend([search_param, search_param])
        
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
        
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
        
    if min_amount is not None and str(min_amount).strip() != "":
        query += " AND amount >= ?"
        params.append(float(min_amount))
        
    if max_amount is not None and str(max_amount).strip() != "":
        query += " AND amount <= ?"
        params.append(float(max_amount))
        
    # Sorting
    allowed_sorts = {"date": "date", "amount": "amount", "category": "category", "type": "type", "id": "id"}
    sort_column = allowed_sorts.get(sort_by, "date")
    sort_order = "ASC" if str(order).upper() == "ASC" else "DESC"
    
    query += f" ORDER BY {sort_column} {sort_order}, id DESC"
    
    if limit is not None:
        query += " LIMIT ? OFFSET ?"
        params.extend([int(limit), int(offset)])
        
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

# --- Analytics, Summaries and Calculations ---

def get_financial_summary(start_date=None, end_date=None, db_path=DEFAULT_DB_PATH):
    """
    Calculate total income, total expenses, balance, and savings rate.
    Can be filtered by date range.
    """
    query = """
        SELECT 
            type,
            COALESCE(SUM(amount), 0) as total,
            COUNT(*) as count
        FROM transactions
        WHERE 1=1
    """
    params = []
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
        
    query += " GROUP BY type"
    
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
    totals = {"income": 0.0, "expense": 0.0, "income_count": 0, "expense_count": 0}
    for row in rows:
        totals[row["type"]] = float(row["total"])
        totals[f"{row['type']}_count"] = int(row["count"])
        
    balance = totals["income"] - totals["expense"]
    savings_rate = (balance / totals["income"] * 100) if totals["income"] > 0 else 0.0
    
    return {
        "total_income": round(totals["income"], 2),
        "total_expenses": round(totals["expense"], 2),
        "remaining_balance": round(balance, 2),
        "savings_rate": round(savings_rate, 1),
        "income_count": totals["income_count"],
        "expense_count": totals["expense_count"],
        "total_count": totals["income_count"] + totals["expense_count"]
    }

def get_category_breakdown(t_type="expense", start_date=None, end_date=None, db_path=DEFAULT_DB_PATH):
    """
    Group transactions by category and calculate total and percentage.
    """
    query = """
        SELECT 
            category,
            SUM(amount) as total,
            COUNT(*) as transaction_count
        FROM transactions
        WHERE type = ?
    """
    params = [t_type.lower()]
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
        
    query += " GROUP BY category ORDER BY total DESC"
    
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
    result = []
    grand_total = sum(row["total"] for row in rows)
    
    for row in rows:
        amount = float(row["total"])
        pct = (amount / grand_total * 100) if grand_total > 0 else 0.0
        result.append({
            "category": row["category"],
            "total": round(amount, 2),
            "count": row["transaction_count"],
            "percentage": round(pct, 1)
        })
        
    return result

def get_daily_summary(days=7, db_path=DEFAULT_DB_PATH):
    """
    Calculate daily financial summary for the last N days.
    Returns date, income, expense, net balance, and transaction count.
    """
    start_date = (datetime.now() - timedelta(days=days-1)).strftime("%Y-%m-%d")
    query = """
        SELECT 
            date,
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expense,
            COUNT(*) as tx_count
        FROM transactions
        WHERE date >= ?
        GROUP BY date
        ORDER BY date DESC
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (start_date,))
        rows = cursor.fetchall()
        
    data = []
    for r in rows:
        inc = float(r["income"])
        exp = float(r["expense"])
        data.append({
            "date": r["date"],
            "income": round(inc, 2),
            "expense": round(exp, 2),
            "net": round(inc - exp, 2),
            "count": int(r["tx_count"])
        })
    return data

def get_weekly_summary(weeks=4, db_path=DEFAULT_DB_PATH):
    """
    Calculate weekly summary aggregated by calendar week for the last N weeks.
    """
    days = weeks * 7
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    query = """
        SELECT 
            strftime('%Y-W%W', date) as week_str,
            MIN(date) as week_start,
            MAX(date) as week_end,
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expense,
            COUNT(*) as tx_count
        FROM transactions
        WHERE date >= ?
        GROUP BY week_str
        ORDER BY week_str DESC
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (start_date,))
        rows = cursor.fetchall()
        
    data = []
    for r in rows:
        inc = float(r["income"])
        exp = float(r["expense"])
        data.append({
            "week": r["week_str"],
            "period": f"{r['week_start']} to {r['week_end']}",
            "income": round(inc, 2),
            "expense": round(exp, 2),
            "net": round(inc - exp, 2),
            "count": int(r["tx_count"])
        })
    return data

def get_monthly_summary(months=6, db_path=DEFAULT_DB_PATH):
    """
    Calculate monthly trends and comparisons for the last N months.
    """
    query = """
        SELECT 
            strftime('%Y-%m', date) as month,
            type,
            SUM(amount) as total,
            COUNT(*) as count
        FROM transactions
        GROUP BY month, type
        ORDER BY month ASC
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        
    data_by_month = {}
    for row in rows:
        m = row["month"]
        if m not in data_by_month:
            data_by_month[m] = {
                "month": m, 
                "income": 0.0, 
                "expense": 0.0, 
                "balance": 0.0, 
                "savings_rate": 0.0,
                "tx_count": 0
            }
        t = row["type"]
        amt = float(row["total"])
        cnt = int(row["count"])
        data_by_month[m][t] = amt
        data_by_month[m]["tx_count"] += cnt

    for m in data_by_month:
        inc = data_by_month[m]["income"]
        exp = data_by_month[m]["expense"]
        bal = inc - exp
        rate = (bal / inc * 100) if inc > 0 else 0.0
        data_by_month[m]["balance"] = round(bal, 2)
        data_by_month[m]["savings_rate"] = round(rate, 1)

    sorted_months = sorted(data_by_month.values(), key=lambda x: x["month"])
    return sorted_months[-months:] if months else sorted_months

# --- Budget Management ---

def set_budget(category, monthly_limit, db_path=DEFAULT_DB_PATH):
    """Create or update a budget limit."""
    category = category.strip()
    limit = float(monthly_limit)
    if limit <= 0:
        raise ValueError("Budget limit must be greater than zero")
        
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO budgets (category, monthly_limit)
            VALUES (?, ?)
            ON CONFLICT(category) DO UPDATE SET monthly_limit = excluded.monthly_limit
        """, (category, limit))
        conn.commit()
        return True

def delete_budget(category, db_path=DEFAULT_DB_PATH):
    """Delete a budget setting."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM budgets WHERE LOWER(category) = LOWER(?)", (category.strip(),))
        conn.commit()
        return cursor.rowcount > 0

def get_budgets(db_path=DEFAULT_DB_PATH):
    """Retrieve all budget definitions."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM budgets ORDER BY category ASC")
        return [dict(row) for row in cursor.fetchall()]

def get_budget_status(month_str=None, db_path=DEFAULT_DB_PATH):
    """
    Compare spending against monthly budgets for the specified month (format 'YYYY-MM').
    Defaults to current month, or the most recent month containing transactions.
    """
    if not month_str:
        cur_m = datetime.now().strftime("%Y-%m")
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM transactions WHERE date LIKE ?", (f"{cur_m}%",))
            if cursor.fetchone()[0] > 0:
                month_str = cur_m
            else:
                cursor.execute("SELECT SUBSTR(date, 1, 7) FROM transactions ORDER BY date DESC LIMIT 1")
                row = cursor.fetchone()
                month_str = row[0] if row and row[0] else cur_m
        
    budgets = get_budgets(db_path)
    
    # Calculate spending by category for this month
    query = """
        SELECT 
            category,
            SUM(amount) as spent
        FROM transactions
        WHERE type = 'expense' AND date LIKE ?
        GROUP BY category
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (f"{month_str}%",))
        spending_rows = cursor.fetchall()
        
        # Total overall expenses this month
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM transactions
            WHERE type = 'expense' AND date LIKE ?
        """, (f"{month_str}%",))
        total_monthly_expense = float(cursor.fetchone()[0])
        
    spent_map = {row["category"].lower(): float(row["spent"]) for row in spending_rows}
    
    status_list = []
    for b in budgets:
        cat = b["category"]
        limit = float(b["monthly_limit"])
        
        if cat.lower() == "overall":
            spent = total_monthly_expense
        else:
            spent = spent_map.get(cat.lower(), 0.0)
            
        remaining = limit - spent
        pct = round((spent / limit * 100), 1) if limit > 0 else 0.0
        
        if spent > limit:
            flag = "exceeded"
        elif spent >= 0.8 * limit:
            flag = "warning"
        else:
            flag = "safe"
            
        status_list.append({
            "category": cat,
            "monthly_limit": round(limit, 2),
            "spent": round(spent, 2),
            "remaining": round(remaining, 2),
            "percentage": pct,
            "status": flag
        })
        
    return {
        "month": month_str,
        "total_spent": round(total_monthly_expense, 2),
        "budgets": status_list
    }

def get_all_categories(db_path=DEFAULT_DB_PATH):
    """Get all unique categories currently in use plus standard default categories."""
    default_expense = [
        "Food", "Transportation", "Shopping", "Bills", "Entertainment",
        "Healthcare", "Education", "Groceries", "Personal Care", "Travel", "Utilities", "Other"
    ]
    default_income = [
        "Salary", "Freelance", "Business", "Investments", "Rental", "Gifts", "Other Income"
    ]
    
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category, type FROM transactions")
        rows = cursor.fetchall()
        
    expense_cats = set(default_expense)
    income_cats = set(default_income)
    
    for r in rows:
        if r["type"] == "expense":
            expense_cats.add(r["category"])
        else:
            income_cats.add(r["category"])
            
    return {
        "expense": sorted(list(expense_cats)),
        "income": sorted(list(income_cats))
    }

def reset_database(db_path=DEFAULT_DB_PATH):
    """Reset the database and re-seed defaults with problem statement example."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS transactions")
        cursor.execute("DROP TABLE IF EXISTS budgets")
        conn.commit()
    init_db(db_path, seed_if_empty=True)
