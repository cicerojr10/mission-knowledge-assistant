import os
import sys


TEST_DATABASE_URL = (
    "postgresql://mission_user:mission_password"
    "@localhost:5432/mission_knowledge_test"
)

if "app.database" in sys.modules:
    raise RuntimeError(
        "Database module loaded before test configuration."
    )

os.environ["DATABASE_URL"] = TEST_DATABASE_URL

# Prevent unintended real OpenAI calls during tests.
os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_ANSWERABILITY_MODEL"] = ""

from app.database import engine  # noqa: E402


if engine.url.database != "mission_knowledge_test":
    raise RuntimeError(
        "Pytest must use mission_knowledge_test."
    )
