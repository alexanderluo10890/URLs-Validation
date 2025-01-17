# Testing Concepts Overview

## Unit Testing

### What are Unit Tests?
Unit tests are a software testing method where individual components (units) of software are tested in isolation. A unit is typically the smallest testable part of an application, such as a function or method.

### Characteristics of Good Unit Tests
- **Isolated**: Tests should be independent and not rely on external systems or other tests
- **Repeatable**: Same results every time they run
- **Fast**: Quick to execute
- **Clear**: Easy to understand what's being tested
- **Single Responsibility**: Each test focuses on one specific functionality

## Types of Tests in Our Project

### 1. Model Tests
Tests that validate data structures and their behavior.
```python
def test_valid_pokemon_model():
    pokemon = Pokemon(id=1, name="Bulbasaur", ...)
    assert pokemon.id == 1
    assert pokemon.name == "Bulbasaur"
```

### 2. Service Tests
Tests that verify business logic and operations.
```python
def test_get_pokemon_by_id():
    pokemon = get_pokemon_by_id(1)
    assert pokemon["name"] == "Bulbasaur"
```

### 3. File Operation Tests
Tests that verify data persistence and file handling.
```python
def test_save_pokemon_data():
    save_pokemon_data([{"id": 1, "name": "Bulbasaur"}])
    assert file_exists("pokedex.json")
```

## Mocking

### What is Mocking?
Mocking is a technique used in unit testing where actual objects are replaced with mock objects that simulate their behavior. This is useful when:
- The real object is impractical to incorporate into a unit test
- The real object has non-deterministic behavior
- You want to verify how an object is being used

### Examples of Mocking in Our Tests
```python
# Mocking file operations
monkeypatch.setattr("app.services.pokemon_service.save_pokemon_data", 
                    lambda x: None)

# Mocking database data
monkeypatch.setattr(pokemon_service, "pokemon_list", 
                    mock_db_with_all_variants["pokemon"])
```

## Monkeypatching

### What is Monkeypatching?
Monkeypatching is a technique for modifying classes or modules in the runtime to change their behavior. In testing, we use it to:
- Replace functions with mock implementations
- Modify environment variables
- Change module-level variables

### Using pytest's monkeypatch
```python
def test_with_monkeypatch(monkeypatch):
    # Replace a function
    monkeypatch.setattr(module, "function_name", mock_function)
    
    # Set an environment variable
    monkeypatch.setenv("ENV_VAR", "test_value")
    
    # Modify a dictionary
    monkeypatch.setitem(some_dict, "key", "value")
```

## Test Fixtures

### What are Fixtures?
Fixtures are a way to provide a fixed baseline for tests. They:
- Set up test data
- Provide test dependencies
- Can be reused across multiple tests

### Example Fixtures from Our Project
```python
@pytest.fixture
def mock_db_with_all_variants():
    """Provides test database with different Pokemon types"""
    return {
        "pokemon": [
            {"name": "Bulbasaur", ...},
            {"name": "Ditto", ...},
            {"name": "Vaporeon", ...}
        ]
    }
```

## Test Organization

### Directory Structure
```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_file_operations.py
└── conftest.py
```

### Shared Test Resources
- `conftest.py`: Contains shared fixtures
- Test data files
- Helper functions

## Test Coverage Types

### 1. Happy Path Testing
Testing the standard, expected flow:
```python
def test_add_new_pokemon_basic():
    """Test adding a valid new Pokemon"""
```

### 2. Error Path Testing
Testing error handling and edge cases:
```python
def test_add_duplicate_pokemon():
    """Test adding a Pokemon with existing ID"""
```

### 3. Edge Case Testing
Testing boundary conditions:
```python
def test_empty_pokemon_list():
    """Test handling empty Pokemon list"""
```

## Best Practices We Follow

1. **Clear Test Names**
   - Descriptive of what's being tested
   - Includes the scenario being tested

2. **Test Independence**
   - Each test can run in isolation
   - No dependencies between tests

3. **Arrange-Act-Assert Pattern**
   ```python
   # Arrange
   pokemon_data = {...}
   
   # Act
   result = add_new_pokemon(pokemon_data)
   
   # Assert
   assert result["name"] == "TestMon"
   ```

4. **Mock External Dependencies**
   - File system operations
   - Database calls
   - External services

5. **Clean Up After Tests**
   - Remove test files
   - Reset mocked states
   - Clean up any test data


## Integration Testing

### What are Integration Tests?
Integration tests verify that different components of the application work together correctly. Unlike unit tests that test components in isolation, integration tests examine the interactions between integrated components.

### Characteristics of Good Integration Tests
- **Realistic Environment**: Tests should mirror production setup
- **End-to-End Flow**: Tests complete workflows, not just single operations
- **Data Persistence**: Verifies data is correctly saved and retrieved
- **Error Handling**: Tests how components handle errors together
- **State Management**: Maintains and verifies system state across operations

## Types of Integration Tests in Our Project

### 1. CRUD Flow Tests
Tests that verify complete Create, Read, Update operations work together.
```python
def test_create_read_update_flow():
    # Create Pokemon
    response = client.post("/pokemon/", json=new_pokemon)
    assert response.status_code == 201
    
    # Read it back
    get_response = client.get("/pokemon/1")
    assert get_response.json()["name"] == new_pokemon["name"]
```

### 2. Data Persistence Tests
Tests that verify data is correctly saved and retrieved from storage.
```python
def test_data_persistence():
    # Create data
    client.post("/pokemon/", json=new_pokemon)
    
    # Verify file contents
    with open(test_db, "r") as f:
        saved_data = json.load(f)
    assert saved_data["pokemon"][0]["name"] == "Charmander"
```

### 3. Error Handling Flow Tests
Tests that verify error handling across components.
```python
def test_error_handling_flow():
    # Test non-existent resource
    response = client.get("/pokemon/999")
    assert response.status_code == 404
    
    # Test duplicate creation
    response = client.post("/pokemon/", json=existing_pokemon)
    assert response.status_code == 400
```

## Integration Test Patterns

### Database Management
Integration tests need careful database handling:
```python
@pytest.fixture(scope="session", autouse=True)
def backup_restore_db():
    """Backup real database and restore after tests"""
    if os.path.exists("pokedex.json"):
        shutil.copy("pokedex.json", "pokedex.json.backup")
    yield
    if os.path.exists("pokedex.json.backup"):
        shutil.copy("pokedex.json.backup", "pokedex.json")
```

### Test Client Usage
FastAPI's TestClient allows testing HTTP endpoints:
```python
from fastapi.testclient import TestClient

client = TestClient(app)
response = client.post("/pokemon/", json=pokemon_data)
assert response.status_code == 201
```

### State Verification
Testing state across operations:
```python
def test_evolution_chain_integrity():
    # Create Pokemon with evolution
    client.post("/pokemon/", json=pokemon_with_evolution)
    
    # Verify related Pokemon
    response = client.get("/pokemon/1")
    assert response.json()["next_evolution"][0]["name"] == "Ivysaur"
```

## Best Practices for Integration Tests

1. **Test Database Isolation**
   - Use separate test database
   - Backup and restore production data
   - Clean state between tests

2. **Complete Workflows**
   - Test entire features
   - Verify all components interact correctly
   - Check data persistence

3. **Realistic Scenarios**
   ```python
   # Test real-world workflow
   def test_complete_pokemon_lifecycle():
       # Create
       create_response = client.post("/pokemon/", json=new_pokemon)
       
       # Read
       read_response = client.get(f"/pokemon/{pokemon_id}")
       
       # Update
       update_response = client.patch(f"/pokemon/{pokemon_id}", 
                                    json=updated_data)
       
       # Verify each step
       assert create_response.status_code == 201
       assert read_response.status_code == 200
       assert update_response.status_code == 200
   ```

4. **Error Handling**
   - Test system-wide error handling
   - Verify error propagation
   - Check error recovery

5. **Resource Cleanup**
   - Clean up test data
   - Reset system state
   - Restore initial conditions

## End-to-End (E2E) Testing

### What are E2E Tests?
E2E tests verify that all components of the application work together through complete user scenarios. They simulate real user interactions and validate entire workflows from start to finish.

### Characteristics of Good E2E Tests
- **Complete Workflows**: Tests entire features from start to finish
- **Real Data Flow**: Verifies data moves correctly through all layers
- **User Perspective**: Tests from the user's point of view
- **System Integration**: Validates all components working together

### Example E2E Test
```python
def test_complete_pokemon_lifecycle():
    # Create new Pokemon
    create_response = client.post("/pokemon/", json=new_pokemon)
    
    # Verify in database
    with open(test_db, "r") as f:
        saved_data = json.load(f)
    
    # Update evolution chain
    update_response = client.patch(f"/pokemon/{id}", 
                                 json=evolution_data)
    
    # Verify complete workflow
    final_response = client.get(f"/pokemon/{id}")
    assert final_response.json()["evolution"] == expected_data
```

### E2E Test Organization
- Complete Evolution Chain Tests
- Pokemon Lifecycle Tests
- Data Consistency Tests

### When to Use E2E Tests
- Testing complete user workflows
- Validating critical business paths
- Verifying system integration
- Testing data flow through all layers

### E2E vs Integration Tests
- E2E tests complete workflows
- Integration tests focus on component interactions
- E2E includes data persistence
- E2E simulates real user scenarios