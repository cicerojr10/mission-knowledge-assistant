from fastapi import FastAPI

app = FastAPI(
    title="Mission Knowledge Assistant",
    version="0.1.0",
    description="API base para um assistente de IA aplicada com RAG."
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "mission-knowledge-assistant"
    }