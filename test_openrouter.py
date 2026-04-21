from openai import OpenAI
from config import OPENROUTER_API_KEY

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

response = client.chat.completions.create(
    model="openai/gpt-oss-120b:free",
    messages=[
        {"role": "user", "content": "Say hello in one line"}
    ]
)

print(response.choices[0].message.content)