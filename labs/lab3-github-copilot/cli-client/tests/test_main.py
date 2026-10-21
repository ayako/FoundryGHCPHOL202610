from collections.abc import Iterator
from types import SimpleNamespace
from unittest.mock import call, patch

import pytest
from azure.core.exceptions import ClientAuthenticationError
from openai import omit

import main as cli


@pytest.fixture(autouse=True)
def isolated_cli(monkeypatch: pytest.MonkeyPatch) -> Iterator[SimpleNamespace]:
    monkeypatch.delenv("FOUNDRY_PROJECT_ENDPOINT", raising=False)
    monkeypatch.delenv("FOUNDRY_AGENT_NAME", raising=False)
    with (
        patch.object(cli, "load_dotenv", return_value=False) as load_dotenv,
        patch.object(cli, "DefaultAzureCredential") as credential,
        patch.object(cli, "AIProjectClient") as project,
    ):
        client = project.return_value.__enter__.return_value.get_openai_client.return_value.__enter__.return_value
        yield SimpleNamespace(
            load_dotenv=load_dotenv,
            credential=credential,
            project=project,
            client=client,
        )


@pytest.fixture
def configured_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "FOUNDRY_PROJECT_ENDPOINT",
        "https://example.services.ai.azure.com/api/projects/test-project",
    )
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "ReceptionAgent")


@pytest.mark.parametrize(
    ("endpoint", "agent_name", "missing"),
    [
        (None, None, ("FOUNDRY_PROJECT_ENDPOINT", "FOUNDRY_AGENT_NAME")),
        (None, "ReceptionAgent", ("FOUNDRY_PROJECT_ENDPOINT",)),
        ("https://example.test/api/projects/test", None, ("FOUNDRY_AGENT_NAME",)),
        ("  ", "\t", ("FOUNDRY_PROJECT_ENDPOINT", "FOUNDRY_AGENT_NAME")),
    ],
)
def test_missing_environment_reports_clear_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    isolated_cli: SimpleNamespace,
    endpoint: str | None,
    agent_name: str | None,
    missing: tuple[str, ...],
) -> None:
    if endpoint is not None:
        monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", endpoint)
    if agent_name is not None:
        monkeypatch.setenv("FOUNDRY_AGENT_NAME", agent_name)

    assert cli.main() == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "設定エラー" in captured.err
    assert "設定してください" in captured.err
    assert ".env.example と README.md" in captured.err
    for name in missing:
        assert name in captured.err
    isolated_cli.credential.assert_not_called()
    isolated_cli.project.assert_not_called()
    isolated_cli.client.responses.create.assert_not_called()


@pytest.mark.usefixtures("configured_env")
def test_conversation_sends_agent_name_and_previous_response_id(
    isolated_cli: SimpleNamespace,
    capsys: pytest.CaptureFixture[str],
) -> None:
    isolated_cli.client.responses.create.side_effect = [
        SimpleNamespace(status="completed", id="resp_first", output_text="こんにちは。"),
        SimpleNamespace(status="completed", id="resp_second", output_text="ご案内します。"),
    ]
    with patch("builtins.input", side_effect=["こんにちは", "予約したい", "exit"]):
        assert cli.main() == 0

    agent_reference = {
        "agent_reference": {"name": "ReceptionAgent", "type": "agent_reference"}
    }
    assert isolated_cli.client.responses.create.call_args_list == [
        call(input="こんにちは", previous_response_id=omit, extra_body=agent_reference),
        call(
            input="予約したい",
            previous_response_id="resp_first",
            extra_body=agent_reference,
        ),
    ]
    captured = capsys.readouterr()
    assert "ReceptionAgent> こんにちは。" in captured.out
    assert "ReceptionAgent> ご案内します。" in captured.out
    assert captured.err == ""


@pytest.mark.usefixtures("configured_env")
def test_blank_input_and_exit_do_not_send_requests(
    isolated_cli: SimpleNamespace,
) -> None:
    with patch("builtins.input", side_effect=[" ", " ExIt "]):
        assert cli.main() == 0

    isolated_cli.client.responses.create.assert_not_called()


@pytest.mark.usefixtures("configured_env")
def test_incomplete_response_preserves_previous_response_id(
    isolated_cli: SimpleNamespace,
    capsys: pytest.CaptureFixture[str],
) -> None:
    isolated_cli.client.responses.create.side_effect = [
        SimpleNamespace(status="completed", id="resp_first", output_text="こんにちは。"),
        SimpleNamespace(
            status="incomplete",
            id="resp_incomplete",
            error=None,
            incomplete_details="max_output_tokens",
        ),
        SimpleNamespace(status="completed", id="resp_last", output_text="ご案内します。"),
    ]
    with patch("builtins.input", side_effect=["こんにちは", "予約", "再試行", "exit"]):
        assert cli.main() == 0

    calls = isolated_cli.client.responses.create.call_args_list
    assert len(calls) == 3
    assert calls[1].kwargs["previous_response_id"] == "resp_first"
    assert calls[2].kwargs["previous_response_id"] == "resp_first"
    assert "会話の参照は更新していません" in capsys.readouterr().err


@pytest.mark.usefixtures("configured_env")
def test_authentication_error_is_reported(
    isolated_cli: SimpleNamespace,
    capsys: pytest.CaptureFixture[str],
) -> None:
    isolated_cli.client.responses.create.side_effect = ClientAuthenticationError(
        message="test authentication failure"
    )
    with patch("builtins.input", return_value="こんにちは"):
        assert cli.main() == 1

    captured = capsys.readouterr()
    assert "認証に失敗しました" in captured.err
    assert "az login" in captured.err
    assert "test authentication failure" in captured.err
    isolated_cli.client.responses.create.assert_called_once()
