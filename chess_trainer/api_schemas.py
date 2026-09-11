"""Pydantic response models for the HTTP API (separate from the internal dataclasses
in `weakness.py`/`resources.py` so the wire format can evolve independently)."""

from __future__ import annotations

from pydantic import BaseModel


class ResourceResponse(BaseModel):
    title: str
    url: str
    source: str


class WeakThemeResponse(BaseModel):
    theme_id: str
    display_name: str
    performance: int
    attempts: int
    first_win_rate: float
    resources: list[ResourceResponse]
