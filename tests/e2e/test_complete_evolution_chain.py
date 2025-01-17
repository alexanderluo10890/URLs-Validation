def test_complete_evolution_workflow(client, e2e_test_db):
    """Test complete evolution chain workflow from start to finish"""
    # Step 1: Verify initial Bulbasaur state
    bulbasaur_response = client.get("/pokemon/1")
    assert bulbasaur_response.status_code == 200
    bulbasaur = bulbasaur_response.json()
    assert bulbasaur["name"] == "Bulbasaur"
    assert len(bulbasaur["next_evolution"]) == 1
    
    # Step 2: Follow evolution chain to Ivysaur
    ivysaur_response = client.get("/pokemon/2")
    assert ivysaur_response.status_code == 200
    ivysaur = ivysaur_response.json()
    assert ivysaur["name"] == "Ivysaur"
    assert len(ivysaur["prev_evolution"]) == 1
    assert len(ivysaur["next_evolution"]) == 1
    
    # Step 3: Verify final evolution Venusaur
    venusaur_response = client.get("/pokemon/3")
    assert venusaur_response.status_code == 200
    venusaur = venusaur_response.json()
    assert venusaur["name"] == "Venusaur"
    assert len(venusaur["prev_evolution"]) == 2
    
    # Step 4: Verify evolution relationships
    assert bulbasaur["next_evolution"][0]["name"] == ivysaur["name"]
    assert ivysaur["prev_evolution"][0]["name"] == bulbasaur["name"]
    assert ivysaur["next_evolution"][0]["name"] == venusaur["name"]
    assert venusaur["prev_evolution"][1]["name"] == ivysaur["name"]