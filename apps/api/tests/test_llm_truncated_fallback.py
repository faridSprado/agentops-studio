from app.services.llm import LLMClient
from app.core.config import Settings


def test_truncated_json_returns_recovered_output():
    client = LLMClient(Settings(mock_mode=True))
    raw = '{"title":"Storyboard para Noctra Coffee","summary":"Desarrollar un storyboard premium","items":["Hero video","Short reel"],"data":{"hero_video":{"duration":"60 segundos","scenes":[{"time":"0-5 segundos","shot":"Plano general","screen_text":'
    out = client._fallback_from_invalid("storyboard", raw, {"project": {"name": "Noctra Coffee"}, "brief": "Campaña de café"}, ValueError("bad json"))
    assert out["title"] == "Storyboard para Noctra Coffee"
    assert out["summary"] == "Desarrollar un storyboard premium"
    assert out["items"] == ["Hero video", "Short reel"]
    assert out["data"]["recovered"] is True
