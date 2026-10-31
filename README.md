# 💰 Expense Tracker — Pure Python Financial Analytics System

A **pure Python** personal finance and expense-management program. **No web server, no browser, and no web UI required.** Everything runs directly in Python via an interactive terminal CLI and Python visualization tools.

---

## 📌 Problem Statement & Solution

Managing personal expenses manually can be difficult and time-consuming. People spend on various categories (Food, Transportation, Shopping, Bills, Entertainment, Education, Healthcare), but often lack an accurate record. 

Without a system, it is difficult to:
- Understand where money goes
- Control unnecessary and discretionary spending
- Track monthly budgets
- Plan savings

This **Expense Tracker** provides a complete, easy-to-use Python solution to record, categorize, monitor, and analyze income and expenses.

---

## 🎯 Main Objectives & Features Implemented

| # | Objective | Implementation in this Python Program |
|---|---|---|
| **1** | **Record Transactions** | Add income and expense transactions with amount, date, category, and description notes. |
| **2** | **Categorize Expenses** | Pre-built categories (Food, Transportation, Shopping, Bills, Entertainment, Healthcare, Education, etc.) plus custom category creation. |
| **3** | **Track Complete History** | Full transaction history with clean formatted tables, pagination, and timestamps. |
| **4** | **Calculate Balance** | Automatically calculates Total Income, Total Expenses, Remaining Balance, and Savings Rate %. |
| **5** | **Set Budgets** | Set and update monthly spending limits globally ("Overall") or category-wise. |
| **6** | **Monitor Spending** | Real-time budget monitoring with utilization bars and status alerts (`[SAFE]`, `[WARN 80%+]`, `[OVER BUDGET!]`). |
| **7** | **Generate Reports** | Daily summary, Weekly summary, Monthly trends, and Custom Date Range financial reports. |
| **8** | **Visualize Data** | **Both** Terminal ASCII horizontal bar charts and Python Matplotlib graphical charts (Pie/Donut charts, grouped bar charts, and 4-in-1 Dashboard). |
| **9** | **Search & Filter** | Search transactions by keyword, filter by type (income/expense), date range, and min/max amount. |
| **10** | **Improve Financial Awareness** | Built-in **50/30/20 Rule** analyzer (Needs vs Wants vs Savings), discretionary spending alerts, and smart budgeting recommendations. |

---

## 📊 Example Scenario (Built-in Problem Statement Example)

Suppose a user has:
- **Monthly Income:** ₹40,000
- **Food:** ₹6,000
- **Transportation:** ₹3,000
- **Shopping:** ₹5,000
- **Bills:** ₹7,000
- **Entertainment:** ₹2,000

The system automatically calculates:
- **Total Expenses:** ₹23,000
- **Remaining Balance:** ₹40,000 − ₹23,000 = **₹17,000** (Savings Rate: **42.5%**)

You can reload this example data at any time from the menu (`Option 13`) or with `python main.py --reset-example`.

---

## 🚀 How to Run

### 1. Interactive Terminal Mode (Main Program)
Run the application directly:
```bash
python main.py
```
This opens the clean interactive menu:
```text
+--------------------------------------------------------------+
|             EXPENSE TRACKER & FINANCIAL ANALYTICS            |
+--------------------------------------------------------------+
 Income: ₹40,000.00  |  Expenses: ₹23,000.00  |  Balance: ₹17,000.00 (42.5%)
----------------------------------------------------------------
  [1]  Add Income (Record Salary, Freelance, etc.)
  [2]  Add Expense (Food, Bills, Shopping, Travel, etc.)
  [3]  View All Transactions (Full History)
  [4]  Search & Filter Transactions (Date, Category, Amount)
  [5]  Financial Balance & Category Breakdown
  [6]  Monthly Budget Tracker & Spending Alerts
  [7]  Edit a Transaction
  [8]  Delete a Transaction
  [9]  Generate Financial Reports (Daily, Weekly, Monthly)
  [10] Visualize Data (Terminal Bars & Matplotlib Charts)
  [11] Financial Awareness & Smart Budgeting Insights
  [12] Export Transactions to CSV
  [13] Load Problem Statement Example (₹40,000 Income / ₹23,000 Expenses)
  [0]  Exit Application
----------------------------------------------------------------
Select an option (0-13):
```

### 2. Command-Line Shortcuts
You can also run quick operations directly from the command line:

```bash
# Print quick balance and financial overview
python main.py --summary

# Display financial reports
python main.py --report daily
python main.py --report weekly
python main.py --report monthly

# Render terminal visual spending charts
python main.py --chart

# Show 50/30/20 financial awareness & budgeting recommendations
python main.py --insights

# Reset database to problem statement sample
python main.py --reset-example
```

---

## 📁 Project Structure

```text
Expense Tracker/
├── main.py            # Main entry point for the Python application
├── cli.py             # Interactive terminal interface & menu navigation
├── database.py        # SQLite database operations, queries, and calculations
├── visualizer.py      # ASCII terminal bar charts & Matplotlib graphical figures
├── insights.py        # Financial awareness engine (50/30/20 rule & recommendations)
├── reports.py         # Daily, weekly, monthly, and custom financial reports
├── requirements.txt   # Python dependencies (matplotlib optional for GUI charts)
├── expenses.db        # SQLite database (auto-created on first run)
└── README.md          # Complete documentation
```

---

## 🛠️ Requirements & Installation

- **Python 3.8+**
- The core program runs **100% on the Python Standard Library** (`sqlite3`, `csv`, `datetime`, `os`, `sys`).
- Optional for GUI popup charts and PNG export:
  ```bash
  pip install matplotlib
  ```
  *(If Matplotlib is not installed, the program automatically displays beautiful ASCII bar charts right in the terminal!)*

---

## 🔒 Data Persistence & Export

All transactions, categories, and budgets are persisted locally in SQLite (`expenses.db`). You can export your full transaction records to a CSV spreadsheet anytime via **Option 12** in the menu.
