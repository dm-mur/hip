# ADR-001: Platform Principles

## Status

Accepted

## Context

The Health Intelligence Platform (HIP) is intended to be an enterprise-grade, open-source health analytics platform built using modern Data Engineering, Analytics Engineering, DevOps, and AI practices.

## Decisions

- Docker-first development.
- PostgreSQL as the primary analytical database.
- Bronze, Silver, Gold architecture.
- Metadata-driven ETL.
- Database changes managed through versioned migrations.
- Public repository uses aggregate DHIS2 data only.
- Clinical demonstrations use synthetic or de-identified data.

## Consequences

The platform remains portable, reproducible, scalable, and suitable as a professional portfolio project.