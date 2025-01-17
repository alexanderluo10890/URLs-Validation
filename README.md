How to run file locally: uv run uvicorn main:app --reload




request (get, post, patch) => endpoint (/pokemon/{id}) => reponse (200, data)

user request => handle request => schema => endpoints => business logic => responses


main => simple entryway to the app 
api => routes
schema => object validation
service => business logic


@router.get("/{id}")
def get_pokemon(id: int):
    """Route to fetch a Pokémon by ID."""
    try:
        return get_pokemon_by_id(id)
    except HTTPException as e:
        raise e  # Rethrow known exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def get_pokemon_by_id(id: int):
    """Fetch a Pokémon by its ID."""
    try:
        for pokemon in pokemon_list:
            if pokemon["id"] == id:
                return pokemon
        raise HTTPException(status_code=404, detail="Pokemon not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Pokémon: {str(e)}")


router.get gets called 
router.get takes an id value
router.get calls get_pokemon_by_id with the id value
get_pokemon_by_id tries to find the pokemon and if there an exception (technically a real error) it will get returned

router.get(1)
router.get(1).get_pokemon_by_id(1)
{"name": "bulbasaur"}

fetch_pokemon = get_pokemon_by_id(1)
print(fetch_pokemon)
{"name": "bulbasaur"}

#error case
router.get(1)
router.get(1).get_pokemon_by_id(e)

print(fetch_pokemon)
HTTPException(status_code=500, detail=f"Error fetching Pokémon: {str(server error 500, json malformed )}")


