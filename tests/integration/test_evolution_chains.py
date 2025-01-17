def test_evolution_chain_integrity(client, populated_db):
    """Test evolution chain consistency across operations"""
    # Create Pokemon with next evolution
    venusaur = {
        "id": 3,
        "num": "003",
        "name": "Venusaur",
        "img": "http://example.com/venusaur.jpg",
        "type": ["Grass", "Poison"],
        "height": "2.0 m",
        "weight": "100.0 kg",
        "weaknesses": ["Fire", "Ice", "Flying", "Psychic"],
        "prev_evolution": [
            {
                "num": "001",
                "name": "Bulbasaur"
            },
            {
                "num": "002",
                "name": "Ivysaur"
            }
        ]
    }
    
    # Create Venusaur
    create_response = client.post("/pokemon/", json=venusaur)
    assert create_response.status_code == 201
    
    # Verify evolution chain in Bulbasaur
    bulbasaur_response = client.get("/pokemon/1")
    assert bulbasaur_response.status_code == 200
    bulbasaur = bulbasaur_response.json()
    assert len(bulbasaur["next_evolution"]) == 1
    assert bulbasaur["next_evolution"][0]["name"] == "Ivysaur"
    
    # Update evolution chain
    update_data = {
        "prev_evolution": [
            {
                "num": "002",
                "name": "Ivysaur"
            }
        ]
    }
    update_response = client.patch("/pokemon/3", json=update_data)
    assert update_response.status_code == 200
    
    # Verify evolution chain after update
    venusaur_response = client.get("/pokemon/3")
    assert venusaur_response.status_code == 200
    updated_venusaur = venusaur_response.json()
    assert len(updated_venusaur["prev_evolution"]) == 1
    assert updated_venusaur["prev_evolution"][0]["name"] == "Ivysaur"