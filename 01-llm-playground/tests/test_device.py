import pytest
import torch

from playground.device import pick_device


def test_defaults_to_mps_when_available(monkeypatch):
    monkeypatch.delenv("PLAYGROUND_DEVICE", raising=False)
    expected = "mps" if torch.backends.mps.is_available() else "cpu"
    assert pick_device().type == expected


def test_override_forces_cpu(monkeypatch):
    monkeypatch.setenv("PLAYGROUND_DEVICE", "cpu")
    assert pick_device().type == "cpu"


def test_override_is_case_insensitive(monkeypatch):
    monkeypatch.setenv("PLAYGROUND_DEVICE", " CPU ")
    assert pick_device().type == "cpu"


def test_invalid_override_raises(monkeypatch):
    monkeypatch.setenv("PLAYGROUND_DEVICE", "cuda")
    with pytest.raises(ValueError, match="not valid"):
        pick_device()
