from app.services.llm import LLMClient


def test_repairs_groq_failed_generation_with_string_set_and_thousands():
    client = LLMClient.__new__(LLMClient)
    bad = '''{
      "title":"Medición de Campaña Noctra Coffee",
      "summary":"Definir KPIs y criterios de éxito",
      "items":["North Star Metric"],
      "data":{
        "targets":{"awareness":50.000,"engagement":5.000},
        "hipotesis":{
          "La campaña aumentará conciencia de marca",
          "La landing aumentará conversiones"
        }
      }
    }'''
    data = client._parse_json(bad)
    assert data["data"]["targets"]["awareness"] == 50000
    assert data["data"]["hipotesis"] == [
        "La campaña aumentará conciencia de marca",
        "La landing aumentará conversiones",
    ]
