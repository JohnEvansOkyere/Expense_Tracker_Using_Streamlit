import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from db_config import add_expense, get_expenses, get_latest_expense, get_user_by_email, get_user_by_username, create_user

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'show_signup' not in st.session_state:
        st.session_state.show_signup = False

# Call the initialization function
init_session_state()

# Page Configuration
st.set_page_config(page_title="Personal Expense Tracker", page_icon="💰", layout="wide")

# Title and Styling
st.title(":bar_chart: Personal Expense Tracker")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)
st.markdown("""
    <style>
    .metric-card {
        border-radius: 5px;
        padding: 15px;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .positive {
        background-color: #dcf7dc;
        color: #0f5132;
    }
    .negative {
        background-color: #f8d7da;
        color: #842029;
    }
    .warning {
        background-color: #fff3cd;
        color: #664d03;
    }
    .normal {
        background-color: #e7f1ff;
        color: #084298;
    }
    .bold-text {
        font-size: 24px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Login Page
def login_page():
    """Display the login page"""
    st.title("Login to Expense Tracker")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not email or not password:
                st.error("Please fill in all fields")
                return
                
            user = get_user_by_email(email)
            if user and user.verify_password(password):
                st.session_state.authenticated = True
                st.session_state.user = user
                st.success("Login successful!")
                st.rerun()  # Refresh the app to show the main interface
            else:
                st.error("Invalid email or password")
    
    st.markdown("---")
    st.write("Don't have an account?")
    if st.button("Sign Up"):
        st.session_state.show_signup = True
        st.rerun()

# Signup Page
def signup_page():
    """Display the signup page"""
    st.title("Create an Account")
    
    with st.form("signup_form"):
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            if not all([email, username, password, confirm_password]):
                st.error("Please fill in all fields")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            if get_user_by_email(email):
                st.error("Email already registered")
                return
                
            if get_user_by_username(username):
                st.error("Username already taken")
                return
            
            try:
                user = create_user(email, username, password)
                if user:
                    st.success("Account created successfully! Please log in.")
                    st.session_state.show_signup = False
                    st.rerun()
                else:
                    st.error("Error creating account. Please try again.")
            except Exception as e:
                st.error(f"Error creating account: {str(e)}")
    
    st.markdown("---")
    st.write("Already have an account?")
    if st.button("Login"):
        st.session_state.show_signup = False
        st.rerun()

# Main Interface
def main_interface():
    """Display the main interface"""
    # Sidebar for Navigation
    st.sidebar.header("Filter Panel")
    filter_option = st.sidebar.radio(
        "Select View:",
        ("Overview / Summary", "Budget", "Income", "Expenses")
    )

    # Logout button in the sidebar
    st.markdown("""
        <style>
        .stButton button {
            background-color: black;
            color: white;
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("Logout"):
        # Reset session state variables
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.show_signup = False
        st.rerun()  # Refresh the app to return to the login page

    # Date range selector
    st.sidebar.header("Date Range")
    start_date = st.sidebar.date_input("Start Date", value=date.today() - timedelta(days=30))
    end_date = st.sidebar.date_input("End Date", value=date.today())

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

    # Save button
    if st.sidebar.button("Save Expense"):
        if not st.session_state.authenticated or not st.session_state.user:
            st.error("Please log in to save expenses.")
        else:
            user_id = st.session_state.user.id  # Get the user_id from session state
            add_expense(
                user_id=user_id,  # Pass user_id
                date=selected_date,
                budget=budget,
                salary=salary,
                side_job=side_job,
                gift=gift,
                interest=interest,
                food=food,
                transportation=transportation,
                grocery=grocery,
                savings=savings
            )
            st.sidebar.success("Details saved successfully!")

    # Initialize df as an empty DataFrame
    df = pd.DataFrame()

    # Get expenses for the selected date range
    if not st.session_state.authenticated or not st.session_state.user:
        st.error("Please log in to view your expenses.")
    else:
        user_id = st.session_state.user.id  # Get the user_id from session state
        expenses = get_expenses(user_id, start_date, end_date)  # Pass user_id as the first argument
        df = pd.DataFrame([{
            'date': exp.date,
            'budget': exp.budget,
            'salary': exp.salary,
            'side_job': exp.side_job,
            'gift': exp.gift,
            'interest': exp.interest,
            'food': exp.food,
            'transportation': exp.transportation,
            'grocery': exp.grocery,
            'savings': exp.savings
        } for exp in expenses])

    # Calculate totals from the database
    if not df.empty:
        total_income = df[['salary', 'side_job', 'gift', 'interest']].sum().sum()
        total_expenses = df[['food', 'transportation', 'grocery', 'savings']].sum().sum()
        balance = total_income - total_expenses
        budget = df['budget'].iloc[-1]  # Get the most recent budget
        remaining_budget = budget - total_expenses
    else:
        total_income = salary + side_job + gift + interest
        total_expenses = food + transportation + grocery + savings
        balance = total_income - total_expenses
        remaining_budget = budget - total_expenses

    # Display Based on Selected Filter
    if filter_option == "Overview / Summary":
        st.subheader("Overview / Summary")

        # Display Total Income, Total Expenses, Total Budget, and Total Balance
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            st.markdown(
                f"""
                <div class="metric-card normal">
                    <h3>💵 Total Income</h3>
                    <h2 class="bold-text">GHS {total_income:.2f}</h2>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div class="metric-card normal">
                    <h3>📉 Total Expenses</h3>
                    <h2 class="bold-text">GHS {total_expenses:.2f}</h2>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div class="metric-card normal">
                    <h3>📊 Total Budget</h3>
                    <h2 class="bold-text">GHS {budget:.2f}</h2>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col4:
            balance_status = "positive" if balance >= 0 else "negative"
            balance_icon = "💰" if balance >= 0 else "⚠️"
            st.markdown(
                f"""
                <div class="metric-card {balance_status}">
                    <h3>{balance_icon} Total Balance</h3>
                    <h2 class="bold-text">GHS {balance:.2f}</h2>
                    <p>{"Surplus" if balance >= 0 else "Deficit"}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Display Budget Status
        st.markdown("---")
        st.subheader("Budget Status")

        if budget > 0:
            budget_percentage = min((total_expenses / budget) * 100, 100)
            st.progress(budget_percentage / 100)
            st.write(f"Budget utilized: {budget_percentage:.1f}%")

            if total_expenses > budget:
                exceeded_amount = total_expenses - budget
                st.error(f"Budget Exceeded by GHS {exceeded_amount:.2f}! Please review your expenses.")
            else:
                st.success("Under Budget")

        st.markdown("---")
        st.subheader("Visual Analysis")
        
        col1, col2 = st.columns(2)

        # Income vs Expenses Chart
        with col1:
            if not df.empty:
                income_vs_expenses = pd.DataFrame({
                    "Category": ["Total Income", "Total Expenses"],
                    "Amount": [total_income, total_expenses]
                })
                fig = px.bar(income_vs_expenses, x="Category", y="Amount", title="Income vs Expenses", color="Category",
                            text_auto='.2s', height=400)
                st.plotly_chart(fig, use_container_width=True)

        # Expense Breakdown Chart
        with col2:
            if not df.empty:
                expense_cols = ['food', 'transportation', 'grocery', 'savings']
                expense_data = pd.DataFrame({
                    "Category": ["Food", "Transportation", "Grocery", "Savings"],
                    "Amount": df[expense_cols].sum().values
                })
                fig = px.pie(expense_data, names="Category", values="Amount", title="Expense Breakdown", height=400)
                st.plotly_chart(fig, use_container_width=True)

        # Show expense history
        if not df.empty:
            st.subheader("Expense History")
            st.dataframe(df.sort_values('date', ascending=False))

    elif filter_option == "Budget":
        st.subheader("Budget Management")
        st.write(f"### Monthly Budget: GHS {budget:.2f}")
        st.metric(label="Remaining Budget", value=f"GHS {remaining_budget:.2f}", delta=f"{remaining_budget:.2f}")

        if remaining_budget < 0:
            st.error("You have exceeded your budget. Consider revising your expenses.")
        else:
            st.success("You are within your budget. Keep it up!")

        if not df.empty:
            # Budget trend over time
            budget_trend = df[['date', 'budget']].drop_duplicates()
            fig = px.line(budget_trend, x='date', y='budget', title='Budget History')
            st.plotly_chart(fig, use_container_width=True)

    elif filter_option == "Income":
        st.subheader("Income Breakdown")

        if not df.empty:
            total_salary = df['salary'].sum()
            total_side_job = df['side_job'].sum()
            total_gift = df['gift'].sum()
            total_interest = df['interest'].sum()

            st.write(f"💼 Total Salary: GHS {total_salary:.2f}")
            st.write(f"🏷️ Total Side Job: GHS {total_side_job:.2f}")
            st.write(f"🎁 Total Gifts: GHS {total_gift:.2f}")
            st.write(f"💰 Total Interest: GHS {total_interest:.2f}")

            income_data = pd.DataFrame({
                "Category": ["Salary", "Side Job", "Gifts", "Interest"],
                "Amount": [total_salary, total_side_job, total_gift, total_interest]
            })

            fig = px.pie(income_data, names="Category", values="Amount", title="Income Distribution", height=400)
            st.plotly_chart(fig, use_container_width=True)

            # Income trend over time
            income_trend = df.melt(id_vars=['date'], 
                                 value_vars=['salary', 'side_job', 'gift', 'interest'],
                                 var_name='Category', value_name='Amount')
            fig = px.line(income_trend, x='date', y='Amount', color='Category', title='Income Trends')
            st.plotly_chart(fig, use_container_width=True)

    elif filter_option == "Expenses":
        st.subheader("Expense Breakdown")

        if not df.empty:
            total_food = df['food'].sum()
            total_transportation = df['transportation'].sum()
            total_grocery = df['grocery'].sum()
            total_savings = df['savings'].sum()

            st.write(f"🍲 Total Food: GHS {total_food:.2f}")
            st.write(f"🚗 Total Transportation: GHS {total_transportation:.2f}")
            st.write(f"🛒 Total Grocery: GHS {total_grocery:.2f}")
            st.write(f"💳 Total Savings: GHS {total_savings:.2f}")

            expense_data = pd.DataFrame({
                "Category": ["Food", "Transportation", "Grocery", "Savings"],
                "Amount": [total_food, total_transportation, total_grocery, total_savings]
            })

            fig = px.bar(expense_data, x="Category", y="Amount", title="Expenses by Category", text_auto='.2s', height=400)
            st.plotly_chart(fig, use_container_width=True)

            # Expense trend over time
            expense_trend = df.melt(id_vars=['date'], 
                                  value_vars=['food', 'transportation', 'grocery', 'savings'],
                                  var_name='Category', value_name='Amount')
            fig = px.line(expense_trend, x='date', y='Amount', color='Category', title='Expense Trends')
            st.plotly_chart(fig, use_container_width=True)

    # Footer
    st.markdown("---")
    st.write(f"Data recorded for: {selected_date}")
    st.caption("Built by John Evans Okyere")

# Main App Logic
if not st.session_state.authenticated:
    if st.session_state.show_signup:
        signup_page()
    else:
        login_page()
else:
    main_interface()