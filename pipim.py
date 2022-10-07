#!/usr/bin/env python

import os
import shutil
import sys
import venv
from argparse import ArgumentParser
from pathlib import Path


class ArgumentParser(ArgumentParser):
    def error(self, *args, **kwargs):
        raise Exception


def log(*args):
    print("pipim:", *args)


INSTALL_ALIASES = ["i", "in"]
UNINSTALL_ALIASES = ["u", "un", "remove"]


parser = ArgumentParser()
parser.description = "pipim: pip improved"
parser.epilog = (
    "For any other command, pipim will run pip instead, see python -m pip"
    " --help for more information about pip"
)
parser.add_argument(
    "--user",
    action="store_true",
    help=(
        "Install packages in user site-packages. If pipus is found, it will be"
        " used instead of pip"
    ),
)
parser.add_argument(
    "command",
    choices=[
        "install",
        *INSTALL_ALIASES,
        "uninstall",
        *UNINSTALL_ALIASES,
        "replace-pip",
    ],
    default="install",
    nargs="?",
    help=(
        "install and uninstall will invoke pip in a venv, replace-pip will"
        " create a script in ~/.local/bin/pip that will invoke pipim instead of"
        " pip"
        "\ndefault: install"
    ),
)
parser.add_argument(
    "packages",
    nargs="*",
    help=(
        "Packages to install/uninstall. If none are given, pipim will install"
        " the packages listed in requirements.txt."
    ),
)


def ensure_venv():
    """Creates a venv if it doesn't exist"""

    if not os.path.exists(".venv"):
        log("Creating virtual environment...")
        venv.create(".venv", with_pip=True)


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
        f.write("#!/bin/sh\n\nexec pipim $@\n")
    target.chmod(0o755)
    log("Created", target, ", you may need to refresh your environment")


def main():
    try:
        args = parser.parse_args()
    except Exception:
        if not os.path.exists(".venv"):
            exec("python", "-m", "pip", *sys.argv[1:])
        exec(".venv/bin/pip", *sys.argv[1:])

    if args.command == "replace-pip":
        replace_pip()
        return

    if args.command in INSTALL_ALIASES:
        args.command = "install"
    if args.command in UNINSTALL_ALIASES:
        args.command = "uninstall"

    if args.user:
        if shutil.which("pipus") is not None:
            log("pipus found, using it instead of pip")
            command = "" if args.command == "install" else "-R"
            exec("pipus", command, *args.packages)

        log("pipus not found, using pip instead")
        exec("pip", *sys.argv[1:])

    if len(args.packages) == 0:
        if not os.path.exists("requirements.txt"):
            log("No requirements.txt found, exiting")
            sys.exit(1)

        ensure_venv()
        exec(".venv/bin/pip", "install", "-r", "requirements.txt")

    ensure_venv()
    exec(".venv/bin/pip", *sys.argv[1:])


if __name__ == "__main__":
    main()
