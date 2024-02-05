from pydantic import BaseModel


def compare_models(a: BaseModel, b: BaseModel):
    """Compare models as dicts for better diffs."""
    assert a.model_dump() == b.model_dump()
