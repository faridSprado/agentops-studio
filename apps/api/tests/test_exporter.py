from app.services.exporter import campaign_json, campaign_markdown, campaign_zip


def test_exporters():
    output = {
        "title": "Test",
        "summary": "Summary",
        "brief": "Brief",
        "channels": ["instagram"],
        "score": 90,
        "revisions": 0,
        "sections": {"copy": {"summary": "Copy", "items": ["A"], "data": {"instagram": {"cta": "Go"}}}},
    }
    assert b"Test" in campaign_json(output)
    assert "# Test" in campaign_markdown(output)
    assert len(campaign_zip(output)) > 100
