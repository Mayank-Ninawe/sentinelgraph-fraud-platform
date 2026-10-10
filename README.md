# SentinelGraph Fraud Platform

SentinelGraph is a real-time, explainable financial fraud detection platform.

It will:

- Process transaction events.
- Create leakage-safe behavioral features.
- Score fraud risk with machine learning.
- Detect suspicious account/device/IP relationships.
- Provide investigation evidence to analysts.
- Track analyst feedback.
- Monitor data and model drift.

## Current Phase

Phase 1: Project setup and verification.

## Technology Plan

- Python
- XGBoost
- Feast
- Kafka
- FastAPI
- PostgreSQL
- NetworkX and PyTorch Geometric
- MLflow
- Evidently
- Streamlit
- Docker
- Kubernetes

## Data Policy

The full dataset will not be committed to GitHub.

Synthetic identity fields such as device, IP, or location will be clearly documented
if they are created for graph demonstration.

## Run Verification

```bash
pip install -r requirements.txt
pytest
ruff check .
```