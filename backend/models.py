import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('MY_SECRET_KEY')
if not key:
    raise ValueError("Error! Cannot find the API_KEY. Check file .env or AWS Config")

model = ChatGroq(model="llama-3.3-70b-versatile", api_key=key)