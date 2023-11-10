from core.vectordatabase import VectorDatabase
import pytest

@pytest.fixture
def user_db():
    user_db = VectorDatabase("34.123.154.72:8000", "chroma", hosted=True)
    return user_db

def test_db_provider(user_db):
    assert user_db.db_provider == "chroma"

# def test_wrong_db_provider():
#     with pytest.raises(TypeError):
#         user_db = VectorDatabase("34.123.154.72:8000", "wrong_provider", hosted=True)
