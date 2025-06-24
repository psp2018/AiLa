import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Load your .env file
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Summarize Article 15 of the GDPR"}
    ]
)

print(response.choices[0].message.content)