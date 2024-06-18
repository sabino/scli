import pytest
import requests
from unittest.mock import patch, mock_open
from src.sabcli.commands.generate_image import (
    authenticate_session,
    enrich_prompt_with_gpt4,
    prepare_payload,
    generate_image_request,
    save_image,
    find_existing_image,
)

def test_authenticate_session_new_session():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"session_id": "12345"}
        session_id = authenticate_session("http://localhost:7801/API", None)
        assert session_id == "12345"

def test_authenticate_session_existing_session():
    session_id = authenticate_session("http://localhost:7801/API", "existing_session")
    assert session_id == "existing_session"

def test_prepare_payload():
    payload = prepare_payload("12345", 1, "test prompt", "test_model", [("key", "value")])
    assert payload["session_id"] == "12345"
    assert payload["images"] == 1
    assert payload["prompt"] == "test prompt"
    assert payload["model"] == "test_model"
    assert payload["key"] == "value"

def test_generate_image_request():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"images": ["image_url"]}
        response_json = generate_image_request("http://localhost:7801/API", {})
        assert response_json["images"] == ["image_url"]

def test_save_image():
    with patch("requests.get") as mock_get, patch("builtins.open", mock_open()), patch("os.system") as mock_system:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"image data"
        response_json = {"images": ["image_url"]}
        save_image(response_json, "localhost", 7801, "./output", False, False)
        mock_get.assert_called_once_with("http://localhost:7801/image_url")
        mock_system.assert_not_called()

def test_find_existing_image():
    with patch("os.listdir") as mock_listdir:
        mock_listdir.return_value = ["test-prompt-test_model-123.png"]
        existing_image = find_existing_image("./output", "prompt", "test_model")
        assert existing_image == "./output/test-prompt-test_model-123.png"
