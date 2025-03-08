import os
from sqlalchemy import create_engine, Column, Integer, Float, Date, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import date
from dotenv import load_dotenv
import hashlib
import secrets
from contextlib import contextmanager

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Promzy1997@localhost/expense_tracker")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(Date, default=date.today)
    is_active = Column(Boolean, default=True)
    
    # Relationship with expenses
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")

    @staticmethod
    def hash_password(password):
        salt = secrets.token_hex(8)
        return f"{salt}${hashlib.sha256((password + salt).encode()).hexdigest()}"

    def verify_password(self, password):
        if not self.password_hash or '$' not in self.password_hash:
            return False
        salt, hash_value = self.password_hash.split('$')
        return hash_value == hashlib.sha256((password + salt).encode()).hexdigest()

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date, default=date.today)
    budget = Column(Float, default=0.0)
    
    # Income categories
    salary = Column(Float, default=0.0)
    side_job = Column(Float, default=0.0)
    gift = Column(Float, default=0.0)
    interest = Column(Float, default=0.0)
    
    # Expense categories
    food = Column(Float, default=0.0)
    transportation = Column(Float, default=0.0)
    grocery = Column(Float, default=0.0)
    savings = Column(Float, default=0.0)

    # Relationship with user
    user = relationship("User", back_populates="expenses")

def recreate_database():
    """Drop all tables and recreate them"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database recreated successfully.")

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    """Provide a database session for CRUD operations"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User management functions
def create_user(email, username, password):
    """Create a new user in the database"""
    with get_db() as db:
        try:
            user = User(
                email=email,
                username=username,
                password_hash=User.hash_password(password)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error creating user: {str(e)}")

def get_user_by_email(email):
    """Get a user by email"""
    with get_db() as db:
        return db.query(User).filter(User.email == email).first()

def get_user_by_username(username):
    """Get a user by username"""
    with get_db() as db:
        return db.query(User).filter(User.username == username).first()

def get_all_users():
    """Get all users (for debugging or admin purposes)"""
    with get_db() as db:
        return db.query(User).all()

# Expense management functions
def add_expense(
    user_id,
    date,
    budget=0.0,
    salary=0.0,
    side_job=0.0,
    gift=0.0,
    interest=0.0,
    food=0.0,
    transportation=0.0,
    grocery=0.0,
    savings=0.0
):
    """Add a new expense for a user"""
    with get_db() as db:
        try:
            expense = Expense(
                user_id=user_id,
                date=date,
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
            db.add(expense)
            db.commit()
            db.refresh(expense)
            return expense
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error adding expense: {str(e)}")

def get_expenses(user_id, start_date=None, end_date=None):
    """Get expenses for a user within a date range"""
    with get_db() as db:
        if not isinstance(user_id, int):
            raise ValueError(f"user_id must be an integer, but got {type(user_id).__name__}: {user_id}")
        
        query = db.query(Expense).filter(Expense.user_id == user_id)
        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)
        return query.all()

def get_latest_expense(user_id):
    """Get the latest expense for a user"""
    with get_db() as db:
        return db.query(Expense).filter(Expense.user_id == user_id).order_by(Expense.date.desc()).first()