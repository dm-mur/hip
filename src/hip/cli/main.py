"""
Command-line interface for HIP.

The CLI translates operator input into pipeline configuration
and delegates execution to PipelineRunner.
"""

import argparse

from dotenv import load_dotenv

from hip.config.database import DatabaseSettings
from hip.config.settings import DHIS2Settings
from hip.config.source import DHIS2SourceConfig
from hip.pipelines.config import PipelineConfig
from hip.pipelines.request import PipelineRequest
from hip.pipelines.runner import PipelineRunner


def build_parser() -> argparse.ArgumentParser:
    """Build the HIP command-line parser."""

    parser = argparse.ArgumentParser(
        prog="hip",
        description="Health Intelligence Platform",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Run a HIP data pipeline",
    )

    run_parser.add_argument(
        "pipeline_type",
        help="Registered pipeline type, for example: dhis2",
    )

    run_parser.add_argument(
        "--source-instance",
        required=True,
        help="Logical name identifying the source system instance",
    )

    run_parser.add_argument(
        "--endpoint",
        required=True,
        help="Source API endpoint to execute",
    )

    run_parser.add_argument(
        "--environment",
        required=True,
        choices=["DEV", "TEST", "UAT", "PROD"],
        help="Pipeline execution environment",
    )

    run_parser.add_argument(
        "--initiated-by",
        required=True,
        help="User or process initiating the pipeline",
    )

    run_parser.add_argument(
        "--batch-name",
        required=True,
        help="Human-readable batch name",
    )

    run_parser.add_argument(
        "--period",
        help="Reporting period passed to the source request",
    )

    run_parser.add_argument(
        "--param",
        action="append",
        help="Request parameter in KEY=VALUE format; may be repeated",
    )

    return parser


def parse_request_params(
    period: str | None,
    parameters: list[str] | None,
) -> dict[str, str] | None:
    """Build request parameters from CLI arguments."""

    params = {}

    if period:
        params["period"] = period

    for parameter in parameters or []:
        if "=" not in parameter:
            raise ValueError(
                f"Invalid request parameter: {parameter}. "
                "Expected KEY=VALUE."
            )

        key, value = parameter.split("=", 1)

        if not key.strip():
            raise ValueError(
                f"Invalid request parameter: {parameter}. "
                "Expected KEY=VALUE."
            )

        params[key] = value

    return params or None


def run_pipeline(args: argparse.Namespace) -> int:
    """Execute a pipeline from parsed CLI arguments."""

    if args.pipeline_type != "dhis2":
        raise ValueError(
            f"Unsupported CLI pipeline type: {args.pipeline_type}"
        )

    source_config = DHIS2SourceConfig(
        source_instance=args.source_instance,
        settings=DHIS2Settings.from_environment(),
    )

    database_settings = DatabaseSettings.from_environment()

    pipeline_config = PipelineConfig(
        environment=args.environment,
        initiated_by=args.initiated_by,
        batch_name=args.batch_name,
    )


    params = parse_request_params(
        period=args.period,
        parameters=args.param,
    )

    request = PipelineRequest(
        endpoint=args.endpoint,
        params=params,
    )

    return PipelineRunner.run(
        pipeline_type=args.pipeline_type,
        source_config=source_config,
        database_settings=database_settings,
        pipeline_config=pipeline_config,
        request=request,
    )


def main() -> int:
    """Run the HIP command-line application."""

    load_dotenv()

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        try:
            loaded_count = run_pipeline(args)
        except ValueError as exc:
            parser.error(str(exc))

        print(f"Loaded {loaded_count} records")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
