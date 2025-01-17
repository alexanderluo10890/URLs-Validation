def test_complete_pokemon_lifecycle(client, e2e_test_db):
    """Test complete Pokemon lifecycle from creation to evolution"""
    # Step 1: Create base Pokemon
    charmander_data = {
        "id": 4,
        "num": "004",
        "name": "Charmander",
        "img": "http://example.com/charmander.jpg",
        "type": ["Fire"],
        "height": "0.6 m",
        "weight": "8.5 kg",
        "weaknesses": ["Water", "Rock", "Ground"],
        "next_evolution": [
            {
                "num": "005",
                "name": "Charmeleon"
            }
        ]
    }
    
    create_response = client.post("/pokemon/", json=charmander_data)
    assert create_response.status_code == 201
    
    # Step 2: Verify creation and read data
    read_response = client.get("/pokemon/4")
    assert read_response.status_code == 200
    pokemon_data = read_response.json()
    assert pokemon_data["name"] == "Charmander"
    
    # Step 3: Update with additional evolution data
    update_data = {
        "next_evolution": [
            {
                "num": "005",
                "name": "Charmeleon"
            },
            {
                "num": "006",
                "name": "Charizard"
            }
        ]
    }
    
    update_response = client.patch("/pokemon/4", json=update_data)
    assert update_response.status_code == 200
    
    # Step 4: Verify final state
    final_response = client.get("/pokemon/4")
    assert final_response.status_code == 200
    final_data = final_response.json()
    assert len(final_data["next_evolution"]) == 2
    assert final_data["next_evolution"][1]["name"] == "Charizard"