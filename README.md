# Build an AI Agent in Python from Scratch

Lesson 1 of the series "Build Your Own AI Agent in Python: Tools, Automation & Memory".

In this lesson we build an AI agent in one short Python file: a chat with the model, one tool (`look`, which can list a folder or read a text file inside one project folder), and the loop that lets the model decide which files to open. Then we ask it why a small shop app's nightly report crashed.

## What's in this folder

| File | What it is |
|---|---|
| **The video's files** | **What we type in the video** |
| `part1_chat.py` | Part 1: a plain chat with the model in your terminal |
| `part2_tool.py` | Part 2: adds a simple `look` tool. The model can ask for it, but nothing runs it yet |
| `part3_loop.py` | Part 3: the loop. The finished agent we type in the video |
| **The full version** | **Use this one on your own projects** |
| `agent.py` | The same agent, with more checks and plainer error messages |
| `agent_search.py` | The answer to the exercise, built on `agent.py` (try it yourself first) |
| **The rest** | |
| `build_demo.py` | Makes `demo_project/`, the shop app whose report crashed "last night" |
| `requirements.txt` | The two libraries, at the versions we tested |
| `.env.example` | A template for your `.env` file |
| `.gitignore` | Keeps `.env` (your key) and the folders the setup makes out of git |

Following along with the video? Type the code into a new file, `my_agent.py`. At the end of each part it should match that part's file (`part1_chat.py`, `part2_tool.py`, `part3_loop.py`), so use those files to compare or to catch up.

## What you need

- Python. We used Python 3.14. If you're installing Python now, choose 3.14. Other versions may work, but we haven't tested them.
- An Anthropic API key with a little credit, from the Claude Console (see "Get an API key"). Each question about the demo cost us under $0.002 with the default model (measured in November 2026; check Anthropic's pricing page for today's prices). Questions about a bigger project cost more, because the agent reads more and every question resends the whole chat.
- A terminal and a plain-text editor.

We recorded and tested on Ubuntu 22.04. The Windows and macOS steps below are written carefully but **not tested by us**. If something fails, tell us in the comments: your OS, your Python version and the error. Never paste your key, and remove your user name from any file paths you paste.

## Get an API key

Your key comes from the Claude Console, Anthropic's website for API keys and billing. These steps follow Anthropic's page "Get your Claude API key" (https://platform.claude.com/docs/en/get-api-key) as it read in November 2026. If the Console looks different, follow that page.

1. Go to https://platform.claude.com and sign in, or create an account.
2. Open the API keys page: https://platform.claude.com/settings/keys
3. Click **Create key**. In the form, give the key a **Name**, choose when it **Expires**, and set **Linked account** to yourself.
4. Set **Scope** to **Default workspace**, not **Organization**. This lesson's code sends no workspace ID, and a key scoped to the Organization must send one with every request: it fails on the first question with a 400 error.
5. Copy the key, which starts with `sk-ant-`. The Console shows it only once. You'll paste it into `.env` in "Set up". If you lose it, create a new key.
6. Credit: Anthropic says new users receive free credits to test the API. To buy credits, go to the Billing page: https://platform.claude.com/settings/billing

When the key expires, every question fails with an `authentication_error`. An expired key can't be turned back on: create a new one.

## Set up

First, unzip the download (Windows: right-click the zip and choose "Extract All") and open a terminal in this folder (the one with this README):

- Ubuntu: open the folder in Files, right-click an empty spot and choose "Open in Terminal".
- Windows 11 (not tested by us): open the folder in File Explorer, right-click an empty spot and choose "Open in Terminal".
- macOS (not tested by us): open Terminal, type `cd ` (with a space after it), drag the folder onto the window and press Enter.

Type `ls` (Windows: `dir`) and press Enter. You should see `requirements.txt`. Run every command in this README in this terminal.

Run the lines in each block below one at a time, and read what each prints. The first line shows your Python version. If you have more than one Python, name the one you want in the `venv` line, for example `python3.14 -m venv .venv` (Windows: `py -3.14 -m venv .venv`). If you run a `venv` line again, because it failed or to use a different Python, add `--clear` so it replaces the old environment (`python3.14 -m venv --clear .venv`), then run the `activate` and `pip install` lines again. After the `activate` line, `python --version` shows which Python the environment uses.

If pip prints a notice that a new pip release is available, you can ignore it.

### Ubuntu / Linux (tested on Ubuntu 22.04)

```
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

If `python3 -m venv` says ensurepip is not available, install the package the message names (for example `sudo apt install python3.12-venv`), then run `python3 -m venv --clear .venv` and the `activate` and `pip install` lines again.

### Windows (not tested by us)

In PowerShell:

```
py --version
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
```

If PowerShell refuses to run `Activate.ps1`, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use Command Prompt and `.venv\Scripts\activate.bat`.

### macOS (not tested by us)

```
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

### Put your key in `.env`

Open `.env` in a plain-text editor and paste your key after the `=` sign. File windows may hide `.env`, because its name starts with a dot: on Ubuntu, press Ctrl+H in Files or in the editor's Open window to show it; from the same terminal, `notepad .env` opens it on Windows and `open -e .env` on macOS.

```
ANTHROPIC_API_KEY=your-key-here
```

- No quotes and no spaces around the key.
- Save it as plain text (UTF-8). On Windows, Notepad may save it as `.env.txt` while Explorer hides the `.txt`: turn on "File name extensions" to check. Don't create it with `echo ... > .env` in Windows PowerShell 5: that writes a format Python can't read.
- On macOS, keep TextEdit in plain-text mode (Format, Make Plain Text).
- Run the `cp` line (Windows: `copy`) only once: running it again replaces `.env` with the empty template.
- Never share or commit `.env`. It holds your key.

## Run it

Run everything from this folder, with the virtual environment active: you'll see `(.venv)` at the start of the prompt. In a new terminal, go to this folder (see the start of "Set up") and run the `activate` line again first.

```
python build_demo.py
python agent.py
```

`build_demo.py` makes `demo_project/` with dates based on the last time the demo's report ran (it runs every night at 02:14), so "last night" is in the past at any hour. Run it again any time to reset the demo, and after 02:14 passes while you work (the demo is then a day old): it deletes and rebuilds `demo_project/` in the current folder, so close any demo files you opened (for example a CSV in Excel) first.

Then ask:

```
You: Why did my nightly report crash last night?
```

Type `quit` or `exit` to stop. Ctrl+C or Ctrl+D (Ctrl+Z then Enter on Windows) also ends the program.

Ask one question per line. If you paste several lines at once, each line becomes its own question (and its own cost); Ctrl+C stops it.

`part1_chat.py`, `part2_tool.py`, `part3_loop.py` and `agent_search.py` run the same way (`python part1_chat.py`). All of them except `part1_chat.py` need a folder to look in: `demo_project/` (run `build_demo.py` first) or your own `AGENT_FOLDER`.

The video's files are kept simple. `part2_tool.py` has two checks (the folder, and hidden names such as `.env`), and no tool writes; nothing runs its tool yet. `part3_loop.py` has the same two checks, a step cap, and no tool writes. Neither has a file-size limit, and `part3_loop.py` lists hidden names in a folder, but refuses any path that leads to one of them. In all three, an API error (a bad key, no credit, no network), Ctrl+C or Ctrl+D ends the program with a long error message (a traceback). `agent.py` adds more checks, including for big files, links and special files, and plainer error messages; use it on your own projects.

## Settings

All settings are optional. Put them in `.env` (or set them in your terminal). A blank value means the default. `agent_search.py` reads every setting below, and `agent.py` all but `MAX_MATCHES`. Of these, `part2_tool.py` and `part3_loop.py` read only `AGENT_FOLDER`, and `part1_chat.py` reads none: the video's files set `MODEL` and `MAX_TOKENS` (and `part3_loop.py` its `MAX_STEPS`) in their top lines.

| Setting | Default | What it does |
|---|---|---|
| `MODEL` | `claude-haiku-5-5` | Which Claude model answers. If you change it, check its price first |
| `MAX_TOKENS` | `16000` | The most the model may write per model call (one question can take several), including its hidden thinking. Keep it at 20000 or less: above about 21,000 the library refuses the request and the program stops with a long error message (a traceback) |
| `MAX_STEPS` | `10` | The most model calls for one question, so it can't loop forever |
| `AGENT_FOLDER` | `demo_project` | The only folder the agent may look into. Relative to where you run it; `~` works |
| `MAX_BYTES` | `20000` | (`agent.py` and `agent_search.py`) files bigger than this are refused (to keep cost low) |
| `MAX_ITEMS` | `200` | (`agent.py` and `agent_search.py`) a folder listing shows at most this many entries |
| `MAX_MATCHES` | `50` | (`agent_search.py`) at most this many search results |

A setting already set in your terminal wins over `.env`. If you change `.env` and nothing changes, check that the same name isn't set in your terminal or shell profile. The video's two runs on the lesson folder type `AGENT_FOLDER=.` before the command, a form for Ubuntu's terminal, not for PowerShell or Command Prompt. On any system, you can instead put `AGENT_FOLDER=.` on its own line in `.env` (tested by us on Ubuntu only) and run `python agent.py` (or your `my_agent.py`). Then delete that line, so later runs use `demo_project/` again.

## Try it on your own project

Set `AGENT_FOLDER` to a project folder of yours, run `python agent.py` (the full version), and ask:

- Explain this project.
- What's the tech stack?
- Suggest the top 3 improvements.

AI agents can be confidently wrong, so always check what it tells you.

Everything the agent reads is sent to Anthropic's API, so only point it at folders you're fine sharing. Never point it at your home folder or the top of your disk.

## What the agent can and can't do

This is the full version, `agent.py` (and `agent_search.py`). The video's files have fewer checks: see "Run it".

- It can only read. No tool can create, change or delete files.
- It can only see `AGENT_FOLDER`. Paths that lead outside the folder, even through links, are refused by our code, not just by the model, and full paths are refused before anything is opened.
- Hidden names (names starting with a dot, like `.env`) are never listed. Before anything is read, our code follows any symbolic links to where the path really leads, and refuses it if any name on that path inside `AGENT_FOLDER` starts with a dot, so no symbolic link can reach a hidden file or folder that is inside `AGENT_FOLDER` (hard links and mounted folders are different: see the next point). `AGENT_FOLDER`'s own name, and the names of the folders above it, are not checked. A symbolic link with a hidden name is treated as the file it leads to, so one that leads to a file inside `AGENT_FOLDER` is not refused as hidden if no name on that path inside `AGENT_FOLDER` starts with a dot. Files with the Windows "hidden" attribute but no dot are not hidden to the agent.
- Links are left out of listings and search (on Windows, a folder junction may be listed, but reading through it to outside the folder is still refused). Hard links and mounted folders inside `AGENT_FOLDER` look like normal files and folders, so the agent can read through them.
- Our code checks a path just before it reads it, so another program that swaps part of the path for a symbolic link at that moment can get past some of these checks.
- Files can contain text that tries to steer the agent. Check any command or change it suggests before you run it.

## When something goes wrong

Find what you see in the left column. If the program stops with a long error message (a traceback), look at its last line. The video's files print no `Error:` line: an API error stops them with a traceback, and its last line holds the same words as the `Error:` rows below.

| You see | What it means | What to do |
|---|---|---|
| `Could not open requirements file`, `can't open file` (with a `.py` name), or `.venv/bin/activate: No such file or directory` | The terminal isn't in this folder, or the `venv` line didn't finish | Go to this folder (see the start of "Set up"), then run the `venv`, `activate` and `pip install` lines |
| `No matching distribution found` or `Could not find a version that satisfies the requirement` | Your Python is older than these library versions support | Use Python 3.14 (see "What you need"), then make the environment again with `--clear` (see "Set up") |
| `python: command not found` (Ubuntu: `Command 'python' not found`; macOS: `zsh: command not found: python`), or `ModuleNotFoundError: No module named 'anthropic'` (or `'dotenv'`) | The virtual environment isn't active (every new terminal needs it again), or the install step was skipped | Go to this folder, run the `activate` line from "Set up", then the `pip install` line |
| `No API key found` | No key in `.env` or in your terminal | Put the key in `.env` (see above). Check the file is named exactly `.env` and sits in this folder |
| `Project folder not found` | `demo_project/` (or your `AGENT_FOLDER`) isn't there | Run `python build_demo.py`, and run everything from this folder |
| `Error: ...` with `authentication_error` | The key is wrong, revoked or expired, or an old key set in your terminal wins over `.env` | Check the key in the Claude Console (an expired key can't be turned back on: create a new one); see "Settings" |
| `Error: ...` with `not scoped to a workspace` | The key's Scope is "Organization", and this code sends no workspace ID | Make a key with Scope "Default workspace" (see "Get an API key") and put it in `.env`. An old key set in your terminal wins over `.env`: see "Settings" |
| `Error: ...` that mentions your credit balance | Your account has no credit left | Add credit on the Claude Console's Billing page, then ask again |
| `Error: ...` with `not_found_error` and `model` | `MODEL` names a model that doesn't exist, or one Anthropic has retired (this can happen to the default too) | Fix the name, or remove the `MODEL` line to use the default. If the default itself is retired, set `MODEL` to a current Haiku model from Anthropic's models page, and check its price |
| `Error: ...` with `overloaded_error` or `rate_limit_error` | The API is busy, or you asked many questions quickly | Wait a minute and ask again |
| `Error: Connection error.` or `Error: Request timed out ...` | No connection to the API | Check your internet, VPN or proxy |
| `Error: ...` with `prompt is too long` | The chat got longer than the model can read (every question resends the whole chat) | Type `quit` and start again |
| (`agent.py`) A reply that starts with `[` or with `Error:` | That question didn't finish, and the agent has forgotten it, including any files it looked at | Ask again |
| (`agent.py`) `[max_tokens]` | The reply hit `MAX_TOKENS`. With no text before it, the model spent the whole budget thinking | Ask again. If it keeps happening, ask a narrower question or raise `MAX_TOKENS` (20000 or less) |
| (`agent.py`) `[refusal]` | The model declined to answer | Rephrase, or type `quit` and start again |
| `[stopped after 10 steps]` (`agent.py`: `[stopped after 10 steps; ...]`) | The question needed more model calls than `MAX_STEPS` | Raise `MAX_STEPS` (in `part3_loop.py`, in its top lines), or ask a narrower question |
| `ValueError: Streaming is required ...` | `MAX_TOKENS` is too high: above about 21,000, or lower for some older models | Set it to 20000 or less (or remove the line). If this started after you changed `MODEL`, also set `MAX_TOKENS=8000`, or remove the `MODEL` line |
| (`agent.py`) `ValueError: invalid literal for int()` | A number setting isn't a number | Fix or remove that line in `.env` |
| `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte` | `.env` was saved as UTF-16 (for example with `echo ... > .env` in Windows PowerShell 5), not as plain text (UTF-8) | Open `.env` in Notepad, choose Save As, set Encoding to UTF-8, and save |

## Exercise

Add a second tool, `search`, that finds every line containing some text in the project folder. It needs the same three parts as `look`: a function, an entry in `TOOLS`, and an entry in `RUN`. Keep the same safety rules. Then ask "Find every TODO in my project."

Try it yourself first. Our answer, built on `agent.py`, is `agent_search.py`.
