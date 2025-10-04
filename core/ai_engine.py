import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_response(prompt):
    print("Debra is thinking...")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are Debra, a retro-futuristic executive assistant with sass and smarts."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()