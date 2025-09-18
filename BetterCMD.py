import os
import json
import subprocess

# Files for history and aliases
HISTORY_FILE = "cmdhistory.txt"
ALIASES_FILE = "aliases.json"

# Load command history
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        history = f.read().splitlines()
else:
    history = []

def save_history(command):
    history.append(command)
    with open(HISTORY_FILE, "w") as f:
        f.write("\n".join(history))

# Load aliases
aliases = {}
if os.path.exists(ALIASES_FILE):
    with open(ALIASES_FILE, "r") as f:
        aliases = json.load(f)

def save_aliases():
    with open(ALIASES_FILE, "w") as f:
        json.dump(aliases, f, indent=4)

# Colored text
def color_text(text, r, g, b):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

# Bash-like commands
def ls(args):
    path = args[0] if args else "."
    try:
        for item in os.listdir(path):
            print(item)
    except Exception as e:
        print(color_text(f"Error: {e}", 255, 0, 0))

def cd(args):
    path = args[0] if args else os.path.expanduser("~")
    try:
        os.chdir(path)
    except Exception as e:
        print(color_text(f"Error: {e}", 255, 0, 0))

def pwd(args):
    print(os.getcwd())

def echo(args):
    print(" ".join(args))

def alias_command(args):
    if not args:
        for k, v in aliases.items():
            print(f"{k} = {v}")
        return
    # Set new alias
    if "=" in args[0]:
        key, val = args[0].split("=", 1)
        aliases[key.strip()] = val.strip()
        save_aliases()
        print(f"Alias set: {key.strip()} = {val.strip()}")
    else:
        key = args[0]
        if key in aliases:
            print(f"{key} = {aliases[key]}")
        else:
            print(f"Alias not found: {key}")

# Command dispatcher
commands = {
    "ls": ls,
    "cd": cd,
    "pwd": pwd,
    "echo": echo,
    "alias": alias_command,
    "h": lambda args: print("\n".join(history)),
    "cls": lambda args: os.system("cls")
}

# Parse user input and check aliases
def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return None, []
    cmd = parts[0]
    args = parts[1:]
    # Apply alias if exists
    if cmd in aliases:
        aliased = aliases[cmd].split()
        cmd = aliased[0]
        args = aliased[1:] + args
    return cmd, args

# Parse color text command
def parse_color_command(user_input):
    if user_input.startswith("color text"):
        try:
            _, _, r, g, b, *text = user_input.split()
            r, g, b = int(r), int(g), int(b)
            print(color_text(" ".join(text), r, g, b))
        except Exception as e:
            print(color_text(f"Error: {e}", 255, 0, 0))
        return True
    return False

# Main loop
def main():
    while True:
        try:
            user_input = input(f"{os.getcwd()} $ ")
            if not user_input.strip():
                continue
            save_history(user_input)
            if user_input in ("exit", "quit"):
                break
            if parse_color_command(user_input):
                continue
            cmd, args = parse_input(user_input)
            if cmd in commands:
                commands[cmd](args)
            else:
                try:
                    # Run as system command (supports executables with full paths and spaces)
                    subprocess.run([cmd] + args, check=False, shell=True)
                except FileNotFoundError:
                    # Try wrapping in quotes in case of spaces
                    try:
                        subprocess.run(" ".join(['"' + cmd + '"'] + args), check=False, shell=True)
                    except FileNotFoundError:
                        print(color_text(f"Command not found: {cmd}", 255, 0, 0))
        except KeyboardInterrupt:
            print()
            continue
        except Exception as e:
            print(color_text(f"Error: {e}", 255, 0, 0))

if __name__ == "__main__":
    main()
