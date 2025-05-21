# canvas-gci

![CI](https://github.com/zk/canvas-gci/actions/workflows/ci.yml/badge.svg)

A tool to clone Canvas course content locally, creating a directory structure based on the course modules.

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/zk/canvas-gci.git
   cd canvas-gci
   ```

2. **Create and activate a virtual environment (recommended):**

   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use .venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```sh
   uv sync
   ```

## Configuration

To use `canvas-gci`, you need to provide your Canvas API token and the API root URL for your Canvas instance.

There are two primary ways to configure these:

### 1. Using a `.env` file (Recommended for project-based use)

Create a file named `.env` in the root directory of this project (`canvas-gci/.env`). Add the following lines, replacing the placeholder values with your actual information:

```env
CANVAS_API_ROOT="https://your.canvas.instance.com/api/v1"
CANVAS_TOKEN="your_api_token_here"
```

*   `CANVAS_API_ROOT`: The root URL of your Canvas instance (e.g., `https://canvas.its.virginia.edu/api/v1` or `https://canvas.instructure.com/api/v1`).
*   `CANVAS_TOKEN`: Your Canvas API access token. You can generate this from your Canvas profile settings.

When you run `uv run canvas-gci ...` from any directory, the application will automatically load these variables from the `.env` file located in the project's root directory.

*(For running tests, you might also need `PYTEST_VALID_COURSE_ID` as noted in older versions of this README; see `pyproject.toml` or test configurations for details if you intend to record new test cassettes.)*

### 2. Using System Environment Variables (For global access)

Alternatively, you can set `CANVAS_TOKEN` and `CANVAS_API_ROOT` as environment variables directly in your operating system. This makes them available globally, regardless of your current working directory or whether a `.env` file is present.

**On Linux/macOS (e.g., in your `.bashrc` or `.zshrc`):**
```sh
export CANVAS_TOKEN="your_api_token_here"
export CANVAS_API_ROOT="https://your.canvas.instance.com/api/v1"
```
Remember to source your shell configuration file (e.g., `source ~/.zshrc`) or open a new terminal for these changes to take effect.

**On Windows:**
Search for "environment variables" in the Start Menu to find the system settings panel where you can add or edit user or system environment variables.

If `CANVAS_API_ROOT` is not set either via a `.env` file or as a system environment variable, the tool will default to `https://canvas.instructure.com/api/v1`.

## Usage

Once configured, you can run the CLI from any directory using `uv`:

```sh
uv run canvas-gci --course-id YOUR_COURSE_ID
```

Replace `YOUR_COURSE_ID` with the actual ID of the course you want to process.

The tool will create a directory named `modules/` in your current working directory, containing subdirectories for each module from the specified course.

**Example:**
```sh
# Ensure your .env file is in the project root, or system env vars are set.
cd ~/MyCourses/STAT4000/

# This will create ./modules/ inside ~/MyCourses/STAT4000/
uv run canvas-gci --course-id 12345
```

See `uv run canvas-gci --help` for all command-line options.

## Slug Rules Example

- `Introduction - Linear Regression` → `introduction-linear-regression`
- `Week 03: k-NN & SVM` → `week-03-k-n-n-svm`

See `--help` for all options.

## Running Tests

Install test dependencies and run pytest:

```sh
uv pip install -r pyproject.toml --extra test
pytest
```
