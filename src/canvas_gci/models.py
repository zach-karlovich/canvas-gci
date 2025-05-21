from pydantic import BaseModel

__all__ = ["CanvasModule"]


class CanvasModule(BaseModel):
    """
    Data model for a Canvas Module, as returned by the Canvas API.
    """

    id: int
    name: str
    position: int
    # Add other fields as needed
