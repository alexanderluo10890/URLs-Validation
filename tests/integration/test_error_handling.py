def test_error_handling_flow(client, populated_db):
    """Test error handling across different operations"""
    # Try to get non-existent Pokemon
    response = client.get("/pokemon/999")
    assert response.status_code == 404
    
    # Try to create Pokemon with duplicate ID
    duplicate_pokemon = {
        "id": 1,  # Already exists
        "num": "001",
        "name": "DuplicateMon",
        "img": "http://example.com/duplicate.jpg",
        "type": ["Normal"],
        "height": "1.0 m",
        "weight": "10.0 kg",
        "weaknesses": ["Fighting"]
    }
    response = client.post("/pokemon/", json=duplicate_pokemon)
    assert response.status_code == 400
    
    # Try to update non-existent Pokemon
    response = client.patch("/pokemon/999", json={"name": "NonExistent"})
    assert response.status_code == 404
    
    # Try to create Pokemon with invalid data
    invalid_pokemon = {
        "id": 5,
        "name": "InvalidMon"
        # Missing required fields
    }
    response = client.post("/pokemon/", json=invalid_pokemon)
    assert response.status_code == 422  # Validation error