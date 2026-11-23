import os

import anthropic
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    raise SystemExit("No API key found. Put ANTHROPIC_API_KEY=your-key"
                     " in a file named .env (see the README).")
client = anthropic.Anthropic(api_key=API_KEY)
MODEL = "claude-haiku-5-5"
MAX_TOKENS = 16000


# send the conversation, get the reply
def ask(messages):
    response = client.messages.create(model=MODEL, max_tokens=MAX_TOKENS,
                                      messages=messages)
    messages.append({"role": "assistant", "content": response.content})
    return "".join(b.text for b in response.content if b.type == "text")


# the conversation so far
messages = []
# the chat loop
while True:
    text = input("You: ").strip()
    if text in ("quit", "exit"):
        break
    if text:
        messages.append({"role": "user", "content": text})
        print("Model:", ask(messages))
