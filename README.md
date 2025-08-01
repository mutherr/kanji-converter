# Installation

Install the `uv` package manager, then run `uv sync`.

## A note on installation with Homebrew python

When installing via `uv`, you may need to set the paths manually if using Homebrew python.
This will often manifest as the program reporting a missing `Python.h`file while building.

```
export CPPFLAGS="-I/home/linuxbrew/.linuxbrew/include/python3.12" (adjust for your version of python, 3.12 is the latest stable at time of writing.)
export LDFLAGS="-L/home/linuxbrew/.linuxbrew/lib"
uv sync
```

Installing based on system python should be fine, as the headers should already be in your path.
