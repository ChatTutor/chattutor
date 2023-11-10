from core.vectordatabase import VectorDatabase
import pytest

@pytest.fixture
def user_db():
    user_db = VectorDatabase("34.123.154.72:8000", "chroma", hosted=True)
    return user_db

def test_1():
    assert 1 == 1

# def test_wrong_db_provider():
#     with pytest.raises(TypeError):
#         user_db = VectorDatabase("34.123.154.72:8000", "wrong_provider", hosted=True)
