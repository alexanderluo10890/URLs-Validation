def test_create_read_update_flow(client, test_db):
    """Test complete flow: Create → Read → Update Pokemon"""
    # Create new Pokemon
    new_pokemon = {
        "id": 2,
        "num": "002",
        "name": "Ivysaur",
        "img": "http://example.com/ivysaur.jpg",
        "type": ["Grass", "Poison"],
        "height": "1.0 m",
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
    
    # Create
    create_response = client.post("/pokemon/", json=new_pokemon)
    print(f"Response status: {create_response.status_code}")
    print(f"Response content: {create_response.json()}")
    assert create_response.status_code == 201