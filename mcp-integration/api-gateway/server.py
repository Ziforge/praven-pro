#!/usr/bin/env python3
"""
Praven Pro API Gateway
Simple HTTP gateway for Raven MCP service
"""

from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI(title="Praven Pro API Gateway")


class RavenExportRequest(BaseModel):
    detections_csv: str
    output_path: str
    audio_file: str
    audio_path: str
    default_low_freq: float = 500.0
    default_high_freq: float = 8000.0
    channel: int = 1


class RavenBatchExportRequest(BaseModel):
    detections_dir: str
    output_dir: str
    audio_dir: str
    file_pattern: str = "*_detections.csv"
    default_low_freq: float = 500.0
    default_high_freq: float = 8000.0


@app.get("/health")
def health():
    return {"ok": True, "service": "praven-api-gateway"}


@app.post("/raven/export")
def raven_export(req: RavenExportRequest):
    """Export single detection CSV to Raven selection table"""
    url = "http://praven-raven-mcp:7085/run/export_to_raven"
    response = requests.post(url, json=req.dict(), timeout=300)
    response.raise_for_status()
    return response.json()


@app.post("/raven/export_batch")
def raven_batch_export(req: RavenBatchExportRequest):
    """Batch export multiple detection CSVs to Raven selection tables"""
    url = "http://praven-raven-mcp:7085/run/batch_export_to_raven"
    response = requests.post(url, json=req.dict(), timeout=600)
    response.raise_for_status()
    return response.json()


@app.post("/raven/import")
def raven_import(raven_table_path: str, output_csv: str):
    """Import Raven selection table to CSV"""
    url = "http://praven-raven-mcp:7085/run/import_from_raven"
    payload = {"raven_table_path": raven_table_path, "output_csv": output_csv}
    response = requests.post(url, json=payload, timeout=300)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
