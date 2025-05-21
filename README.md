# canvas-gci

![CI](https://github.com/zk/canvas-gci/actions/workflows/ci.yml/badge.svg)

A tool to clone Canvas course content locally, creating a directory structure based on the course modules.

## Installation

1.  **Clone the repository:**

    ```sh
    git clone https://github.com/zk/canvas-gci.git
    cd canvas-gci
    ```

2.  **Create and activate a virtual environment (recommended):**

    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```sh
    uv sync
    ```

## Usage

1.  **Set environment variables:**
    Create a `.env` file in the project root or set the following environment variables directly:

    - `CANVAS_API_ROOT`: The root URL of your Canvas instance (e.g., `https://canvas.instructure.com/api/v1`).
    - `CANVAS_TOKEN`: Your Canvas API access token.

    Example `.env` file:

    ```env
    CANVAS_API_ROOT="https://your.canvas.instance.com/api/v1"
    CANVAS_TOKEN="your_api_token_here"
    ```

2.  **Run the CLI:**
    ```sh
    uv run canvas-gci --course-id YOUR_COURSE_ID
    ```
    Replace `YOUR_COURSE_ID` with the actual ID of the course you want to clone.
    The tool will create a directory named after the course (or as specified by `--output`) containing subdirectories for each module.

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
