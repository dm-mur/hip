# ADR-002: Enterprise Audit Framework

## Status

Accepted

## Date

2026-08-07

---

## Context

HIP is designed as a reusable enterprise health data platform capable of ingesting data from multiple source systems including DHIS2, EMRs, laboratory systems, and future APIs.

Every execution of the platform should be observable, measurable, and auditable.

The platform therefore requires a standardized audit framework capable of tracking pipeline execution across all components.

---

## Decision

HIP will implement a hierarchical audit framework consisting of:

- audit.etl_batch
- audit.pipeline_run
- audit.pipeline_step
- audit.error_log

The framework will:

- uniquely identify every execution using UUIDs
- record execution status
- record execution duration
- capture operational metrics
- support monitoring dashboards
- support troubleshooting
- support future workflow orchestration

Applied Flyway migrations will never be modified.

Database evolution will always occur through new migration files.

---

## Consequences

Benefits include:

- Complete execution traceability
- Easier operational support
- Reproducible schema evolution
- Platform observability
- Enterprise-grade governance