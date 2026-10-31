"""
Visualizer module for Expense Tracker.
Provides both rich Terminal ASCII/Unicode bar charts and Python Matplotlib graphical charts.
Satisfies Objective 8: "Visualize data — Use charts/graphs to make spending patterns easier to understand."
"""

import os
import sys

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ANSI Color codes for clean terminal output
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

# -------------------------------------------------------------
# 1. TERMINAL ASCII / UNICODE CHARTS (Zero External Dependency)
# -------------------------------------------------------------

def display_ascii_category_chart(breakdown, title="Expense Distribution by Category"):
    """
    Renders a clean terminal horizontal bar chart representing category spending.
    """
    if not breakdown:
        print(f"\n{YELLOW}No expense data available to visualize.{RESET}")
        return

    print(f"\n{BOLD}{CYAN}{'='*65}{RESET}")
    print(f"{BOLD}{CYAN}  {title.center(61)}  {RESET}")
    print(f"{BOLD}{CYAN}{'='*65}{RESET}\n")

    max_len = max(len(b["category"]) for b in breakdown) if breakdown else 10
    max_amount = max(b["total"] for b in breakdown) if breakdown else 1.0

    colors = [CYAN, YELLOW, GREEN, MAGENTA, BLUE, RED]

    for idx, b in enumerate(breakdown):
        color = colors[idx % len(colors)]
        cat_name = b["category"].ljust(max_len)
        pct = b["percentage"]
        amount_str = f"₹{b['total']:,.2f}".rjust(12)
        
        # 30-column max width bar
        bar_len = int((b["total"] / max_amount) * 30) if max_amount > 0 else 0
        bar = "█" * max(bar_len, 1) if b["total"] > 0 else " "

        print(f" {BOLD}{cat_name}{RESET} | {color}{bar:<30}{RESET} | {pct:>5.1f}% | {amount_str}")

    print(f"{'-'*65}")
    grand_total = sum(b["total"] for b in breakdown)
    print(f" {BOLD}Total Tracked Expenses:{RESET} {BOLD}{RED}₹{grand_total:,.2f}{RESET}\n")


def display_ascii_budget_chart(budget_status):
    """
    Renders terminal comparison bars showing spent vs budget limit for each category.
    """
    budgets = budget_status.get("budgets", [])
    if not budgets:
        print(f"\n{YELLOW}No budgets configured yet.{RESET}")
        return

    print(f"\n{BOLD}{CYAN}{'='*72}{RESET}")
    print(f"{BOLD}{CYAN}  {'Monthly Budget vs Actual Spending Comparison'.center(68)}  {RESET}")
    print(f"{BOLD}{CYAN}{'='*72}{RESET}\n")

    print(f" {'Category':<15} | {'Usage Bar (Spent / Limit)':<28} | {'Spent / Limit':<22}")
    print("-" * 72)

    for b in budgets:
        pct = b["percentage"]
        limit = b["monthly_limit"]
        spent = b["spent"]

        # Determine color
        if b["status"] == "exceeded":
            bar_color = RED
            status_tag = f"{RED}[OVER]{RESET}"
        elif b["status"] == "warning":
            bar_color = YELLOW
            status_tag = f"{YELLOW}[80%+]{RESET}"
        else:
            bar_color = GREEN
            status_tag = f"{GREEN}[SAFE]{RESET}"

        # Bar representation (20 units max)
        fill_units = min(int((spent / limit) * 20), 20) if limit > 0 else 0
        bar = "█" * fill_units
        empty = "░" * (20 - fill_units)

        ratio_str = f"₹{spent:,.0f} / ₹{limit:,.0f}"

        print(f" {b['category']:<15} | {bar_color}{bar}{RESET}{empty} {pct:>5.1f}% | {ratio_str:<18} {status_tag}")

    print("-" * 72 + "\n")


def display_ascii_monthly_trend(trends):
    """
    Renders monthly income vs expense comparison bars.
    """
    if not trends:
        print(f"\n{YELLOW}No monthly data available.{RESET}")
        return

    print(f"\n{BOLD}{CYAN}{'='*70}{RESET}")
    print(f"{BOLD}{CYAN}  {'Monthly Income vs Expense Trend'.center(66)}  {RESET}")
    print(f"{BOLD}{CYAN}{'='*70}{RESET}\n")

    all_vals = [t["income"] for t in trends] + [t["expense"] for t in trends]
    max_val = max(all_vals) if all_vals and max(all_vals) > 0 else 1.0

    for t in trends:
        m = t["month"]
        inc_bar_len = int((t["income"] / max_val) * 25)
        exp_bar_len = int((t["expense"] / max_val) * 25)

        inc_bar = "█" * inc_bar_len
        exp_bar = "█" * exp_bar_len

        print(f"{BOLD}Month: {m}{RESET}")
        print(f"  Income   | {GREEN}{inc_bar:<25}{RESET} | ₹{t['income']:,.2f}")
        print(f"  Expense  | {RED}{exp_bar:<25}{RESET} | ₹{t['expense']:,.2f}")
        bal_color = GREEN if t["balance"] >= 0 else RED
        print(f"  Net      | {bal_color}₹{t['balance']:,.2f}{RESET} (Savings: {t.get('savings_rate', 0)}%)")
        print("-" * 60)
    print()


# -------------------------------------------------------------
# 2. PYTHON GRAPHICAL CHARTS WITH MATPLOTLIB (Interactive / PNG)
# -------------------------------------------------------------

def try_import_matplotlib():
    """Attempt to import matplotlib and return pyplot module or None."""
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        # Clean styling
        plt.style.use('fast')
        return plt
    except ImportError:
        return None


def plot_category_pie_chart(breakdown, save_path="expense_category_chart.png", show=True):
    """
    Generates a high-quality Category Expense Pie/Donut Chart.
    """
    plt = try_import_matplotlib()
    if not plt:
        print(f"{RED}Matplotlib is not installed. Using terminal ASCII chart instead.{RESET}")
        display_ascii_category_chart(breakdown)
        return False

    if not breakdown:
        print(f"{YELLOW}No expense data available for graphical chart.{RESET}")
        return False

    labels = [b["category"] for b in breakdown]
    amounts = [b["total"] for b in breakdown]
    total_spent = sum(amounts)

    fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(aspect="equal"))
    
    # Custom vibrant palette
    colors = plt.cm.tab10.colors[:len(labels)]

    def autopct_format(pct):
        val = (pct / 100) * total_spent
        return f"{pct:.1f}%\n(₹{val:,.0f})"

    wedges, texts, autotexts = ax.pie(
        amounts,
        labels=labels,
        autopct=autopct_format,
        startangle=140,
        colors=colors,
        pctdistance=0.75,
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2)  # Donut style
    )

    for autotext in autotexts:
        autotext.set_fontsize(8)
        autotext.set_weight("bold")
    for text in texts:
        text.set_fontsize(9)

    ax.set_title(f"Expense Breakdown by Category\nTotal Spent: ₹{total_spent:,.2f}", fontsize=13, weight="bold", pad=20)
    plt.tight_layout()

    # Save to disk
    full_path = os.path.abspath(save_path)
    plt.savefig(full_path, dpi=150)
    print(f"\n{GREEN}✓ Chart saved to: {full_path}{RESET}")

    if show:
        print(f"{CYAN}Displaying chart window... (Close the chart window to return to terminal){RESET}")
        try:
            plt.show()
        except Exception:
            pass
    plt.close()
    return True


def plot_budget_vs_actual(budget_status, save_path="budget_vs_actual.png", show=True):
    """
    Generates a grouped horizontal bar chart comparing Budget Limit vs Actual Spending.
    """
    plt = try_import_matplotlib()
    if not plt:
        print(f"{RED}Matplotlib is not installed. Using terminal ASCII chart instead.{RESET}")
        display_ascii_budget_chart(budget_status)
        return False

    budgets = budget_status.get("budgets", [])
    if not budgets:
        print(f"{YELLOW}No budgets configured to plot.{RESET}")
        return False

    categories = [b["category"] for b in budgets]
    limits = [b["monthly_limit"] for b in budgets]
    spent = [b["spent"] for b in budgets]

    import numpy as np
    y = np.arange(len(categories))
    height = 0.35

    fig, ax = plt.subplots(figsize=(9, 6))

    rects1 = ax.barh(y - height/2, limits, height, label='Budget Limit', color='#4A90E2')
    
    # Color actual spent bars based on threshold
    spent_colors = []
    for b in budgets:
        if b["status"] == "exceeded":
            spent_colors.append('#E74C3C') # Red
        elif b["status"] == "warning":
            spent_colors.append('#F39C12') # Yellow
        else:
            spent_colors.append('#2ECC71') # Green

    rects2 = ax.barh(y + height/2, spent, height, label='Actual Spent', color=spent_colors)

    ax.set_xlabel('Amount in ₹ (INR)', fontsize=11, weight='bold')
    ax.set_title(f"Budget Limit vs Actual Spending ({budget_status.get('month', 'Current Month')})", fontsize=13, weight='bold', pad=15)
    ax.set_yticks(y)
    ax.set_yticklabels(categories, fontsize=10)
    ax.legend(loc='lower right')
    ax.grid(axis='x', linestyle='--', alpha=0.5)

    plt.tight_layout()
    full_path = os.path.abspath(save_path)
    plt.savefig(full_path, dpi=150)
    print(f"\n{GREEN}✓ Budget chart saved to: {full_path}{RESET}")

    if show:
        print(f"{CYAN}Displaying budget chart window... (Close chart window to continue){RESET}")
        try:
            plt.show()
        except Exception:
            pass
    plt.close()
    return True


def plot_income_vs_expense(monthly_data, save_path="monthly_trends.png", show=True):
    """
    Generates a grouped vertical bar chart comparing Monthly Income and Expenses.
    """
    plt = try_import_matplotlib()
    if not plt:
        print(f"{RED}Matplotlib is not installed. Using terminal ASCII trend instead.{RESET}")
        display_ascii_monthly_trend(monthly_data)
        return False

    if not monthly_data:
        print(f"{YELLOW}No monthly data available to plot.{RESET}")
        return False

    months = [m["month"] for m in monthly_data]
    incomes = [m["income"] for m in monthly_data]
    expenses = [m["expense"] for m in monthly_data]

    import numpy as np
    x = np.arange(len(months))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 5.5))

    ax.bar(x - width/2, incomes, width, label='Income', color='#2ECC71')
    ax.bar(x + width/2, expenses, width, label='Expenses', color='#E74C3C')

    ax.set_ylabel('Amount in ₹ (INR)', fontsize=11, weight='bold')
    ax.set_title('Monthly Income vs Expenses Trend', fontsize=13, weight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(months, fontsize=10)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    full_path = os.path.abspath(save_path)
    plt.savefig(full_path, dpi=150)
    print(f"\n{GREEN}✓ Trend chart saved to: {full_path}{RESET}")

    if show:
        print(f"{CYAN}Displaying trend chart window... (Close chart window to continue){RESET}")
        try:
            plt.show()
        except Exception:
            pass
    plt.close()
    return True


def plot_full_dashboard(summary, breakdown, budget_status, monthly_data, save_path="financial_dashboard.png", show=True):
    """
    Generates a comprehensive 4-in-1 Financial Analytics Dashboard figure.
    Panel 1: Category Breakdown Donut Chart
    Panel 2: Overall Income vs Expense & Balance
    Panel 3: Budget vs Actual Comparison
    Panel 4: Monthly Trend Comparison
    """
    plt = try_import_matplotlib()
    if not plt:
        print(f"{RED}Matplotlib is not installed. Showing ASCII charts in terminal.{RESET}")
        display_ascii_category_chart(breakdown)
        display_ascii_budget_chart(budget_status)
        return False

    import numpy as np
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Expense Tracker — Financial Overview & Analytics Dashboard", fontsize=16, weight="bold", y=0.98)

    # Panel 1: Donut Chart
    ax1 = axes[0, 0]
    if breakdown:
        labels = [b["category"] for b in breakdown]
        amounts = [b["total"] for b in breakdown]
        ax1.pie(amounts, labels=labels, autopct='%1.1f%%', startangle=140,
                wedgeprops=dict(width=0.45, edgecolor='white'))
        ax1.set_title(f"Expense by Category (Total: ₹{sum(amounts):,.0f})", fontsize=11, weight="bold")
    else:
        ax1.text(0.5, 0.5, "No Expense Data", ha="center", va="center")
        ax1.set_title("Expense by Category", fontsize=11, weight="bold")

    # Panel 2: Summary Bar Chart
    ax2 = axes[0, 1]
    metrics = ['Income', 'Expenses', 'Balance']
    vals = [summary['total_income'], summary['total_expenses'], max(0, summary['remaining_balance'])]
    bar_cols = ['#2ECC71', '#E74C3C', '#3498DB']
    bars = ax2.bar(metrics, vals, color=bar_cols, width=0.5)
    ax2.set_title(f"Total Overview (Savings Rate: {summary['savings_rate']}%)", fontsize=11, weight="bold")
    ax2.set_ylabel("Amount in ₹")
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    for b in bars:
        ax2.annotate(f"₹{b.get_height():,.0f}",
                     xy=(b.get_x() + b.get_width() / 2, b.get_height()),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=9, weight='bold')

    # Panel 3: Budget vs Actual
    ax3 = axes[1, 0]
    budgets = budget_status.get("budgets", [])
    if budgets:
        cats = [b["category"] for b in budgets]
        b_limits = [b["monthly_limit"] for b in budgets]
        b_spent = [b["spent"] for b in budgets]
        y_pos = np.arange(len(cats))
        h = 0.35
        ax3.barh(y_pos - h/2, b_limits, h, label='Budget Limit', color='#4A90E2')
        cols = ['#E74C3C' if b['status'] == 'exceeded' else ('#F39C12' if b['status'] == 'warning' else '#2ECC71') for b in budgets]
        ax3.barh(y_pos + h/2, b_spent, h, label='Spent', color=cols)
        ax3.set_yticks(y_pos)
        ax3.set_yticklabels(cats, fontsize=8)
        ax3.set_title("Budget vs Actual Spending", fontsize=11, weight="bold")
        ax3.legend(loc="lower right", fontsize=8)
        ax3.grid(axis='x', linestyle='--', alpha=0.5)
    else:
        ax3.text(0.5, 0.5, "No Budgets Configured", ha="center", va="center")
        ax3.set_title("Budget vs Actual Spending", fontsize=11, weight="bold")

    # Panel 4: Monthly Trend
    ax4 = axes[1, 1]
    if monthly_data:
        m_labels = [m["month"] for m in monthly_data]
        m_inc = [m["income"] for m in monthly_data]
        m_exp = [m["expense"] for m in monthly_data]
        x_pos = np.arange(len(m_labels))
        w = 0.35
        ax4.bar(x_pos - w/2, m_inc, w, label='Income', color='#2ECC71')
        ax4.bar(x_pos + w/2, m_exp, w, label='Expense', color='#E74C3C')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(m_labels, fontsize=8)
        ax4.set_title("Monthly Income vs Expense Trend", fontsize=11, weight="bold")
        ax4.legend(loc="upper right", fontsize=8)
        ax4.grid(axis='y', linestyle='--', alpha=0.5)
    else:
        ax4.text(0.5, 0.5, "No Trend Data", ha="center", va="center")
        ax4.set_title("Monthly Trends", fontsize=11, weight="bold")

    plt.tight_layout()
    full_path = os.path.abspath(save_path)
    plt.savefig(full_path, dpi=150)
    print(f"\n{GREEN}✓ Full Financial Analytics Dashboard saved to: {full_path}{RESET}")

    if show:
        print(f"{CYAN}Displaying dashboard window... (Close the dashboard window to return){RESET}")
        try:
            plt.show()
        except Exception:
            pass
    plt.close()
    return True
