"""
Interactive Terminal CLI for Expense Tracker.
Pure Python Application - No Web Server, No Browser required.
Provides full transaction management, budget monitoring, financial awareness,
daily/weekly/monthly reporting, and data visualization (terminal & graphical charts).
"""

import sys
import os
import csv
from datetime import datetime

# Local project modules
import database
import visualizer
import insights
import reports

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ANSI Color codes for clean terminal output
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_header(title):
    print(f"\n{BOLD}{CYAN}{'='*68}{RESET}")
    print(f"{BOLD}{CYAN}  {title.center(64)}  {RESET}")
    print(f"{BOLD}{CYAN}{'='*68}{RESET}\n")

def format_currency(amount):
    return f"₹{amount:,.2f}"

def prompt_date(prompt_text="Enter date (YYYY-MM-DD) [press Enter for Today]: "):
    raw = input(prompt_text).strip()
    if not raw:
        return datetime.now().strftime("%Y-%m-%d")
    try:
        dt = datetime.strptime(raw, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        print(f"{YELLOW}Invalid date format! Using today's date.{RESET}")
        return datetime.now().strftime("%Y-%m-%d")

def prompt_amount(prompt_text="Enter amount (₹): "):
    while True:
        try:
            val = float(input(prompt_text).strip())
            if val <= 0:
                print(f"{RED}Amount must be greater than zero!{RESET}")
                continue
            return val
        except ValueError:
            print(f"{RED}Please enter a valid numeric value!{RESET}")

def prompt_category(t_type):
    categories = database.get_all_categories()[t_type]
    print(f"\n{YELLOW}Select a Category:{RESET}")
    for idx, cat in enumerate(categories, 1):
        print(f"  [{idx:2d}] {cat}")
    print(f"  [ 0] Custom Category (Type your own)...")
    
    while True:
        choice = input(f"\nChoose category number (0-{len(categories)}) or type name: ").strip()
        if choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(categories):
                return categories[num - 1]
            elif num == 0:
                custom = input("Enter new custom category name: ").strip()
                return custom if custom else ("Other Income" if t_type == "income" else "Other")
            else:
                print(f"{RED}Please select a valid option number.{RESET}")
        elif choice:
            return choice.title()

# --- Core Actions ---

def action_add_transaction(t_type):
    action_name = "Add Income" if t_type == "income" else "Add Expense"
    print_header(f"{action_name}")
    
    amount = prompt_amount()
    category = prompt_category(t_type)
    date_val = prompt_date()
    description = input("Enter description / note (optional): ").strip()
    
    tx_id = database.add_transaction(t_type, category, amount, date_val, description)
    print(f"\n{GREEN}[OK] Transaction recorded successfully! (ID: #{tx_id}){RESET}")
    
    # If expense, check budget limits
    if t_type == "expense":
        b_status = database.get_budget_status()
        for b in b_status.get("budgets", []):
            if b["category"].lower() == category.lower() or b["category"].lower() == "overall":
                if b["status"] == "exceeded":
                    print(f"\n{RED}[!] BUDGET ALERT: Spending for '{b['category']}' has EXCEEDED the monthly limit!{RESET}")
                    print(f"    Spent: {format_currency(b['spent'])} | Limit: {format_currency(b['monthly_limit'])} | Over by: {format_currency(abs(b['remaining']))}")
                elif b["status"] == "warning":
                    print(f"\n{YELLOW}[!] BUDGET NOTICE: 80%+ of '{b['category']}' budget reached.{RESET}")
                    print(f"    Spent: {format_currency(b['spent'])} | Limit: {format_currency(b['monthly_limit'])} | Remaining: {format_currency(b['remaining'])}")
                    
    input("\nPress Enter to return to menu...")

def display_transactions_table(txs, title="Transactions"):
    if not txs:
        print(f"\n{YELLOW}No transactions found matching the criteria.{RESET}\n")
        return
        
    print_header(title)
    header = f"{'ID':<5} | {'Date':<10} | {'Type':<8} | {'Category':<15} | {'Amount':<14} | {'Description'}"
    print(BOLD + header + RESET)
    print("-" * 80)
    
    for t in txs:
        is_inc = t["type"].lower() == "income"
        type_str = f"{GREEN}INCOME{RESET}" if is_inc else f"{RED}EXPENSE{RESET}"
        amt_color = GREEN if is_inc else RED
        amt_str = f"{amt_color}{format_currency(t['amount']):>14}{RESET}"
        desc = (t["description"] or "")[:25]
        print(f"{t['id']:<5} | {t['date']:<10} | {type_str:<17} | {t['category']:<15} | {amt_str} | {desc}")
    print("-" * 80)
    print(f"Total Transactions listed: {BOLD}{len(txs)}{RESET}\n")

def action_view_transactions():
    txs = database.get_transactions(sort_by="date", order="DESC")
    display_transactions_table(txs, "Transaction History")
    input("Press Enter to return to menu...")

def action_search_filter():
    print_header("Search & Filter Transactions")
    print("Leave any field blank to skip that specific filter.\n")
    
    search = input("Keyword search (searches category or description): ").strip()
    
    print("\nTransaction Type:")
    print("  [1] All Transactions")
    print("  [2] Income Only")
    print("  [3] Expenses Only")
    t_choice = input("Select type [1-3, default 1]: ").strip()
    t_type = "income" if t_choice == "2" else ("expense" if t_choice == "3" else None)
    
    start_date = input("Start Date (YYYY-MM-DD) [optional]: ").strip() or None
    end_date = input("End Date (YYYY-MM-DD) [optional]: ").strip() or None
    
    min_amt = input("Minimum Amount (₹) [optional]: ").strip()
    max_amt = input("Maximum Amount (₹) [optional]: ").strip()
    
    txs = database.get_transactions(
        t_type=t_type,
        search=search if search else None,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amt if min_amt else None,
        max_amount=max_amt if max_amt else None,
        sort_by="date",
        order="DESC"
    )
    
    display_transactions_table(txs, f"Filtered Results ({len(txs)} found)")
    input("Press Enter to return to menu...")

def action_edit_transaction():
    print_header("Edit Existing Transaction")
    tx_id_str = input("Enter Transaction ID to edit: ").strip()
    if not tx_id_str.isdigit():
        print(f"{RED}Invalid ID! Please enter a numeric ID.{RESET}")
        input("Press Enter...")
        return
        
    tx_id = int(tx_id_str)
    tx = database.get_transaction(tx_id)
    if not tx:
        print(f"{RED}Transaction #{tx_id} not found.{RESET}")
        input("Press Enter...")
        return
        
    print(f"\nCurrent Transaction details:")
    print(f"  ID:          #{tx['id']}")
    print(f"  Type:        {tx['type'].upper()}")
    print(f"  Category:    {tx['category']}")
    print(f"  Amount:      {format_currency(tx['amount'])}")
    print(f"  Date:        {tx['date']}")
    print(f"  Description: {tx['description']}")
    print("-" * 45)
    print("Press Enter without typing to keep the existing value.\n")
    
    raw_type = input(f"New Type (income/expense) [{tx['type']}]: ").strip().lower()
    t_type = raw_type if raw_type in ("income", "expense") else tx['type']
    
    raw_cat = input(f"New Category [{tx['category']}]: ").strip()
    category = raw_cat.title() if raw_cat else tx['category']
    
    raw_amt = input(f"New Amount (₹) [{tx['amount']}]: ").strip()
    amount = float(raw_amt) if raw_amt else tx['amount']
    
    raw_date = input(f"New Date (YYYY-MM-DD) [{tx['date']}]: ").strip()
    date_val = raw_date if raw_date else tx['date']
    
    raw_desc = input(f"New Description [{tx['description']}]: ").strip()
    description = raw_desc if raw_desc else tx['description']
    
    database.update_transaction(tx_id, t_type, category, amount, date_val, description)
    print(f"\n{GREEN}[OK] Transaction #{tx_id} successfully updated!{RESET}")
    input("\nPress Enter to return to menu...")

def action_delete_transaction():
    print_header("Delete Transaction")
    tx_id_str = input("Enter Transaction ID to delete: ").strip()
    if not tx_id_str.isdigit():
        print(f"{RED}Invalid ID! Please enter a numeric ID.{RESET}")
        input("Press Enter...")
        return
        
    tx_id = int(tx_id_str)
    tx = database.get_transaction(tx_id)
    if not tx:
        print(f"{RED}Transaction #{tx_id} not found.{RESET}")
        input("Press Enter...")
        return
        
    print(f"\nFound: #{tx['id']} | {tx['type'].upper()} | {tx['category']} | {format_currency(tx['amount'])} on {tx['date']}")
    print(f"Note:  {tx['description']}")
    confirm = input(f"\n{YELLOW}Are you sure you want to permanently delete this transaction? (y/N): {RESET}").strip().lower()
    if confirm == "y":
        database.delete_transaction(tx_id)
        print(f"\n{GREEN}[OK] Transaction #{tx_id} deleted successfully.{RESET}")
    else:
        print("\nDeletion cancelled.")
    input("\nPress Enter to return to menu...")

def action_financial_summary():
    print_header("Financial Balance & Category Summary")
    
    print("Select Timeframe:")
    print("  [1] All-Time (Default)")
    print("  [2] Current Month")
    print("  [3] Custom Date Range")
    ch = input("Enter choice [1-3, default 1]: ").strip()
    
    start_date, end_date = None, None
    if ch == "2":
        start_date = datetime.now().strftime("%Y-%m-01")
        end_date = datetime.now().strftime("%Y-%m-%d")
    elif ch == "3":
        start_date = input("Start Date (YYYY-MM-DD): ").strip() or None
        end_date = input("End Date (YYYY-MM-DD): ").strip() or None
        
    summary = database.get_financial_summary(start_date=start_date, end_date=end_date)
    
    print(f"\n{BOLD}{'Financial Metric':<32} | {'Value'}{RESET}")
    print("-" * 52)
    print(f"{GREEN}{'Total Income':<32} | {format_currency(summary['total_income'])}{RESET}")
    print(f"{RED}{'Total Expenses':<32} | {format_currency(summary['total_expenses'])}{RESET}")
    
    bal = summary['remaining_balance']
    bal_color = GREEN if bal >= 0 else RED
    print(f"{BOLD}{bal_color}{'Remaining Balance':<32} | {format_currency(bal)}{RESET}")
    print(f"{CYAN}{'Savings Rate':<32} | {summary['savings_rate']}%{RESET}")
    print(f"{'Total Transactions':<32} | {summary['total_count']} ({summary['income_count']} Incomes, {summary['expense_count']} Expenses)")
    print("-" * 52)
    
    # Category breakdown
    breakdown = database.get_category_breakdown("expense", start_date=start_date, end_date=end_date)
    if breakdown:
        print(f"\n{BOLD}{YELLOW}Expense Breakdown by Category:{RESET}")
        print(f"{'Category':<18} | {'Total Spent':<12} | {'Share'}")
        print("-" * 48)
        for b in breakdown:
            bar = "█" * int(b['percentage'] / 5)
            print(f"{b['category']:<18} | {format_currency(b['total']):<12} | {b['percentage']:>5.1f}%  {bar}")
        print("-" * 48)
        
    input("\nPress Enter to return to menu...")

def action_budget_manager():
    print_header("Monthly Budget Management & Tracking")
    status = database.get_budget_status()
    
    print(f"Tracking Period: {BOLD}{status['month']}{RESET}")
    print(f"Total Spent This Month: {BOLD}{format_currency(status['total_spent'])}{RESET}\n")
    
    print(f"{'Category':<16} | {'Limit':<12} | {'Spent':<12} | {'Remaining':<12} | {'Usage':<8} | {'Status'}")
    print("-" * 76)
    
    for b in status.get("budgets", []):
        color = GREEN
        tag = "[SAFE]"
        if b["status"] == "exceeded":
            color = RED
            tag = "[OVER!]"
        elif b["status"] == "warning":
            color = YELLOW
            tag = "[WARN]"
            
        pct_str = f"{b['percentage']:.1f}%"
        rem_str = format_currency(b['remaining'])
        if b['remaining'] < 0:
            rem_str = f"-{format_currency(abs(b['remaining']))}"
            
        print(f"{b['category']:<16} | {format_currency(b['monthly_limit']):<12} | {format_currency(b['spent']):<12} | {rem_str:<12} | {pct_str:<8} | {color}{tag}{RESET}")
        
    print("-" * 76)
    print("\nBudget Options:")
    print("  [1] Set / Update a Category Budget Limit")
    print("  [2] Delete a Category Budget")
    print("  [0] Return to Main Menu")
    
    sub_ch = input("\nSelect option (0-2): ").strip()
    if sub_ch == "1":
        cat = input("Enter Category Name (e.g. Food, Transportation, Overall): ").strip()
        if cat:
            limit = prompt_amount(f"Enter Monthly Limit for {cat} (₹): ")
            database.set_budget(cat, limit)
            print(f"{GREEN}[OK] Budget set for '{cat}': {format_currency(limit)}{RESET}")
            input("Press Enter...")
    elif sub_ch == "2":
        cat = input("Enter Category Name to remove budget for: ").strip()
        if cat:
            if database.delete_budget(cat):
                print(f"{GREEN}[OK] Budget removed for '{cat}'.{RESET}")
            else:
                print(f"{RED}Category not found in active budgets.{RESET}")
            input("Press Enter...")

def action_reports_menu():
    while True:
        print_header("Financial Reports Generator")
        print("Select Report Type:")
        print("  [1] Daily Financial Summary (Last 7 Days)")
        print("  [2] Weekly Financial Summary (Last 4 Weeks)")
        print("  [3] Monthly Financial Summary & Savings Trend")
        print("  [4] Custom Date Range Report")
        print("  [0] Return to Main Menu")
        
        ch = input("\nSelect option (0-4): ").strip()
        if ch == "1":
            reports.display_daily_report(days=7)
            input("Press Enter to continue...")
        elif ch == "2":
            reports.display_weekly_report(weeks=4)
            input("Press Enter to continue...")
        elif ch == "3":
            reports.display_monthly_report(months=6)
            input("Press Enter to continue...")
        elif ch == "4":
            s_dt = prompt_date("Enter Start Date (YYYY-MM-DD): ")
            e_dt = prompt_date("Enter End Date (YYYY-MM-DD): ")
            reports.display_custom_period_report(s_dt, e_dt)
            input("Press Enter to continue...")
        elif ch == "0":
            break

def action_visualize_menu():
    while True:
        print_header("Data Visualization & Spending Charts")
        print("Select Visualization Mode:")
        print("  --- Terminal Visualizer (Console Bars) ---")
        print("  [1] Terminal Bar Chart: Expense Distribution by Category")
        print("  [2] Terminal Bar Chart: Monthly Budget vs Actual Spent")
        print("  [3] Terminal Bar Chart: Monthly Income vs Expense Trend")
        print("  --- Graphical Visualizer (Matplotlib Window & Image Export) ---")
        print("  [4] Graphical Donut / Pie Chart: Category Expense Breakdown")
        print("  [5] Graphical Bar Chart: Budget Limit vs Actual Spending")
        print("  [6] Graphical Bar Chart: Monthly Income vs Expense Comparison")
        print("  [7] Graphical 4-in-1 Complete Financial Analytics Dashboard")
        print("  [0] Return to Main Menu")
        
        ch = input("\nSelect option (0-7): ").strip()
        
        breakdown = database.get_category_breakdown("expense")
        budget_status = database.get_budget_status()
        monthly_data = database.get_monthly_summary(months=6)
        summary = database.get_financial_summary()
        
        if ch == "1":
            visualizer.display_ascii_category_chart(breakdown)
            input("Press Enter to continue...")
        elif ch == "2":
            visualizer.display_ascii_budget_chart(budget_status)
            input("Press Enter to continue...")
        elif ch == "3":
            visualizer.display_ascii_monthly_trend(monthly_data)
            input("Press Enter to continue...")
        elif ch == "4":
            visualizer.plot_category_pie_chart(breakdown, save_path="expense_category_chart.png", show=True)
            input("Press Enter to continue...")
        elif ch == "5":
            visualizer.plot_budget_vs_actual(budget_status, save_path="budget_vs_actual.png", show=True)
            input("Press Enter to continue...")
        elif ch == "6":
            visualizer.plot_income_vs_expense(monthly_data, save_path="monthly_trends.png", show=True)
            input("Press Enter to continue...")
        elif ch == "7":
            visualizer.plot_full_dashboard(summary, breakdown, budget_status, monthly_data, save_path="financial_dashboard.png", show=True)
            input("Press Enter to continue...")
        elif ch == "0":
            break

def action_insights():
    summary = database.get_financial_summary()
    breakdown = database.get_category_breakdown("expense")
    budget_status = database.get_budget_status()
    insights.display_insights(summary, breakdown, budget_status)
    input("Press Enter to return to menu...")

def action_export_csv():
    print_header("Export Transactions to CSV")
    filename = input("Enter export filename [default: transactions_report.csv]: ").strip()
    if not filename:
        filename = "transactions_report.csv"
    if not filename.endswith(".csv"):
        filename += ".csv"
        
    txs = database.get_transactions(sort_by="date", order="DESC")
    if not txs:
        print(f"{YELLOW}No transactions to export.{RESET}")
        input("Press Enter...")
        return
        
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Date", "Type", "Category", "Amount (INR)", "Description", "Created At"])
        for t in txs:
            writer.writerow([t["id"], t["date"], t["type"].upper(), t["category"], t["amount"], t["description"], t["created_at"]])
            
    print(f"\n{GREEN}[OK] Successfully exported {len(txs)} transactions to:{RESET}")
    print(f"     {filepath}")
    input("\nPress Enter to return to menu...")

def action_reset_sample():
    print_header("Load Problem Statement Example Data")
    print("This will populate the database with the exact problem statement sample:")
    print("  - Monthly Income: ₹40,000")
    print("  - Food: ₹6,000")
    print("  - Transportation: ₹3,000")
    print("  - Shopping: ₹5,000")
    print("  - Bills: ₹7,000")
    print("  - Entertainment: ₹2,000")
    print("  Total Expenses = ₹23,000 | Balance = ₹17,000\n")
    
    confirm = input(f"{YELLOW}Reset and load problem statement sample? (y/N): {RESET}").strip().lower()
    if confirm == "y":
        database.reset_database()
        print(f"\n{GREEN}[OK] Database loaded with problem statement example!{RESET}")
    else:
        print("\nAction cancelled.")
    input("\nPress Enter to return to menu...")

# --- Main CLI Loop ---

def main_cli():
    """Main interactive terminal loop for Expense Tracker."""
    database.init_db()
    
    while True:
        clear_screen()
        summary = database.get_financial_summary()
        bal = summary['remaining_balance']
        bal_color = GREEN if bal >= 0 else RED
        
        print(f"{BOLD}{CYAN}+--------------------------------------------------------------+{RESET}")
        print(f"{BOLD}{CYAN}|             EXPENSE TRACKER & FINANCIAL ANALYTICS            |{RESET}")
        print(f"{BOLD}{CYAN}+--------------------------------------------------------------+{RESET}")
        print(f" {GREEN}Income: {format_currency(summary['total_income'])}{RESET}  |  {RED}Expenses: {format_currency(summary['total_expenses'])}{RESET}  |  {bal_color}Balance: {format_currency(bal)}{RESET} ({summary['savings_rate']}%)")
        print("-" * 64)
        print("  [1]  Add Income (Record Salary, Freelance, etc.)")
        print("  [2]  Add Expense (Food, Bills, Shopping, Travel, etc.)")
        print("  [3]  View All Transactions (Full History)")
        print("  [4]  Search & Filter Transactions (Date, Category, Amount)")
        print("  [5]  Financial Balance & Category Breakdown")
        print("  [6]  Monthly Budget Tracker & Spending Alerts")
        print("  [7]  Edit a Transaction")
        print("  [8]  Delete a Transaction")
        print("  [9]  Generate Financial Reports (Daily, Weekly, Monthly)")
        print("  [10] Visualize Data (Terminal Bars & Matplotlib Charts)")
        print("  [11] Financial Awareness & Smart Budgeting Insights")
        print("  [12] Export Transactions to CSV")
        print("  [13] Load Problem Statement Example (₹40,000 Income / ₹23,000 Expenses)")
        print("  [0]  Exit Application")
        print("-" * 64)
        
        choice = input(f"{BOLD}Select an option (0-13): {RESET}").strip()
        
        if choice == "1":
            action_add_transaction("income")
        elif choice == "2":
            action_add_transaction("expense")
        elif choice == "3":
            action_view_transactions()
        elif choice == "4":
            action_search_filter()
        elif choice == "5":
            action_financial_summary()
        elif choice == "6":
            action_budget_manager()
        elif choice == "7":
            action_edit_transaction()
        elif choice == "8":
            action_delete_transaction()
        elif choice == "9":
            action_reports_menu()
        elif choice == "10":
            action_visualize_menu()
        elif choice == "11":
            action_insights()
        elif choice == "12":
            action_export_csv()
        elif choice == "13":
            action_reset_sample()
        elif choice == "0":
            print(f"\n{CYAN}Thank you for using Expense Tracker! Have a great day.{RESET}\n")
            sys.exit(0)
        else:
            print(f"{RED}Invalid option! Please enter a number between 0 and 13.{RESET}")
            input("Press Enter...")

if __name__ == "__main__":
    main_cli()
