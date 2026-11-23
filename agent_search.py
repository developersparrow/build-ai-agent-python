import json
import os
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    raise SystemExit("No API key found. Put ANTHROPIC_API_KEY=your-key in a file named .env (see the README).")
client = anthropic.Anthropic(api_key=API_KEY)
MODEL = os.getenv("MODEL") or "claude-haiku-5-5"
MAX_TOKENS = int(os.getenv("MAX_TOKENS") or "16000")
MAX_STEPS = int(os.getenv("MAX_STEPS") or "10")
FOLDER = Path(os.getenv("AGENT_FOLDER") or "demo_project").expanduser().resolve()
if not FOLDER.is_dir():
    raise SystemExit("Project folder not found. Run build_demo.py first, or set AGENT_FOLDER (see the README).")
MAX_BYTES = int(os.getenv("MAX_BYTES") or "20000")
MAX_ITEMS = int(os.getenv("MAX_ITEMS") or "200")
MAX_MATCHES = int(os.getenv("MAX_MATCHES") or "50")


# a tool: look inside FOLDER
def look(path):
    outside = {"error": "That path is outside the folder I'm allowed to see."}
    # only paths relative to FOLDER
    if Path(path).anchor:
        return {"error": "Give a path relative to the project folder, not a full path."}
    target = (FOLDER / path).resolve()
    # check 1: stays inside FOLDER
    if not target.is_relative_to(FOLDER):
        return outside
    # check 2: no path to FOLDER's hidden names
    if any(part.startswith(".") for part in target.relative_to(FOLDER).parts):
        return {"error": "Hidden files are off limits: they often hold passwords and keys."}
    if target.is_dir():
        items = []
        for p in sorted(target.iterdir()):
            # listings skip hidden names and links
            if p.name.startswith(".") or p.is_symlink():
                continue
            if p.is_dir():
                items.append(p.name + "/")
            else:
                info = p.stat()
                changed = datetime.fromtimestamp(info.st_mtime).isoformat(timespec="minutes")
                items.append(f"{p.name} ({info.st_size} bytes, changed {changed})")
        return {"folder": path, "total": len(items), "items": items[:MAX_ITEMS]}
    # big files are refused
    if target.stat().st_size > MAX_BYTES:
        return {"error": f"File is bigger than {MAX_BYTES} bytes."}
    # special files are refused
    if not target.is_file():
        return {"error": "That's not a normal file."}
    return {"file": path, "text": target.read_text(encoding="utf-8")}


# a second tool: find text in FOLDER
def search(text):
    if not text:
        return {"error": "Give some text to search for."}
    matches = []
    for root, folders, files in os.walk(FOLDER):
        # change the list in place, so os.walk skips hidden folders
        folders[:] = sorted(f for f in folders if not f.startswith("."))
        for name in sorted(files):
            path = Path(root) / name
            try:
                # look's checks, and links skipped
                if path.is_symlink():
                    continue
                target = path.resolve()
                if not target.is_relative_to(FOLDER):
                    continue
                if any(part.startswith(".") for part in target.relative_to(FOLDER).parts):
                    continue
                if not target.is_file() or target.stat().st_size > MAX_BYTES:
                    continue
                lines = target.read_text(encoding="utf-8").split("\n")
            except (ValueError, OSError, RuntimeError):
                continue
            for number, line in enumerate(lines, 1):
                at = line.lower().find(text.lower())
                if at >= 0:
                    snippet = line[max(at - 100, 0):at + 100].strip()
                    matches.append(f"{path.relative_to(FOLDER)} line {number}: {snippet}")
    return {"text": text, "found": len(matches), "matches": matches[:MAX_MATCHES]}


# what the model reads about each tool
TOOLS = [{
    "name": "look",
    "description": f"Look inside the project folder. Give a folder path to list what's in it, or a file path to read it. Paths are relative to the project folder; use '.' for the top. Hidden files and links are left out, files over {MAX_BYTES} bytes are refused, and a folder shows its first {MAX_ITEMS} entries. You have no way to create, change or delete files. Never offer to make changes: give the user the change to make.",
    "input_schema": {
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    },
}, {
    "name": "search",
    "description": f"Find every line that contains some text, in all files of the project folder (not case-sensitive). Returns each file, line number and line. Use it to find things; use look to read a whole file. It can only read. Hidden files, links, files that aren't UTF-8 text and files over {MAX_BYTES} bytes are skipped; long lines are cut to 200 characters around the match; it shows the first {MAX_MATCHES} matches.",
    "input_schema": {
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
    },
}]
# each tool's name, to its function
RUN = {"look": look, "search": search}


# run one tool request
def run_tool(block):
    print(f"  [tool] {block.name} {block.input}")
    try:
        output = RUN[block.name](**block.input)
    except OSError as error:
        # a file error's short reason
        output = {"error": error.strerror or type(error).__name__}
    except Exception as error:
        # only the error's name goes back
        output = {"error": type(error).__name__}
    return {"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(output)}


# send the conversation, get the reply
def ask(messages):
    # the agent loop
    for _ in range(MAX_STEPS):
        response = client.messages.create(model=MODEL, max_tokens=MAX_TOKENS, tools=TOOLS, messages=messages)
        calls = [b for b in response.content if b.type == "tool_use"]
        if calls:
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": [run_tool(b) for b in calls]})
            continue
        answer = "".join(b.text for b in response.content if b.type == "text").strip()
        # an empty reply isn't kept
        if answer:
            messages.append({"role": "assistant", "content": response.content})
        # name any stop reason but end_turn
        if response.stop_reason != "end_turn":
            answer += f" [{response.stop_reason}]"
        return answer.strip() or "[no answer]"
    return f"[stopped after {MAX_STEPS} steps; set MAX_STEPS higher to allow more]"


# the conversation so far
messages = []
# the chat loop
while True:
    # Ctrl+C or Ctrl+D quits cleanly
    try:
        text = input("You: ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        break
    if text.lower() in ("quit", "exit"):
        break
    if not text:
        continue
    start = len(messages)
    messages.append({"role": "user", "content": text})
    try:
        print("Agent:", ask(messages))
    except anthropic.APIError as error:
        # the error's message, not a traceback
        print("Error:", error.message)
    except KeyboardInterrupt:
        print()
        break
    # a failed question is forgotten
    if messages[-1]["role"] != "assistant":
        del messages[start:]
