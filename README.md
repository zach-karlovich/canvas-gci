# canvas-gci

## Quick Start

1. Install dependencies:
   ```sh
   uv sync
   ```
2. Run the CLI:
   ```sh
   uv run canvas-gci --course-id 123456
   ```

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
