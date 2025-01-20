import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

# Page Configuration
st.set_page_config(page_title="Personal Expense Tracker", page_icon="💰", layout="wide")

# Title and Styling
st.title(":bar_chart: Personal Expense Tracker")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

# Sidebar for Navigation
st.sidebar.header("Filter Panel")
filter_option = st.sidebar.radio(
    "Select View:",
    ("Overview / Summary", "Budget", "Income", "Expenses")
)

# Sidebar for Inputs
st.sidebar.header("Enter Your Details")
selected_date = st.sidebar.date_input("Select Date", value=date.today())

# Budget Input
st.sidebar.subheader("Set Your Budget")
budget = st.sidebar.number_input("Monthly Budget (GHS):", min_value=0.0, value=0.0, step=1.0)

# Income Inputs
st.sidebar.subheader("Income Categories")
salary = st.sidebar.number_input("Salary", min_value=0.0, value=0.0, step=1.0)
side_job = st.sidebar.number_input("Side Job", min_value=0.0, value=0.0, step=1.0)
gift = st.sidebar.number_input("Gifts", min_value=0.0, value=0.0, step=1.0)
interest = st.sidebar.number_input("Interest Income", min_value=0.0, value=0.0, step=1.0)

# Expense Inputs
st.sidebar.subheader("Expense Categories")
food = st.sidebar.number_input("Food", min_value=0.0, value=0.0, step=1.0)
transportation = st.sidebar.number_input("Transportation", min_value=0.0, value=0.0, step=1.0)
grocery = st.sidebar.number_input("Grocery", min_value=0.0, value=0.0, step=1.0)
savings = st.sidebar.number_input("Savings", min_value=0.0, value=0.0, step=1.0)

# Calculations
total_income = salary + side_job + gift + interest
total_expenses = food + transportation + grocery + savings
balance = total_income - total_expenses
remaining_budget = budget - total_expenses

# Display Based on Selected Filter
if filter_option == "Overview / Summary":
    st.subheader("Overview / Summary")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Income", value=f"GHS {total_income:.2f}")
    with col2:
        st.metric(label="Total Expenses", value=f"GHS {total_expenses:.2f}")
    with col3:
        st.metric(label="Balance", value=f"GHS {balance:.2f}", delta=f"{balance:.2f}")

    st.subheader("Visual Analysis")
    col1, col2 = st.columns(2)

    # Income vs Expenses Chart
    with col1:
        income_vs_expenses = pd.DataFrame({
            "Category": ["Total Income", "Total Expenses"],
            "Amount": [total_income, total_expenses]
        })
        fig = px.bar(income_vs_expenses, x="Category", y="Amount", title="Income vs Expenses", color="Category",
                     text_auto='.2s', height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Expense Breakdown Chart
    with col2:
        expense_data = pd.DataFrame({
            "Category": ["Food", "Transportation", "Grocery", "Savings"],
            "Amount": [food, transportation, grocery, savings]
        })
        fig = px.pie(expense_data, names="Category", values="Amount", title="Expense Breakdown", height=400)
        st.plotly_chart(fig, use_container_width=True)

elif filter_option == "Budget":
    st.subheader("Budget Management")
    st.write(f"### Monthly Budget: GHS {budget:.2f}")
    st.metric(label="Remaining Budget", value=f"GHS {remaining_budget:.2f}", delta=f"{remaining_budget:.2f}")

    if remaining_budget < 0:
        st.warning("You have exceeded your budget. Consider revising your expenses.")
    else:
        st.success("You are within your budget. Keep it up!")

elif filter_option == "Income":
    st.subheader("Income Breakdown")

    st.write(f"💼 Salary: GHS {salary:.2f}")
    st.write(f"🏷️ Side Job: GHS {side_job:.2f}")
    st.write(f"🎁 Gifts: GHS {gift:.2f}")
    st.write(f"💰 Interest: GHS {interest:.2f}")

    income_data = pd.DataFrame({
        "Category": ["Salary", "Side Job", "Gifts", "Interest"],
        "Amount": [salary, side_job, gift, interest]
    })

    fig = px.pie(income_data, names="Category", values="Amount", title="Income Distribution", height=400)
    st.plotly_chart(fig, use_container_width=True)

elif filter_option == "Expenses":
    st.subheader("Expense Breakdown")

    st.write(f"🍲 Food: GHS {food:.2f}")
    st.write(f"🚗 Transportation: GHS {transportation:.2f}")
    st.write(f"🛒 Grocery: GHS {grocery:.2f}")
    st.write(f"💳 Savings: GHS {savings:.2f}")

    expense_data = pd.DataFrame({
        "Category": ["Food", "Transportation", "Grocery", "Savings"],
        "Amount": [food, transportation, grocery, savings]
    })

    fig = px.bar(expense_data, x="Category", y="Amount", title="Expenses by Category", text_auto='.2s', height=400)
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.write(f"Data recorded for: {selected_date}")
st.caption("Personal Expense Tracker | Streamlit App")
