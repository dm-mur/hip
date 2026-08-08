# Health Intelligence Platform (HIP)

An open-source, AI-ready health data engineering platform for ingesting, validating, transforming, and analyzing public health data.

HIP is designed around modern data engineering principles including metadata-driven ingestion, layered data warehousing, infrastructure as code, database versioning, and workflow orchestration.

---

## Vision

To provide a reusable, enterprise-grade platform for integrating health information systems such as DHIS2, EMRs, laboratory systems, and other public health data sources into a unified analytics platform.

---

## Current Status

🚧 Under Active Development

Current milestone:

- Platform Foundation ✅

---

## Technology Stack

- PostgreSQL 17
- Docker
- Flyway
- Python
- Git & GitHub

Planned:

- Apache Airflow
- dbt
- FastAPI
- Great Expectations
- AI-assisted metadata generation

---

## Architecture

```
Source Systems
      │
      ▼
Bronze Layer
      │
      ▼
Silver Layer
      │
      ▼
Gold Layer
      │
      ▼
Analytics & AI
```

---

## Repository Structure

```text
hip/

docker/
database/
docs/
ingestion/
transformations/
analytics/
tests/
```

---

## Getting Started

Coming soon.

---

## Roadmap

- ✅ Platform Foundation
- ⏳ Enterprise Audit Framework
- ⏳ Metadata Repository
- ⏳ DHIS2 Metadata Ingestion
- ⏳ DHIS2 Aggregate Data Ingestion
- ⏳ Silver Transformations
- ⏳ Gold Analytics
- ⏳ Airflow Orchestration
- ⏳ AI Integration

---

## License

MIT License