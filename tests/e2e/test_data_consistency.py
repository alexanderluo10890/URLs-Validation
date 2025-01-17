import json

def test_data_consistency_across_operations(client, e2e_test_db):
    """Test data consistency across multiple operations and verifications"""
    
    # Step 1: Create a new Pokemon
    new_pokemon = {
        "id": 133,
        "num": "133",
        "name": "Eevee",
        "img": "http://example.com/eevee.jpg",
        "type": ["Normal"],
        "height": "0.3 m",
        "weight": "6.5 kg",
        "weaknesses": ["Fighting"],
        "next_evolution": [
            {"num": "134", "name": "Vaporeon"},
            {"num": "135", "name": "Jolteon"},
            {"num": "136", "name": "Flareon"}
        ]
    }
    
    # Create Pokemon
    create_response = client.post("/pokemon/", json=new_pokemon)
    assert create_response.status_code == 201
    
    # Step 2: Verify API response matches file data
    api_response = client.get("/pokemon/133")
    assert api_response.status_code == 200
    api_data = api_response.json()
    
    with open(e2e_test_db, "r") as f:
        file_data = json.load(f)
    
    file_pokemon = next(p for p in file_data["pokemon"] if p["id"] == 133)
    
    # Verify API and file data match
    assert api_data["name"] == file_pokemon["name"]
    assert api_data["next_evolution"] == file_pokemon["next_evolution"]
    
    # Step 3: Update and verify consistency
    update_data = {
        "weight": "7.0 kg",
        "next_evolution": [
            {"num": "134", "name": "Vaporeon"}  # Reduce to one evolution
        ]
    }
    
    update_response = client.patch("/pokemon/133", json=update_data)
    assert update_response.status_code == 200
    
    # Step 4: Verify consistency after update
    updated_response = client.get("/pokemon/133")
    with open(e2e_test_db, "r") as f:
        updated_file_data = json.load(f)
    
    updated_file_pokemon = next(p for p in updated_file_data["pokemon"] if p["id"] == 133)
    
    # Verify all data sources match
    assert updated_response.json()["weight"] == "7.0 kg"
    assert updated_file_pokemon["weight"] == "7.0 kg"
    assert len(updated_response.json()["next_evolution"]) == 1
    assert len(updated_file_pokemon["next_evolution"]) == 1