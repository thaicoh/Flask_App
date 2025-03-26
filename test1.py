import os
from dotenv import load_dotenv

load_dotenv()

print("DB_HOST:", os.getenv("DB_HOST"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_PASS:", os.getenv("DB_PASS"))
print("DB_NAME:", os.getenv("DB_NAME"))
print("SECRET_KEY:", os.getenv("SECRET_KEY"))
