"""
Financial Awareness and Smart Budgeting Insights Engine.
Satisfies Objective 10: "Improve financial awareness — Help users identify unnecessary expenses and make better budgeting decisions."
"""

import sys
from datetime import datetime

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

# Categorization mapping for Needs vs Wants
NEEDS_CATEGORIES = {
    "food", "groceries", "bills", "utilities", "transportation", 
    "healthcare", "medical", "education", "rent", "housing"
}
WANTS_CATEGORIES = {
    "shopping", "entertainment", "dining out", "movies", "travel",
    "electronics", "subscriptions", "personal care", "hobbies", "gifts"
}

def analyze_financial_health(summary, breakdown, budget_status):
    """
    Evaluates spending patterns, categorizes into 50/30/20 rule,
    identifies non-essential spending, and produces actionable tips.
    """
    income = summary.get("total_income", 0.0)
    expenses = summary.get("total_expenses", 0.0)
    balance = summary.get("remaining_balance", 0.0)
    savings_rate = summary.get("savings_rate", 0.0)

    # Classify expenses into Needs vs Wants
    needs_total = 0.0
    wants_total = 0.0

    needs_items = []
    wants_items = []

    for b in breakdown:
        cat_lower = b["category"].lower().strip()
        amt = b["total"]
        if any(need in cat_lower for need in NEEDS_CATEGORIES):
            needs_total += amt
            needs_items.append(b)
        elif any(want in cat_lower for want in WANTS_CATEGORIES):
            wants_total += amt
            wants_items.append(b)
        else:
            wants_total += amt
            wants_items.append(b)

    # Calculate actual percentages relative to income
    if income > 0:
        needs_pct = (needs_total / income) * 100
        wants_pct = (wants_total / income) * 100
        savings_pct = (balance / income) * 100
    else:
        needs_pct = 0.0
        wants_pct = 0.0
        savings_pct = 0.0

    # Generate insights and recommendations
    recommendations = []
    warnings = []

    # Savings rate evaluation
    if savings_rate >= 30:
        score = "EXCELLENT"
        score_color = GREEN
        recommendations.append("Outstanding savings discipline! You are saving >30% of your income. Consider investing your surplus into emergency funds, mutual funds, or high-yield savings.")
    elif savings_rate >= 20:
        score = "GOOD"
        score_color = GREEN
        recommendations.append("Healthy financial footing! You meet the benchmark 20% savings rule. Keep monitoring recurring bills to maintain this cushion.")
    elif savings_rate >= 10:
        score = "FAIR"
        score_color = YELLOW
        recommendations.append("Moderate savings rate (10%-20%). Try reducing non-essential wants (such as shopping or entertainment) to push your savings above 20%.")
    elif savings_rate > 0:
        score = "NEEDS ATTENTION"
        score_color = RED
        warnings.append(f"Low savings buffer ({savings_rate:.1f}%). A single unplanned emergency could put you in a deficit.")
        recommendations.append("Audit monthly subscriptions, eating out, and leisure purchases immediately.")
    else:
        score = "CRITICAL DEFICIT"
        score_color = RED
        warnings.append("You are currently spending more than your income! Immediate budget reductions are required.")
        recommendations.append("Freeze all non-essential shopping and entertainment expenses until your balance turns positive.")

    # High discretionary / wants detection
    if wants_total > 0:
        top_wants = sorted(wants_items, key=lambda x: x["total"], reverse=True)
        top_want_names = [f"{w['category']} (₹{w['total']:,.0f})" for w in top_wants[:3]]
        recommendations.append(f"Discretionary spending ('Wants') totals ₹{wants_total:,.0f} ({wants_pct:.1f}% of income). Top discretionary expenses: {', '.join(top_want_names)}.")

    # Budget overruns
    exceeded_budgets = [b for b in budget_status.get("budgets", []) if b["status"] == "exceeded"]
    if exceeded_budgets:
        for eb in exceeded_budgets:
            warnings.append(f"Budget for '{eb['category']}' has been EXCEEDED by ₹{abs(eb['remaining']):,.0f}!")

    # 50/30/20 Rule compliance
    rule_insights = {
        "needs_actual": round(needs_pct, 1),
        "needs_ideal": 50.0,
        "needs_amount": needs_total,
        "wants_actual": round(wants_pct, 1),
        "wants_ideal": 30.0,
        "wants_amount": wants_total,
        "savings_actual": round(savings_pct, 1),
        "savings_ideal": 20.0,
        "savings_amount": balance,
    }

    return {
        "score": score,
        "score_color": score_color,
        "rule_insights": rule_insights,
        "warnings": warnings,
        "recommendations": recommendations,
        "needs_total": needs_total,
        "wants_total": wants_total
    }


def display_insights(summary, breakdown, budget_status):
    """
    Renders the Financial Awareness and Smart Budgeting report in the terminal.
    """
    res = analyze_financial_health(summary, breakdown, budget_status)

    print(f"\n{BOLD}{CYAN}{'='*68}{RESET}")
    print(f"{BOLD}{CYAN}  {'FINANCIAL AWARENESS & SMART BUDGETING INSIGHTS'.center(64)}  {RESET}")
    print(f"{BOLD}{CYAN}{'='*68}{RESET}\n")

    print(f" Financial Health Rating: {res['score_color']}{BOLD}{res['score']}{RESET}")
    print(f" Total Monthly Income:    {GREEN}₹{summary['total_income']:,.2f}{RESET}")
    print(f" Total Monthly Expenses:  {RED}₹{summary['total_expenses']:,.2f}{RESET}")
    print(f" Remaining Savings:       {BOLD}₹{summary['remaining_balance']:,.2f}{RESET} ({summary['savings_rate']}% of income)\n")

    # 50/30/20 Rule Breakdown
    rule = res["rule_insights"]
    print(f"{BOLD}{YELLOW}The 50 / 30 / 20 Budget Rule Benchmark:{RESET}")
    print(f"{'Category':<22} | {'Ideal':<8} | {'Your Spending':<15} | {'Amount Spent':<14} | {'Status'}")
    print("-" * 68)

    # Needs
    n_status = f"{GREEN}[OK]{RESET}" if rule['needs_actual'] <= 55 else f"{YELLOW}[HIGH]{RESET}"
    print(f" {'Needs (Essentials)':<21} | 50.0%    | {rule['needs_actual']:>5.1f}%          | ₹{rule['needs_amount']:>10,.2f}  | {n_status}")

    # Wants
    w_status = f"{GREEN}[OK]{RESET}" if rule['wants_actual'] <= 30 else f"{RED}[HIGH]{RESET}"
    print(f" {'Wants (Discretionary)':<21} | 30.0%    | {rule['wants_actual']:>5.1f}%          | ₹{rule['wants_amount']:>10,.2f}  | {w_status}")

    # Savings
    s_status = f"{GREEN}[STRONG]{RESET}" if rule['savings_actual'] >= 20 else f"{RED}[LOW]{RESET}"
    print(f" {'Savings / Investment':<21} | 20.0%    | {rule['savings_actual']:>5.1f}%          | ₹{rule['savings_amount']:>10,.2f}  | {s_status}")
    print("-" * 68)

    # Warnings section if any
    if res["warnings"]:
        print(f"\n{BOLD}{RED}[!] Active Budget & Spending Alerts:{RESET}")
        for w in res["warnings"]:
            print(f"  * {RED}{w}{RESET}")

    # Actionable Tips & Recommendations
    print(f"\n{BOLD}{CYAN}[*] Actionable Recommendations to Optimize Spending:{RESET}")
    for idx, tip in enumerate(res["recommendations"], 1):
        print(f"  {idx}. {tip}")

    print("\n" + "-" * 68)
