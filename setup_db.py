from db_config import recreate_database

if __name__ == "__main__":
    print("Recreating database tables...")
    recreate_database()
    print("Database tables recreated successfully!") 