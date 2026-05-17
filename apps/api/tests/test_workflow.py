from app.core.config import Settings
from app.services.workflow import AgentWorkflow


def test_workflow_mock():
    settings = Settings(model_provider="mock", quality_threshold=70)
    events = []
    workflow = AgentWorkflow(settings=settings, emit=lambda agent, status, payload=None: events.append((agent, status)))
    result = workflow.run(
        {
            "project": {"name": "Demo", "audience": "creadores"},
            "brief": "Crear campaña para una herramienta de edición de video con IA",
            "channels": ["instagram", "tiktok", "landing"],
            "language": "es",
            "tone": "directo",
            "memory": [],
            "revision_count": 0,
        }
    )
    assert result["final"]["score"] >= 70
    assert result["status"] == "completed"
    assert any(item[0] == "strategy" for item in events)
