# pipim: PIP IMproved

Drop-in replacement for pip with behavior that imitates other popular languages
packages managers.

## Installing

```
pip install --user pipim
```

Then, if you wish for pipim to be invoked when you simply type `pip`, you can
use `pipim replace-pip` to create a script in `~/.local/bin/pip` that will run
pipim.

## Rationale

When you work on Python projects, you often find yourself creating virtual
environments, and having to manually activate them or install dependencies in
them.

This is not something you typically do with other languages, where the package
manager is smart enough to know if you meant to install packages at the user
level or at the project level.

This is more or less in line with the Zen of Python: explicit is better than
implicit. However I grew tired of having this behavior available everywhere
except with Python, so I decided to write a simple wrapper around pip that will
use virtual environments by default, unless `--user` is passed.

## Features

By default, pipim will be installed as `pipim`, however, you can use it as a
drop-in replacement of `pip`, and the following examples assume you did.

### Automatic use of virtual environments

The following commands will automatically create a virtual environment called `.venv/` if one does not exist already, and then the actual commands inside of it:

```
pip install package1 [package2...]
```

```
pip uninstall package1 [package2...]
```

If you wish to work outside of a virtual environment, you can use the `--user`
flag. This will try to use [pipus](https://github.com/Tina-otoge/pipus) if it is
found in your PATH, and will resort to regular `pip` otherwise.

### Install packages from requirements.txt

If you do not specify any package, this will run `pip install -r requirements.txt`
in the virtual environment. As with other install commands, this will
create the venv first if it does not exist already.

Simply run:

```bash
pip
# or
pip install
```

### Easily installs itself as a replacement

You can use `pipim replace-pip` once to create a simple script in
`~/.local/bin/pip` that will invoke pipim instead of pip. This will allow you to
forget about pipim and just run `pip` like you always did before, except that
now it comes with extra perks ✨✨.

### Run a command inside the virtual environment

```
pip run <command> [arguments...]
```

The first argument will be invoked from `.venv/bin/`, everything that follows is
passed to it. For example:

```
pip run flask --help
```

### Always fallback to regular pip

Every unmatched flags are passed down to pip, any unrecognized command will run
pip too.

## Contributing

Noticed a bug? Want to request a feature? Simply [open a new Issue](https://github.com/Tina-otoge/pip-improved/issues).
