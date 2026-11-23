import os
from pathlib import Path

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
FOLDER = Path(os.getenv("AGENT_FOLDER") or "demo_project").expanduser().resolve()
if not FOLDER.is_dir():
    raise SystemExit("Project folder not found. Run build_demo.py first,"
                     " or set AGENT_FOLDER (see the README).")


# a tool: look inside FOLDER
def look(path):
    target = (FOLDER / path).resolve()
    # check 1: stays inside FOLDER
    if not target.is_relative_to(FOLDER):
        return {"error": "That path is outside the folder I'm allowed to see."}
    # check 2: no path to FOLDER's hidden names
    if any(part.startswith(".") for part in target.relative_to(FOLDER).parts):
        return {"error": "Hidden files are off limits:"
                         " they often hold passwords and keys."}
    if target.is_dir():
        return [p.name + "/" if p.is_dir() else p.name
                for p in sorted(target.iterdir())]
    return target.read_text(encoding="utf-8")


# what the model reads about each tool
TOOLS = [{
    "name": "look",
    "description": (
        "Look inside the project folder."
        " Give a folder path to list what's in it, or a file path to read it."
        " Paths are relative to the project folder; use '.' for the top."
        " You have no way to create, change or delete files."
        " Never offer to make changes: give the user the change to make."
    ),
    "input_schema": {
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    },
}]


# send the conversation, get the reply
def ask(messages):
    response = client.messages.create(model=MODEL, max_tokens=MAX_TOKENS,
                                      tools=TOOLS, messages=messages)
    calls = [b for b in response.content if b.type == "tool_use"]
    if calls:
        return "[asks to run] " + ", ".join(f"{b.name} {b.input}" for b in calls)
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
