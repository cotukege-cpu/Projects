#REQUEST API FROM POKEMON

#im tryna get pansear from pokemon black and white

import requests

base_url1 = "https://pokeapi.co/api/v2/"

def get_info(name):
    url1 = f"{base_url1}/pokemon/{name}"
    response =  requests.get(url1)


    if response.status_code == 200:
        pokemon_Data = response.json()
        return pokemon_Data

    else:
        print("Failed")

pokemon_name = "pansear"
pokemon_info = get_info(pokemon_name)

if pokemon_info:
    print(f"Name:{pokemon_info["name"].capitalize()}")
    print(f"ID:{pokemon_info["id"]}")
    print(f"Height:{pokemon_info["height"]}")
    print(f"Weight:{pokemon_info["weight"]}")