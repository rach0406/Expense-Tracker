import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def make_category_pie(expenses: list) -> go.Figure:
    """
    Donut chart — spending share by category.
    """
    if not expenses:
        return _empty_chart("No expenses yet to show.")

    df = pd.DataFrame(expenses)
    df_grouped = df.groupby("category")["amount"].sum().reset_index()

    fig = px.pie(
        df_grouped,
        names="category",
        values="amount",
        hole=0.45,  # makes it a donut
        color_discrete_sequence=px.colors.qualitative.Pastel,
        title="💰 Spending by Category"
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(showlegend=True, height=400)
    return fig


def make_monthly_bar(expenses: list) -> go.Figure:
    """
    Bar chart — total spending per month.
    """
    if not expenses:
        return _empty_chart("No expenses yet to show.")

    df = pd.DataFrame(expenses)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.strftime("%b %Y")   # e.g. "Jun 2025"

    df_grouped = df.groupby("month")["amount"].sum().reset_index()

    # Sort chronologically
    df_grouped["sort_key"] = pd.to_datetime(df_grouped["month"], format="%b %Y")
    df_grouped = df_grouped.sort_values("sort_key")

    fig = px.bar(
        df_grouped,
        x="month",
        y="amount",
        title="📅 Monthly Spending",
        labels={"month": "Month", "amount": "Total (INR)"},
        color="amount",
        color_continuous_scale="Blues",
        text="amount"
    )
    fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig.update_layout(height=400, coloraxis_showscale=False)
    return fig


def make_budget_bar(expenses: list, budgets: dict) -> go.Figure:
    """
    Horizontal bar chart comparing actual spending vs budget per category.
    """
    if not budgets:
        return _empty_chart("No budgets set yet. Add budgets to see this chart.")

    df = pd.DataFrame(expenses) if expenses else pd.DataFrame(columns=["category", "amount"])
    spent = df.groupby("category")["amount"].sum().to_dict()

    categories = list(budgets.keys())
    spent_vals  = [spent.get(cat, 0) for cat in categories]
    budget_vals = [budgets[cat] for cat in categories]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Spent",
        x=spent_vals,
        y=categories,
        orientation="h",
        marker_color=["#e74c3c" if s > b else "#2ecc71"
                      for s, b in zip(spent_vals, budget_vals)],
        text=[f"₹{v:,.0f}" for v in spent_vals],
        textposition="outside"
    ))

    fig.add_trace(go.Bar(
        name="Budget",
        x=budget_vals,
        y=categories,
        orientation="h",
        marker_color="rgba(52, 152, 219, 0.3)",
        text=[f"₹{v:,.0f}" for v in budget_vals],
        textposition="outside"
    ))

    fig.update_layout(
        title="🎯 Spent vs Budget by Category",
        barmode="overlay",
        height=400,
        xaxis_title="Amount (INR)",
        yaxis_title="Category"
    )
    return fig


def make_daily_line(expenses: list) -> go.Figure:
    """
    Line chart — daily spending trend over time.
    """
    if not expenses:
        return _empty_chart("No expenses yet to show.")

    df = pd.DataFrame(expenses)
    df["date"] = pd.to_datetime(df["date"])
    df_grouped = df.groupby("date")["amount"].sum().reset_index()
    df_grouped = df_grouped.sort_values("date")

    fig = px.line(
        df_grouped,
        x="date",
        y="amount",
        title="📈 Daily Spending Trend",
        labels={"date": "Date", "amount": "Total (INR)"},
        markers=True
    )
    fig.update_traces(line_color="#6c5ce7", marker_size=6)
    fig.update_layout(height=400)
    return fig


def _empty_chart(message: str) -> go.Figure:
    """Returns a blank chart with a friendly message."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, color="gray")
    )
    fig.update_layout(
        height=400,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    return fig


# ─── Quick test ───────────────────────────────────────────────

if __name__ == "__main__":
    # Dummy data to test charts
    sample_expenses = [
        {"title": "Groceries",   "amount": 1500, "category": "Food",      "date": "2025-06-01"},
        {"title": "Netflix",     "amount": 649,  "category": "Utilities", "date": "2025-06-02"},
        {"title": "Uber",        "amount": 320,  "category": "Transport", "date": "2025-06-03"},
        {"title": "Lunch",       "amount": 450,  "category": "Food",      "date": "2025-06-05"},
        {"title": "Electricity", "amount": 1200, "category": "Utilities", "date": "2025-05-20"},
        {"title": "Gym",         "amount": 800,  "category": "Health",    "date": "2025-05-25"},
    ]
    sample_budgets = {"Food": 3000, "Utilities": 1500, "Transport": 1000, "Health": 1000}

    print("📊 Testing charts — browser windows will open...\n")

    make_category_pie(sample_expenses).show()
    make_monthly_bar(sample_expenses).show()
    make_budget_bar(sample_expenses, sample_budgets).show()
    make_daily_line(sample_expenses).show()

    print("✅ All 4 charts opened successfully!")