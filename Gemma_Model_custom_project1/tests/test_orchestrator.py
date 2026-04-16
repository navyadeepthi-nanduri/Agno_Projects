import pytest
from app.services.orchestrator import ChatOrchestrator


def test_input_mode_text():
    orchestrator = ChatOrchestrator()
    assert orchestrator._determine_input_mode(True, False, False) == "text"


def test_input_mode_image():
    orchestrator = ChatOrchestrator()
    assert orchestrator._determine_input_mode(False, True, False) == "image"


def test_input_mode_audio():
    orchestrator = ChatOrchestrator()
    assert orchestrator._determine_input_mode(False, False, True) == "audio"


def test_input_mode_multimodal():
    orchestrator = ChatOrchestrator()
    assert orchestrator._determine_input_mode(True, True, False) == "multimodal"


def test_input_mode_none():
    orchestrator = ChatOrchestrator()
    assert orchestrator._determine_input_mode(False, False, False) == "none"