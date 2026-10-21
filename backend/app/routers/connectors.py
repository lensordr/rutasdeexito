"""Connector status + configuration endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..connector_config import SCHEMAS, connector_config
from ..connectors.registry import registry

router = APIRouter(prefix="/api/connectors", tags=["connectors"])


class SaveValues(BaseModel):
    values: dict[str, str]


@router.get("")
def list_connectors() -> list[dict]:
    """Status for every connector, including whether it is configured."""
    out = []
    for key in SCHEMAS:
        c = registry.get(key)
        status = c.health_check()
        out.append({"key": key, "label": c.label, **status.to_dict()})
    return out


@router.get("/{connector_key}")
def get_connector(connector_key: str) -> dict:
    """Schema (field definitions) + current masked values for one connector."""
    if connector_key not in SCHEMAS:
        raise HTTPException(404, "Unknown connector")
    schema = connector_config.schema_dict(connector_key)
    values = connector_config.masked_values(connector_key)
    status = registry.get(connector_key).health_check()
    return {"schema": schema, "values": values, "status": status.to_dict()}


@router.put("/{connector_key}")
def save_connector(connector_key: str, body: SaveValues) -> dict:
    """Persist values to the gitignored local config file."""
    if connector_key not in SCHEMAS:
        raise HTTPException(404, "Unknown connector")
    connector_config.save_values(connector_key, body.values)
    values = connector_config.masked_values(connector_key)
    status = registry.get(connector_key).health_check()
    return {"saved": True, "values": values, "status": status.to_dict()}


@router.post("/{connector_key}/test")
def test_connector(connector_key: str) -> dict:
    """Run the connector's connection test using saved config."""
    if connector_key not in SCHEMAS:
        raise HTTPException(404, "Unknown connector")
    result = registry.get(connector_key).test_connection()
    return result.to_dict()
