"""
Main Entry Point for the Expense Tracker Python Program.
Pure Python Application - No Web Server, No Browser required.

Usage:
    python main.py             # Launches interactive terminal menu
    python main.py --summary   # Quick financial balance & summary
    python main.py --report    # Shows monthly report
    python main.py --chart     # Generates terminal charts & dashboard
    python main.py --export    # Exports transactions to CSV
"""

import sys
import argparse

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import database
import cli
import reports
import visualizer
import insights

def quick_summary():
    """Print quick financial summary directly to stdout."""
    database.init_db()
    s = database.get_financial_summary()
    b = database.get_category_breakdown("expense")
    print("\n" + "=" * 55)
    print("      EXPENSE TRACKER - QUICK FINANCIAL OVERVIEW")
    print("=" * 55)
    print(f" Total Income:      ₹{s['total_income']:,.2f}")
    print(f" Total Expenses:    ₹{s['total_expenses']:,.2f}")
    print(f" Remaining Balance: ₹{s['remaining_balance']:,.2f}")
    print(f" Savings Rate:      {s['savings_rate']}%")
    print(f" Total Records:     {s['total_count']} ({s['income_count']} Incomes, {s['expense_count']} Expenses)")
    print("-" * 55)
    if b:
        print(" Top Spending Categories:")
        for item in b[:4]:
            print(f"   • {item['category']:<15} ₹{item['total']:>10,.2f} ({item['percentage']:>5.1f}%)")
    print("=" * 55 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description="Expense Tracker — Pure Python Personal Finance & Analytics Program"
    )
    parser.add_argument("--summary", action="store_true", help="Print a quick balance & summary to terminal")
    parser.add_argument("--report", choices=["daily", "weekly", "monthly"], help="Generate specified financial report")
    parser.add_argument("--chart", action="store_true", help="Render ASCII spending charts to terminal")
    parser.add_argument("--insights", action="store_true", help="Show 50/30/20 financial awareness & budgeting insights")
    parser.add_argument("--export", help="Export all transactions to specified CSV filename (e.g. report.csv)")
    parser.add_argument("--reset-example", action="store_true", help="Load problem statement sample data")

    args = parser.parse_args()

    database.init_db()

    # If any specific non-interactive flag was provided, execute it
    if args.summary:
        quick_summary()
        return

    if args.report == "daily":
        reports.display_daily_report(7)
        return
    elif args.report == "weekly":
        reports.display_weekly_report(4)
        return
    elif args.report == "monthly":
        reports.display_monthly_report(6)
        return

    if args.chart:
        b = database.get_category_breakdown("expense")
        bs = database.get_budget_status()
        visualizer.display_ascii_category_chart(b)
        visualizer.display_ascii_budget_chart(bs)
        return

    if args.insights:
        s = database.get_financial_summary()
        b = database.get_category_breakdown("expense")
        bs = database.get_budget_status()
        insights.display_insights(s, b, bs)
        return

    if args.export:
        cli.action_export_csv()
        return

    if args.reset_example:
        database.reset_database()
        print("\n[OK] Database initialized with problem statement example data (₹40,000 Income / ₹23,000 Expenses / ₹17,000 Balance).\n")
        return

    # Default action: launch the full interactive CLI
    cli.main_cli()

if __name__ == "__main__":
    main()
