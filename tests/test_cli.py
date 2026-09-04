import argparse
import sys

from hip.cli.main import build_parser, main, run_pipeline


def test_build_parser_parses_run_command():
    parser = build_parser()

    args = parser.parse_args(
        [
            "run",
            "dhis2",
            "--source-instance",
            "test_dhis2",
            "--endpoint",
            "/api/dataValueSets",
            "--environment",
            "TEST",
            "--initiated-by",
            "pytest",
            "--batch-name",
            "CLI Test",
            "--period",
            "202608",
            "--param",
            "dataSet=abc123",
            "--param",
            "orgUnit=xyz789",
        ]
    )

    assert args.command == "run"
    assert args.pipeline_type == "dhis2"
    assert args.source_instance == "test_dhis2"
    assert args.endpoint == "/api/dataValueSets"
    assert args.environment == "TEST"
    assert args.initiated_by == "pytest"
    assert args.batch_name == "CLI Test"
    assert args.period == "202608"
    assert args.param == [
        "dataSet=abc123",
        "orgUnit=xyz789",
    ]


def test_run_pipeline_delegates_to_pipeline_runner(monkeypatch):
    args = argparse.Namespace(
        command="run",
        pipeline_type="dhis2",
        source_instance="test_dhis2",
        endpoint="/api/dataValueSets",
        environment="TEST",
        initiated_by="pytest",
        batch_name="CLI Test",
        period="202608",
        param=[
            "dataSet=abc123",
            "orgUnit=xyz789",
        ],
    )

    monkeypatch.setenv(
        "DHIS2_BASE_URL",
        "https://example.org",
    )
    monkeypatch.setenv(
        "DHIS2_USERNAME",
        "test-user",
    )
    monkeypatch.setenv(
        "DHIS2_PASSWORD",
        "test-password",
    )
    monkeypatch.setenv(
        "POSTGRES_PASSWORD",
        "test-password",
    )

    captured = {}

    def fake_run(
        *,
        pipeline_type,
        source_config,
        database_settings,
        pipeline_config,
        request,
    ):
        captured["pipeline_type"] = pipeline_type
        captured["source_config"] = source_config
        captured["database_settings"] = database_settings
        captured["pipeline_config"] = pipeline_config
        captured["request"] = request
        return 7

    monkeypatch.setattr(
        "hip.cli.main.PipelineRunner.run",
        fake_run,
    )

    result = run_pipeline(args)

    assert result == 7

    assert captured["pipeline_type"] == "dhis2"

    assert captured["source_config"].source_instance == "test_dhis2"
    assert captured["source_config"].settings.base_url == "https://example.org"

    assert captured["pipeline_config"].environment == "TEST"
    assert captured["pipeline_config"].initiated_by == "pytest"
    assert captured["pipeline_config"].batch_name == "CLI Test"

    assert captured["request"].endpoint == "/api/dataValueSets"
    assert captured["request"].params == {
        "period": "202608",
        "dataSet": "abc123",
        "orgUnit": "xyz789",
    }


def test_run_pipeline_rejects_unsupported_pipeline_type():
    args = argparse.Namespace(
        command="run",
        pipeline_type="csv",
        source_instance="test_source",
        endpoint="/data",
        environment="TEST",
        initiated_by="pytest",
        batch_name="CLI Test",
        period=None,
        param=None,
    )

    try:
        run_pipeline(args)
    except ValueError as exc:
        assert str(exc) == "Unsupported CLI pipeline type: csv"
    else:
        raise AssertionError("Expected ValueError")


def test_run_pipeline_rejects_invalid_param(monkeypatch):
    args = argparse.Namespace(
        command="run",
        pipeline_type="dhis2",
        source_instance="test_dhis2",
        endpoint="/api/dataValueSets",
        environment="TEST",
        initiated_by="pytest",
        batch_name="CLI Test",
        period=None,
        param=["invalid-param"],
    )

    monkeypatch.setenv("DHIS2_BASE_URL", "https://example.org")
    monkeypatch.setenv("DHIS2_USERNAME", "test-user")
    monkeypatch.setenv("DHIS2_PASSWORD", "test-password")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test-password")

    try:
        run_pipeline(args)
    except ValueError as exc:
        assert str(exc) == (
            "Invalid request parameter: invalid-param. "
            "Expected KEY=VALUE."
        )
    else:
        raise AssertionError("Expected ValueError")


def test_main_reports_configuration_error_without_traceback(
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "hip",
            "run",
            "dhis2",
            "--source-instance",
            "test_dhis2",
            "--endpoint",
            "/api/dataValueSets",
            "--environment",
            "TEST",
            "--initiated-by",
            "pytest",
            "--batch-name",
            "CLI Test",
        ],
    )

    monkeypatch.delenv("DHIS2_BASE_URL", raising=False)
    monkeypatch.delenv("DHIS2_USERNAME", raising=False)
    monkeypatch.delenv("DHIS2_PASSWORD", raising=False)

    monkeypatch.setattr(
        "hip.cli.main.load_dotenv",
        lambda: None,
    )

    try:
        main()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("Expected SystemExit")

    captured = capsys.readouterr()

    assert "Missing required DHIS2 configuration" in captured.err
    assert "Traceback" not in captured.err