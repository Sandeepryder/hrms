from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Read database URL
DATABASE_URL = os.getenv("DATABASE_URL")
