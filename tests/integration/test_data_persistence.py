import json
from app.utils.file_operations import save_pokemon_data

def test_data_persistence(client, empty_db, monkeypatch):
    """Test data persistence across operations"""
    # Need to patch the service to use our test db
    import app.services.validators as validators
    import os
    
    # Print current directory for debugging
    print(f"Current directory: {os.getcwd()}")
    print(f"Test DB path: {empty_db}")
    
    # Patch the service to use our test database
    def mock_save_data(data):
        save_pokemon_data(data, empty_db)
    
    monkeypatch.setattr(validators, "save_pokemon_data", mock_save_data)
    
    # Create initial Pokemon
    new_pokemon = {
        "id": 4,
        "num": "004",
        "name": "Charmander",
        "img": "http://example.com/charmander.jpg",
        "type": ["Fire"],
        "height": "0.6 m",
        "weight": "8.5 kg",
        "weaknesses": ["Water", "Rock", "Ground"]
    }
    
    # Create
    create_response = client.post("/pokemon/", json=new_pokemon)
    print(f"Create response status: {create_response.status_code}")
    print(f"Create response content: {create_response.json()}")
    assert create_response.status_code == 201
    
    # Verify data was saved to file
    with open(empty_db, "r") as f:
        saved_data = json.load(f)
    print(f"Saved data content: {json.dumps(saved_data, indent=2)}")
    
    # Additional check before the next() operation
    pokemon_ids = [p["id"] for p in saved_data["pokemon"]]
    print(f"Available Pokemon IDs in file: {pokemon_ids}")
    
    saved_pokemon = next(p for p in saved_data["pokemon"] if p["id"] == 4)
    assert saved_pokemon["name"] == "Charmander"