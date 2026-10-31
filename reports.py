"""
Reports module for Expense Tracker.
Provides daily, weekly, monthly, and custom financial summary reports.
Satisfies Objective 7: "Generate reports — Provide daily, weekly, and monthly summaries."
"""

import sys
from datetime import datetime
import database

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
BOLD = "\033[1m"
RESET = "\033[0m"

def print_report_header(title):
    print(f"\n{BOLD}{CYAN}{'='*68}{RESET}")
    print(f"{BOLD}{CYAN}  {title.center(64)}  {RESET}")
    print(f"{BOLD}{CYAN}{'='*68}{RESET}\n")

def display_daily_report(days=7):
    """Generates and prints a daily summary report for the last N days."""
    daily_data = database.get_daily_summary(days=days)
    print_report_header(f"DAILY FINANCIAL SUMMARY (LAST {days} DAYS)")

    if not daily_data:
        print(f"{YELLOW}No transaction records found for the past {days} days.{RESET}\n")
        return

    print(f" {'Date':<12} | {'Income':<14} | {'Expense':<14} | {'Net Balance':<14} | {'Count'}")
    print("-" * 68)

    total_inc = 0.0
    total_exp = 0.0

    for d in daily_data:
        inc = d["income"]
        exp = d["expense"]
        net = d["net"]
        total_inc += inc
        total_exp += exp

        inc_str = f"{GREEN}₹{inc:>11,.2f}{RESET}" if inc > 0 else f"₹{inc:>11,.2f}"
        exp_str = f"{RED}₹{exp:>11,.2f}{RESET}" if exp > 0 else f"₹{exp:>11,.2f}"
        net_col = GREEN if net >= 0 else RED
        net_str = f"{net_col}₹{net:>11,.2f}{RESET}"

        print(f" {d['date']:<12} | {inc_str} | {exp_str} | {net_str} | {d['count']:>4}")

    print("-" * 68)
    net_tot = total_inc - total_exp
    net_tot_col = GREEN if net_tot >= 0 else RED
    print(f" {BOLD}{'TOTALS':<12} | {GREEN}₹{total_inc:>11,.2f}{RESET} | {RED}₹{total_exp:>11,.2f}{RESET} | {net_tot_col}₹{net_tot:>11,.2f}{RESET} | {sum(d['count'] for d in daily_data):>4}")
    
    avg_exp = total_exp / len(daily_data) if daily_data else 0.0
    print(f"\n * Average Daily Spending: {BOLD}{RED}₹{avg_exp:,.2f}/day{RESET}\n")

def display_weekly_report(weeks=4):
    """Generates and prints a weekly summary report."""
    weekly_data = database.get_weekly_summary(weeks=weeks)
    print_report_header(f"WEEKLY FINANCIAL SUMMARY (LAST {weeks} WEEKS)")

    if not weekly_data:
        print(f"{YELLOW}No weekly records found for this period.{RESET}\n")
        return

    print(f" {'Week / Period':<26} | {'Income':<13} | {'Expense':<13} | {'Net Balance':<13} | {'Tx'}")
    print("-" * 75)

    tot_inc = 0.0
    tot_exp = 0.0

    for w in weekly_data:
        inc = w["income"]
        exp = w["expense"]
        net = w["net"]
        tot_inc += inc
        tot_exp += exp

        label = f"{w['week']} ({w['period'][:10]})"
        inc_str = f"{GREEN}₹{inc:>10,.2f}{RESET}"
        exp_str = f"{RED}₹{exp:>10,.2f}{RESET}"
        net_col = GREEN if net >= 0 else RED
        net_str = f"{net_col}₹{net:>10,.2f}{RESET}"

        print(f" {label:<26} | {inc_str} | {exp_str} | {net_str} | {w['count']:>3}")

    print("-" * 75)
    tot_net = tot_inc - tot_exp
    tot_net_col = GREEN if tot_net >= 0 else RED
    print(f" {BOLD}{'TOTAL':<26} | {GREEN}₹{tot_inc:>10,.2f}{RESET} | {RED}₹{tot_exp:>10,.2f}{RESET} | {tot_net_col}₹{tot_net:>10,.2f}{RESET} | {sum(w['count'] for w in weekly_data):>3}")
    print()

def display_monthly_report(months=6):
    """Generates and prints monthly trends and comparative performance."""
    monthly_data = database.get_monthly_summary(months=months)
    print_report_header(f"MONTHLY FINANCIAL SUMMARY & SAVINGS TREND")

    if not monthly_data:
        print(f"{YELLOW}No monthly data available.{RESET}\n")
        return

    print(f" {'Month':<10} | {'Income':<14} | {'Expense':<14} | {'Balance':<14} | {'Savings %':<10} | {'Tx'}")
    print("-" * 75)

    for m in monthly_data:
        inc = m["income"]
        exp = m["expense"]
        bal = m["balance"]
        bal_col = GREEN if bal >= 0 else RED
        rate_str = f"{m['savings_rate']:>5.1f}%"

        print(f" {m['month']:<10} | {GREEN}₹{inc:>12,.2f}{RESET} | {RED}₹{exp:>12,.2f}{RESET} | {bal_col}₹{bal:>12,.2f}{RESET} | {rate_str:<10} | {m['tx_count']:>3}")

    print("-" * 75)

    # Current month's detailed category breakdown
    now_month = datetime.now().strftime("%Y-%m")
    cat_breakdown = database.get_category_breakdown("expense", start_date=f"{now_month}-01")
    if cat_breakdown:
        print(f"\n{BOLD}{YELLOW}Current Month ({now_month}) Expense Breakdown by Category:{RESET}")
        print(f" {'Category':<18} | {'Spent':<12} | {'Share %':<8} | {'Transactions'}")
        print("-" * 52)
        for c in cat_breakdown:
            print(f" {c['category']:<18} | ₹{c['total']:>10,.2f} | {c['percentage']:>6.1f}% | {c['count']:>4}")
        print("-" * 52)
    print()

def display_custom_period_report(start_date, end_date):
    """Generates summary for a user-specified custom date range."""
    print_report_header(f"FINANCIAL REPORT ({start_date} to {end_date})")
    
    summary = database.get_financial_summary(start_date=start_date, end_date=end_date)
    breakdown = database.get_category_breakdown("expense", start_date=start_date, end_date=end_date)

    bal = summary['remaining_balance']
    bal_col = GREEN if bal >= 0 else RED

    print(f" Total Income:      {GREEN}₹{summary['total_income']:,.2f}{RESET}")
    print(f" Total Expenses:    {RED}₹{summary['total_expenses']:,.2f}{RESET}")
    print(f" Net Balance:       {bal_col}₹{bal:,.2f}{RESET} (Savings Rate: {summary['savings_rate']}%)")
    print(f" Total Activity:    {summary['total_count']} transactions ({summary['income_count']} Incomes, {summary['expense_count']} Expenses)\n")

    if breakdown:
        print(f"{BOLD}Top Spending Categories for this period:{RESET}")
        for b in breakdown:
            bar = "█" * int(b['percentage'] / 5)
            print(f"  * {b['category']:<15} ₹{b['total']:>10,.2f} ({b['percentage']:>5.1f}%) {bar}")
    print()
