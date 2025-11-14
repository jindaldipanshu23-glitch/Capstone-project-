"""
Optional: Vertex AI Agent Engine helper (starter).

Use only if you want to deploy to Vertex AI. Requires GOOGLE_APPLICATION_CREDENTIALS and GCP project.
This is a minimal example inspired by Vertex AI samples.
"""

import os

def get_exchange_rate(currency_from: str = "USD", currency_to: str = "EUR", currency_date: str = "latest"):
    import requests
    resp = requests.get(f"https://api.frankfurter.app/{currency_date}", params={"from": currency_from, "to": currency_to})
    return resp.json()

def create_and_deploy_agent(project_id: str, location: str = "us-central1"):
    try:
        import vertexai
        from vertexai import agent_engines
        from vertexai.preview.reasoning_engines import LangchainAgent
    except Exception as e:
        raise RuntimeError("Install google-cloud-aiplatform[agent_engines,langchain] to use Vertex AI features.") from e

    vertexai.init(project=project_id, location=location)
    model = "gemini-2.0-flash"
    agent = LangchainAgent(model=model, tools=[get_exchange_rate])
    remote_agent = agent_engines.create(
        agent,
        requirements=[
            "google-cloud-aiplatform[agent_engines,langchain]",
            "cloudpickle==3.0.0",
            "pydantic>=2.10",
            "requests",
        ],
    )
    print("Deployed agent resource:", remote_agent.resource_name)
    return remote_agent
