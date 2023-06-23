#!/usr/bin/env python

import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path


def log(*args):
    print("pipim:", *args)


HELP = """\
pipim: pip improved


pipim will create a virtual environment in the current directory if one doesn't
already exist, and run pip inside it, unless the --user flag is passed.


Usage:
    pipim [command] [arguments...]


The default command is install if none is specified.


Commands:
    install, i, in:        Install packages in a virtual environment
                           If no packages are provided, installs from
                           requirements.txt instead

    uninstall, un, remove: Uninstall packages from a virtual environment

    run, r:                Run a command in a virtual environment
                           Everything after the run command is passed to the
                           command

    update, up:            Read dependencies from a file called
                           requirements.update.txt or anything passed as an
                           argument, update them to the latest version, then
                           write the frozen requirements to requirements.txt

    replace-pip:           Writes a script to ~/.local/bin/pip that runs pipim
                           instead of pip

    help                   Show this help message

Flags:
    -h, --help:            Show this help message
    -u, --user:            Work with the user's packages instead of a virtual
                           environment. pipus will be used if available.


Any other flags or arguments will be passed down to pip.
"""


def ensure_venv(path=".venv"):
    """Creates a venv if it doesn't exist"""

    if not os.path.exists(path):
        log("Creating virtual environment...")
        venv.create(path, with_pip=True)


def run(*args):
    """Run a command and return the output"""

    log("Running", *args)
    process = subprocess.run(args, stdout=subprocess.PIPE)
    if process.returncode != 0:
        error("Command failed:", *args)
    return process.stdout.decode("utf-8")


def exec(*args):
    """Replaces the current process with the given command"""

    log("Running", *args)
    os.execvp(args[0], args)


def replace_pip():
    """Replaces the pip executable with a script that invokes pipim instead"""

    target = Path("~/.local/bin/pip").expanduser()
    if target.exists():
        log(target, "already exists")
        sys.exit(1)
    with target.open("w") as f:
        f.write('#!/bin/sh\n\nexec pipim "$@"\n')
    target.chmod(0o755)
    log("Created", target, "you may need to refresh your environment")


def argument_parser(d: dict, stops=[]) -> dict:
    """Parses arguments into a dictionary

    Dictionary keys are the names of the arguments, and the values are the
    names of the flags or commands that should be associated with them.
    Values can be a string or a list of strings.

    Returns a dictionary with the same keys as the input, and values that are
    True if the argument was passed, and False otherwise.

    Example:
        argument_parser({"help": ["-h", "--help"]})
        # If the script is called with -h or --help, returns {"help": True}
        # Otherwise, returns {"help": False}
    """

    rules = {}
    result = {}
    arguments = []
    for name, match in d.items():
        result[name] = False
        if not isinstance(match, list):
            match = [match]
        for m in match:
            rules[m] = name
    for i, arg in enumerate(sys.argv[1:]):
        if arg in rules:
            name = rules[arg]
            result[name] = True
            if name in stops:
                arguments = sys.argv[i + 2 :]
                break
        else:
            arguments.append(arg)
    result["arguments"] = arguments
    return result


def error(*args, help=False):
    print("pipim:", *args, file=sys.stderr)
    if help:
        print(HELP, file=sys.stderr)
    sys.exit(1)


def main():
    args = argument_parser(
        {
            "help": ["help", "-h", "--help"],
            "user": ["-u", "--user"],
            "install": ["install", "i", "in"],
            "update": ["update", "up"],
            "uninstall": ["uninstall", "u", "un", "remove"],
            "run": ["run", "r"],
            "replace_pip": "replace-pip",
        },
        stops=["run", "update"],
    )

    if args["help"]:
        print(HELP)
        return

    if args["replace_pip"]:
        replace_pip()
        return

    if args["user"]:
        if shutil.which("pipus") is not None:
            log("pipus found, using it instead of pip")
            command = "-R" if args["uninstall"] else ""
            exec("pipus", command, *args["arguments"])
        if args["install"]:
            command = "install"
        elif args["uninstall"]:
            command = "uninstall"
        else:
            command = ""
        log("pipus not found, using pip instead")
        exec("python", "-m", "pip", command, *args["arguments"])

    if args["run"]:
        ensure_venv()
        command = args["arguments"][0] if args["arguments"] else "python"
        exec(f".venv/bin/{command}", *args["arguments"][1:])

    if args["uninstall"]:
        exec("python", "-m", "pip", "uninstall", *args["arguments"])

    if args["update"]:
        if len(args["arguments"]) > 1:
            error(
                "Update command takes either a requirements.txt-like file as"
                " parameter or no parameters at all",
                help=True,
            )
        file = (
            args["arguments"][0]
            if args["arguments"]
            else "requirements.update.txt"
        )
        if not os.path.exists(file):
            error(f"File {file} not found")
        log("Working in temporary .update virtual environment...")
        ensure_venv(".update")
        run(".update/bin/pip", "install", "-U", "-r", file)
        requirements = run(".update/bin/pip", "freeze")
        with open("requirements.txt", "w") as f:
            f.write(requirements)
        log("Updated requirements.txt")
        shutil.rmtree(".update")
        log("Removed .update")
        sys.exit(0)

    if len(args["arguments"]) == 0:
        args["install"] = True

    if args["install"]:
        if len(args["arguments"]) == 0:
            if not os.path.exists("requirements.txt"):
                log("No requirements.txt found, exiting")
                sys.exit(1)
            ensure_venv()
            exec(".venv/bin/pip", "install", "-r", "requirements.txt")
        ensure_venv()
        exec(".venv/bin/pip", "install", *args["arguments"])

    ensure_venv()
    exec(".venv/bin/pip", *args["arguments"])


if __name__ == "__main__":
    main()
