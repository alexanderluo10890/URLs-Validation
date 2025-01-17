import pytest
import json
import os
import shutil
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Test client for API endpoints"""
    return TestClient(app)

# Pokemon Data Fixtures
@pytest.fixture
def ditto_data():
    """Pokemon with no evolution"""
    return {
        "id": 132,
        "num": "132",
        "name": "Ditto",
        "img": "http://www.serebii.net/pokemongo/pokemon/132.png",
        "type": ["Normal"],
        "height": "0.30 m",
        "weight": "4.0 kg",
        "weaknesses": ["Fighting"]
    }

@pytest.fixture
def vaporeon_data():
    """Pokemon with only prev_evolution"""
    return {
        "id": 134,
        "num": "134",
        "name": "Vaporeon",
        "img": "http://www.serebii.net/pokemongo/pokemon/134.png",
        "type": ["Water"],
        "height": "0.99 m",
        "weight": "29.0 kg",
        "weaknesses": ["Electric", "Grass"],
        "prev_evolution": [
            {
                "num": "133",
                "name": "Eevee"
            }
        ]
    }

@pytest.fixture
def bulbasaur_data():
    """Pokemon with only next_evolution"""
    return {
        "id": 1,
        "num": "001",
        "name": "Bulbasaur",
        "img": "http://www.serebii.net/pokemongo/pokemon/001.png",
        "type": ["Grass", "Poison"],
        "height": "0.71 m",
        "weight": "6.9 kg",
        "weaknesses": ["Fire", "Ice", "Flying", "Psychic"],
        "next_evolution": [
            {
                "num": "002",
                "name": "Ivysaur"
            },
            {
                "num": "003",
                "name": "Venusaur"
            }
        ]
    }

@pytest.fixture
def ivysaur_data():
    """Pokemon with both prev_evolution and next_evolution"""
    return {
        "id": 2,
        "num": "002",
        "name": "Ivysaur",
        "img": "http://www.serebii.net/pokemongo/pokemon/002.png",
        "type": ["Grass", "Poison"],
        "height": "0.99 m",
        "weight": "13.0 kg",
        "weaknesses": ["Fire", "Ice", "Flying", "Psychic"],
        "prev_evolution": [
            {
                "num": "001",
                "name": "Bulbasaur"
            }
        ],
        "next_evolution": [
            {
                "num": "003",
                "name": "Venusaur"
            }
        ]
    }

# Database Fixtures
@pytest.fixture
def test_db():
    """Create a temporary test database file"""
    filename = "test_pokedex.json"
    if os.path.exists(filename):
        os.remove(filename)
    
    # Create empty database
    with open(filename, "w") as f:
        json.dump({"pokemon": []}, f)
    
    yield filename
    
    # Cleanup
    if os.path.exists(filename):
        os.remove(filename)

@pytest.fixture(scope="session", autouse=True)
def backup_restore_db():
    """Backup the real database before all tests and restore it after"""
    # Backup original if it exists
    if os.path.exists("pokedex.json"):
        shutil.copy("pokedex.json", "pokedex.json.backup")
    
    yield
    
    # Restore from backup
    if os.path.exists("pokedex.json.backup"):
        shutil.copy("pokedex.json.backup", "pokedex.json")
        os.remove("pokedex.json.backup")

@pytest.fixture
def mock_db_with_all_variants(test_db):
    """Create a test database with all Pokemon variants"""
    test_data = {
        "pokemon": [
            {
                "id": 1,
                "num": "001",
                "name": "Bulbasaur",
                "img": "http://www.serebii.net/pokemongo/pokemon/001.png",
                "type": ["Grass", "Poison"],
                "height": "0.71 m",
                "weight": "6.9 kg",
                "weaknesses": ["Fire", "Ice", "Flying", "Psychic"],
                "next_evolution": [
                    {
                        "num": "002",
                        "name": "Ivysaur"
                    }
                ]
            },
            {
                "id": 132,
                "num": "132",
                "name": "Ditto",
                "img": "http://www.serebii.net/pokemongo/pokemon/132.png",
                "type": ["Normal"],
                "height": "0.30 m",
                "weight": "4.0 kg",
                "weaknesses": ["Fighting"]
            },
            {
                "id": 134,
                "num": "134",
                "name": "Vaporeon",
                "img": "http://www.serebii.net/pokemongo/pokemon/134.png",
                "type": ["Water"],
                "height": "0.99 m",
                "weight": "29.0 kg",
                "weaknesses": ["Electric", "Grass"],
                "prev_evolution": [
                    {
                        "num": "133",
                        "name": "Eevee"
                    }
                ]
            }
        ]
    }
    with open(test_db, "w") as f:
        json.dump(test_data, f)
    return test_data

# Evolution Data Fixtures
@pytest.fixture
def evolution_data():
    """Sample evolution data for testing"""
    return {
        "prev_evolution": [
            {
                "num": "001",
                "name": "PrevForm"
            }
        ],
        "next_evolution": [
            {
                "num": "003",
                "name": "NextForm"
            }
        ]
    }

@pytest.fixture
def invalid_evolution_data():
    """Invalid evolution data for testing validation"""
    return {
        "prev_evolution": [
            {
                "name": "MissingNum"  # Missing num field
            }
        ],
        "next_evolution": [
            {
                "num": "003"  # Missing name field
            }
        ]
    }

# Service Mocking Fixtures
@pytest.fixture
def mock_pokemon_service(monkeypatch):
    """Mock the Pokemon service layer for testing"""
    class MockPokemonService:
        def __init__(self):
            self.pokemon_list = []

        def get_pokemon_by_id(self, id):
            for pokemon in self.pokemon_list:
                if pokemon["id"] == id:
                    return pokemon
            raise HTTPException(status_code=404, detail="Pokemon not found")

        def add_new_pokemon(self, pokemon):
            self.pokemon_list.append(pokemon.model_dump())  # Updated to model_dump
            return self.pokemon_list

        def update_existing_pokemon(self, id, updates):
            for pokemon in self.pokemon_list:
                if pokemon["id"] == id:
                    pokemon.update(updates.model_dump(exclude_unset=True))  # Updated to model_dump
                    return {"message": "Pokemon updated successfully", "pokemon": pokemon}
            raise HTTPException(status_code=404, detail="Pokemon not found")

    mock_service = MockPokemonService()
    monkeypatch.setattr("app.services.pokemon_service", mock_service)
    return mock_service

@pytest.fixture(autouse=True)
def reset_pokemon_service():
    """Reset pokemon service state before each test"""
    import app.services.validators as validators
    yield
    # Reset after each test
    validators.pokemon_list = validators.load_pokemon_data()["pokemon"]

@pytest.fixture(autouse=True)
def reset_test_db(test_db):
    """Reset test database before each integration test"""
    # Start with empty Pokemon list
    empty_data = {"pokemon": []}
    with open(test_db, "w") as f:
        json.dump(empty_data, f)
    
    # Reset the service's pokemon_list
    import app.services.validators as validators
    validators.pokemon_list = []

@pytest.fixture
def empty_db(test_db):
    """Create an empty test database"""
    empty_data = {"pokemon": []}
    with open(test_db, "w") as f:
        json.dump(empty_data, f)
    
    # Reset the service's pokemon_list
    import app.services.validators as validators
    validators.pokemon_list = []
    return test_db

@pytest.fixture
def populated_db(test_db):
    """Create a test database with initial data"""
    initial_data = {
        "pokemon": [
            {
                "id": 1,
                "num": "001",
                "name": "Bulbasaur",
                "img": "http://example.com/bulbasaur.jpg",
                "type": ["Grass", "Poison"],
                "height": "0.7 m",
                "weight": "6.9 kg",
                "weaknesses": ["Fire", "Ice", "Flying", "Psychic"],
                "next_evolution": [
                    {
                        "num": "002",
                        "name": "Ivysaur"
                    }
                ]
            }
        ]
    }
    with open(test_db, "w") as f:
        json.dump(initial_data, f)
    
    # Reset the service's pokemon_list
    import app.services.validators as validators
    validators.pokemon_list = initial_data["pokemon"]
    return test_db

@pytest.fixture(scope="function")
def e2e_test_db(monkeypatch):
    """Setup test database for E2E tests with complete initial data"""
    test_file = "e2e_test_pokedex.json"
    
    # Initial test data - complete Pokemon evolution chain
    test_data = {
        "pokemon": [
            {
                "id": 1,
                "num": "001",
                "name": "Bulbasaur",
                "img": "http://www.serebii.net/pokemongo/pokemon/001.png",
                "type": ["Grass", "Poison"],
                "height": "0.71 m",
                "weight": "6.9 kg",
                "weaknesses": ["Fire", "Ice", "Flying", "Psychic"],
                "next_evolution": [{"num": "002", "name": "Ivysaur"}]
            },
            {
                "id": 2,
                "num": "002",
                "name": "Ivysaur",
                "img": "http://www.serebii.net/pokemongo/pokemon/002.png",
                "type": ["Grass", "Poison"],
                "height": "0.99 m",
                "weight": "13.0 kg",
                "weaknesses": ["Fire", "Ice", "Flying", "Psychic"],
                "prev_evolution": [{"num": "001", "name": "Bulbasaur"}],
                "next_evolution": [{"num": "003", "name": "Venusaur"}]
            },
            {
                "id": 3,
                "num": "003",
                "name": "Venusaur",
                "img": "http://www.serebii.net/pokemongo/pokemon/003.png",
                "type": ["Grass", "Poison"],
                "height": "2.0 m",
                "weight": "100.0 kg",
                "weaknesses": ["Fire", "Ice", "Flying", "Psychic"],
                "prev_evolution": [
                    {"num": "001", "name": "Bulbasaur"},
                    {"num": "002", "name": "Ivysaur"}
                ]
            }
        ]
    }
    
    
    # Write test data
    with open(test_file, "w") as f:
        json.dump(test_data, f)
    
    # Patch service to use test database
    import app.services.validators as validators
    from app.utils.file_operations import save_pokemon_data
    
    # Reload data from test file
    validators.pokemon_list = test_data["pokemon"]

    # Patch the save function to use test file
    def mock_save_data(data):
        save_pokemon_data(data, test_file)
    monkeypatch.setattr(validators, "save_pokemon_data", mock_save_data)
    
    yield test_file
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)