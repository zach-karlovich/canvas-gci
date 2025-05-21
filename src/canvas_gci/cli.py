import logging
from pathlib import Path
from typing import Optional

import click
import typer

from .api import (
    CanvasAPI,
    CanvasAPIError,
    CanvasAPINotFound,
    CanvasAPIUnauthorized,
)
from .fs import ensure_module_dirs
from .logging_conf import setup_logging

app = typer.Typer()


def version_callback(value: bool) -> None:
    if value:
        import importlib.metadata

        typer.echo(importlib.metadata.version("canvas-gci"))
        raise typer.Exit()


@app.command()
def main(
    course_id: int = typer.Option(
        ..., "--course-id", help="Canvas course ID", show_default=False
    ),
    api_root: str = typer.Option(
        "https://canvas.instructure.com/api/v1",
        "--api-root",
        help="Canvas API root URL",
    ),
    output: Path = typer.Option(
        Path("./modules"), "--output", help="Output directory for modules"
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose logging"),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    setup_logging(verbose)
    try:
        api = CanvasAPI(api_root=api_root)
        modules = api.get_modules(course_id)
        if not modules:
            logging.info("No modules found for this course.")
            typer.echo("No modules found for this course.")
            raise typer.Exit(0)
        created_paths = ensure_module_dirs(output, modules)
        if not created_paths:
            logging.info("No changes. All module directories already exist.")
            typer.echo("No changes.")
            raise typer.Exit(0)
        typer.echo(f"Created {len(created_paths)} module directories in {output}.")
    except CanvasAPINotFound as e:
        logging.error(str(e))
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(2)
    except CanvasAPIUnauthorized as e:
        logging.error(str(e))
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(3)
    except CanvasAPIError as e:
        logging.error(str(e))
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except click.exceptions.Exit:
        raise
    except Exception as e:
        logging.exception("Unexpected error")
        typer.echo(f"Unexpected error: {str(e)}", err=True)
        raise typer.Exit(99)


if __name__ == "__main__":
    app()
