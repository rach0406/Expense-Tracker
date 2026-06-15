import streamlit as st
import pandas as pd
from datetime import date
from database import init_db, add_expense, get_all_expenses, update_expense, delete_expense, set_budget, get_budgets
from currency import convert_to_inr, get_conversion_info, SUPPORTED_CURRENCIES
from charts import make_category_pie, make_monthly_bar, make_budget_bar, make_daily_line

# ─── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="SpendWise",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

CATEGORIES = ["Food", "Transport", "Utilities", "Health",
              "Shopping", "Entertainment", "Education", "Other"]

# ─── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #0f0f1a; color: #e2e8f0; }

[data-testid="stSidebar"] {
    background: #13131f !important;
    border-right: 1px solid #2d2d4a;
}

.metric-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #2d2d4a;
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: linear-gradient(180deg, #7c3aed, #a78bfa);
    border-radius: 4px 0 0 4px;
}
.metric-label {
    color: #718096;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.metric-value { color: #e2e8f0; font-size: 2rem; font-weight: 700; line-height: 1.1; }
.metric-sub   { color: #a78bfa; font-size: 0.82rem; margin-top: 6px; font-weight: 500; }

.alert-card {
    background: linear-gradient(135deg, #2d1515 0%, #1a0f0f 100%);
    border: 1px solid #7f1d1d;
    border-left: 4px solid #ef4444;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
    color: #fca5a5;
    font-size: 0.9rem;
}

.section-header {
    color: #a78bfa;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 32px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #2d2d4a;
}

.expense-row {
    background: #13131f;
    border: 1px solid #2d2d4a;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.expense-title  { font-weight: 600; color: #e2e8f0; font-size: 0.95rem; }
.expense-meta   { color: #718096; font-size: 0.8rem; margin-top: 2px; }
.expense-amount { color: #a78bfa; font-size: 1.1rem; font-weight: 700; text-align: right; }
.expense-date   { color: #718096; font-size: 0.78rem; text-align: right; margin-top: 2px; }

.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    background: #2d2d4a;
    color: #a78bfa;
    margin-top: 4px;
}

.stTextInput input, .stNumberInput input, .stTextArea textarea {
    background: #1a1a2e !important;
    border: 1px solid #2d2d4a !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

.stButton > button {
    background: white !important;
    color: #13131f !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 28px !important;
    font-weight: 700 !important;
    width: 100%;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #6d28d9, #5b21b6) !important;
    box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4) !important;
}

h1 { color: #e2e8f0 !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
h2 { color: #cbd5e0 !important; }
h3 { color: #a0aec0 !important; }

#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }

.conversion-box {
    background: #1a1a2e;
    border: 1px solid #4c1d95;
    border-radius: 10px;
    padding: 12px 16px;
    color: #c4b5fd;
    font-size: 0.88rem;
    font-weight: 500;
    margin-top: 8px;
    text-align: center;
}

.budget-row {
    background: #13131f;
    border: 1px solid #2d2d4a;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 10px;
}
.budget-cat  { font-weight: 600; color: #e2e8f0; margin-bottom: 8px; }
.budget-nums { display: flex; justify-content: space-between; color: #718096; font-size: 0.82rem; margin-bottom: 6px; }
.progress-bg { background: #2d2d4a; border-radius: 8px; height: 8px; overflow: hidden; }
.progress-ok   { background: linear-gradient(90deg, #22c55e, #16a34a); height: 8px; border-radius: 8px; }
.progress-warn { background: linear-gradient(90deg, #f59e0b, #d97706); height: 8px; border-radius: 8px; }
.progress-over { background: linear-gradient(90deg, #ef4444, #dc2626); height: 8px; border-radius: 8px; }

hr { border-color: #2d2d4a !important; }
            
div[data-testid="stSidebar"] * {
    color: #c9a7c6 !important;
}

label {
    color: #c9a7c6 !important;
}

::placeholder {
    color: #c9a7c6 !important;
    opacity: 0.6 !important;
}
            
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 8px 0;'>
        <div style='font-size:2.5rem;'>💸</div>
        <div style='font-size:1.2rem; font-weight:700; color:#e2e8f0; margin-top:4px;'>SpendWise</div>
        <div style='font-size:0.75rem; color:#c9a7c6; margin-top:2px;'>Personal Expense Tracker</div>
    </div>
    <hr/>
    """, unsafe_allow_html=True)

    page = st.radio("", ["📊 Dashboard", "➕ Expenses", "🎯 Budgets"])

    st.markdown("<hr/>", unsafe_allow_html=True)

    st.markdown("""
<hr/>
<div style='color:#4a5568; font-size:0.7rem; text-align:center;'>
    Streamlit · SQLite · ExchangeRate API
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# CHART THEME
# ══════════════════════════════════════════════════════════════
CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(19,19,31,0.6)",
    font=dict(color="#c9a7c6", family="Inter"),
    title_font=dict(color="#e2e8f0", size=15),
)


# ══════════════════════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.title("Dashboard")

    expenses = get_all_expenses()
    budgets  = get_budgets()

    this_month = [e for e in expenses if e["date"].startswith(str(date.today())[:7])]
    month_total = sum(e["amount"] for e in this_month)
    total_all   = sum(e["amount"] for e in expenses)
    avg_expense = (total_all / len(expenses)) if expenses else 0

    if expenses:
        df_temp  = pd.DataFrame(expenses)
        top_cat  = df_temp.groupby("category")["amount"].sum().idxmax()
        top_amt  = df_temp.groupby("category")["amount"].sum().max()
    else:
        top_cat, top_amt = "—", 0

    # Metric cards
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-label'>This Month</div>
            <div class='metric-value'>₹{month_total:,.0f}</div>
            <div class='metric-sub'>{len(this_month)} transactions</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-label'>Top Category</div>
            <div class='metric-value' style='font-size:1.4rem;'>{top_cat}</div>
            <div class='metric-sub'>₹{top_amt:,.0f} spent</div>
        </div>""", unsafe_allow_html=True)

    # Budget alerts
    if budgets and expenses:
        df = pd.DataFrame(expenses)
        spent_by = df.groupby("category")["amount"].sum().to_dict()
        alerts = [(c, spent_by.get(c, 0), l) for c, l in budgets.items()
                  if spent_by.get(c, 0) > l * 0.8]
        if alerts:
            st.markdown("<div class='section-header'>⚠️ Budget Alerts</div>", unsafe_allow_html=True)
            for cat, spent, lim in alerts:
                pct = (spent / lim) * 100
                icon = "🔴" if spent > lim else "🟡"
                label = "Over budget!" if spent > lim else "Approaching limit."
                st.markdown(f"<div class='alert-card'>{icon} <b>{cat}</b> — {label} Spent ₹{spent:,.0f} of ₹{lim:,.0f} ({pct:.0f}%)</div>",
                            unsafe_allow_html=True)

    # Charts
    st.markdown("<div class='section-header'>📈 Visualizations</div>", unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        fig = make_category_pie(expenses)
        fig.update_layout(**CHART_THEME)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with cb:
        fig = make_budget_bar(expenses, budgets)
        fig.update_layout(**CHART_THEME)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    


# ══════════════════════════════════════════════════════════════
# PAGE 2 — ADD EXPENSE
# ══════════════════════════════════════════════════════════════
elif page == "➕ Expenses":
    st.title("Expenses")
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            title    = st.text_input("Title", placeholder="e.g. Grocery run, Netflix...")
            amount   = float(st.text_input("Amount",placeholder="Enter Amount")or 0)
            currency = st.selectbox("Currency", SUPPORTED_CURRENCIES, index=0)
        with c2:
            category = st.selectbox("Category", CATEGORIES)
            exp_date = st.date_input("Date", value=date.today())
            notes    = st.text_area("Notes (optional)", placeholder="Any extra details...", height=105)

        submitted = st.form_submit_button("➕ Add Expense")
        if submitted:
            if not title.strip():
                st.error("Please enter a title.")
            else:
                inr_amount = convert_to_inr(amount, currency)
                add_expense(title.strip(), inr_amount, currency, category, str(exp_date), notes)
                if currency != "INR":
                    info = get_conversion_info(amount, currency, "INR")
                    st.markdown(f"<div class='conversion-box'>🔄 {info}</div>", unsafe_allow_html=True)
                st.success(f"✅ **{title}** added — ₹{inr_amount:,.2f} under {category}")

    st.markdown("<div class='section-header'>🕐 Recently Added</div>", unsafe_allow_html=True)
    for e in get_all_expenses()[:5]:
        st.markdown(f"""
        <div class='expense-row'>
            <div>
                <div class='expense-title'>{e['title']}</div>
                <span class='badge'>{e['category']}</span>
            </div>
            <div>
                <div class='expense-amount'>₹{e['amount']:,.2f}</div>
                <div class='expense-date'>{e['date']}</div>
            </div>
        </div>""", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>✏️ Edit an Expense</div>", unsafe_allow_html=True)
    all_expenses = get_all_expenses()
    titles_list = [f"#{e['id']} — {e['title']} (₹{e['amount']:,.0f})"
    for e in all_expenses]
    sel_label = st.selectbox("Select expense to edit", titles_list)
    sel_idx   = titles_list.index(sel_label)
    sel_e     = all_expenses[sel_idx]

    with st.form("edit_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_title    = st.text_input("Title",    value=sel_e["title"])
                new_amount   = float(st.text_input("Amount", value=str(sel_e["amount"])) or 0)
                new_currency = st.selectbox("Currency",  SUPPORTED_CURRENCIES,
                                            index=SUPPORTED_CURRENCIES.index(sel_e.get("currency","INR")))
            with c2:
                new_cat  = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(sel_e["category"]))
                new_date = st.date_input("Date", value=pd.to_datetime(sel_e["date"]))
                new_notes= st.text_area("Notes", value=sel_e.get("notes",""), height=105)

            if st.form_submit_button("💾 Save Changes"):
                inr_amount = convert_to_inr(new_amount, new_currency)
                update_expense(sel_e["id"], new_title, inr_amount, new_currency, new_cat, str(new_date), new_notes)
                st.success("✅ Expense updated!")
                st.rerun()
            if st.form_submit_button("🗑️ Delete Expense"):
                delete_expense(sel_e["id"])
                st.success("Expense deleted!")
                st.rerun()
  


# ══════════════════════════════════════════════════════════════
# PAGE 4 — BUDGETS
# ══════════════════════════════════════════════════════════════
elif page == "🎯 Budgets":
    st.title("Budgets")
    st.markdown("<div style='color:#718096; margin-bottom:24px;'>Set monthly spending limits. Get alerts when you're close to exceeding them.</div>", unsafe_allow_html=True)

    budgets  = get_budgets()
    expenses = get_all_expenses()
    this_month = [e for e in expenses if e["date"].startswith(str(date.today())[:7])]
    df = pd.DataFrame(this_month) if this_month else pd.DataFrame(columns=["category","amount"])
    spent_by = df.groupby("category")["amount"].sum().to_dict() if not df.empty else {}

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='section-header'>➕ Set Budget</div>", unsafe_allow_html=True)
        with st.form("budget_form"):
            b_cat   = st.selectbox("Category", CATEGORIES)
            b_limit_text = float(st.text_input("Monthly Limit (INR)", placeholder="Enter Monthly Budget") or 0)
            if st.form_submit_button("💾 Save Budget"):
                try:
                    b_limit = float(b_limit_text)

                    if b_limit <= 0:
                        st.error("Please enter a valid budget amount.")
                    else:
                        set_budget(b_cat, b_limit)
                        st.success(f"✅ {b_cat} → ₹{b_limit:,.0f}/month")
                        st.rerun()

                except ValueError:
                    st.error("Please enter numbers only.")
                
    with c2:
        st.markdown("<div class='section-header'>📊 This Month's Progress</div>", unsafe_allow_html=True)
        if not budgets:
            st.markdown("<div style='color:#4a5568; padding:20px;'>No budgets yet. Add one!</div>", unsafe_allow_html=True)
        else:
            for cat, lim in budgets.items():
                spent = spent_by.get(cat, 0)
                pct   = min((spent / lim) * 100, 100)
                cls   = "progress-ok" if pct < 70 else ("progress-warn" if pct < 100 else "progress-over")
                icon  = "✅" if pct < 70 else ("⚠️" if pct < 100 else "🔴")
                st.markdown(f"""
                <div class='budget-row'>
                    <div class='budget-cat'>{icon} {cat}</div>
                    <div class='budget-nums'>
                        <span>Spent: ₹{spent:,.0f}</span>
                        <span>Limit: ₹{lim:,.0f}</span>
                    </div>
                    <div class='progress-bg'><div class='{cls}' style='width:{pct:.1f}%'></div></div>
                    <div style='color:#4a5568; font-size:0.75rem; margin-top:6px; text-align:right;'>{pct:.0f}% used</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>📈 Spent vs Budget Chart</div>", unsafe_allow_html=True)
    fig = make_budget_bar(expenses, budgets)
    fig.update_layout(**CHART_THEME)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})