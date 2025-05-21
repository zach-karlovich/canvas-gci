# CLI Usage Guide

This guide provides a detailed reference for using the `canvas-gci` command-line interface.

## CLI Reference

The following is the output of `canvas-gci --help`:

```text
 Usage: canvas-gci [OPTIONS]

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --course-id                 INTEGER  Canvas course ID [required]                                                                       │
│    --api-root                  TEXT     Canvas API root URL [default: https://canvas.instructure.com/api/v1]                              │
│    --output                    PATH     Output directory for modules [default: modules]                                                   │
│    --verbose                            Enable verbose logging                                                                            │
│    --version                            Show version and exit                                                                             │
│    --install-completion                 Install completion for the current shell.                                                         │
│    --show-completion                    Show completion for the current shell, to copy it or customize the installation.                  │
│    --help                               Show this message and exit.                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Options Explained

- `--course-id INTEGER`: **(Required)** The numerical ID of the Canvas course you wish to clone. You can usually find this in the URL when viewing the course in your browser.
- `--api-root TEXT`: The base URL for the Canvas API. This defaults to `https://canvas.instructure.com/api/v1`, which is standard for most Canvas instances. You might need to change this if your institution has a custom Canvas domain.
- `--output PATH`: The directory where the course content (module folders) will be saved. This defaults to a directory named `modules` in the current working directory. If the specified directory doesn't exist, it will be created.
- `--verbose`: Enables more detailed logging output to the console. This can be helpful for troubleshooting.
- `--version`: Displays the current version of `canvas-gci` and exits.
- `--install-completion`: Installs shell completion for `canvas-gci` for your current shell (e.g., Bash, Zsh, Fish). This allows you to use the Tab key to autocomplete commands and options.
- `--show-completion`: Shows the shell completion script. This can be useful if you want to manually install or customize the completion.
- `--help`: Displays the help message and exits.

## Examples

### Basic Usage

Clone a course with ID `12345` into the default `modules/` directory:

```sh
canvas-gci --course-id 12345
```

_(Assumes `CANVAS_API_ROOT` and `CANVAS_TOKEN` are set in your environment or `.env` file, and `uv run` or your virtual environment is active)_

### Specify Output Directory

Clone course `67890` into a directory named `my_course_content`:

```sh
canvas-gci --course-id 67890 --output my_course_content
```

### Verbose Logging

Clone a course and get detailed log output:

```sh
canvas-gci --course-id 12345 --verbose
```

### Using a Custom Canvas API Root

If your institution uses `https://canvas.myuniversity.edu`:

```sh
canvas-gci --course-id 12345 --api-root https://canvas.myuniversity.edu/api/v1
```

_(More examples can be added here, e.g., demonstrating slugification, what happens if a module directory already exists, etc.)_
