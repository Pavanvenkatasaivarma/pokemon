import mysql.connector
import streamlit as st
import requests
import json

# Create a connection to MySQL server (without specifying a database)
def create_server_connection():
    return mysql.connector.connect(
        host='localhost',       # Replace with your MySQL host
        user='root',           # Replace with your MySQL username
        password='Pavan@7389'  # Replace with your MySQL password
    )

# Create the database if it doesn't exist
def create_database():
    conn = create_server_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS pokemon_db")
    conn.commit()
    cursor.close()
    conn.close()

# Create a connection to the MySQL database (after it's created)
def create_connection():
    return mysql.connector.connect(
        host='localhost',       # Replace with your MySQL host
        user='root',           # Replace with your MySQL username
        password='Pavan@7389', # Replace with your MySQL password
        database='pokemon_db'  # Replace with your MySQL database name
    )

# Create a table for Pokémon data
def create_table():
    conn = create_connection()
    cursor = conn.cursor()

    # Drop the table if it exists (optional)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pokemon (
            id INT PRIMARY KEY,
            name VARCHAR(50),
            height INT,
            weight INT,
            types TEXT,
            abilities TEXT,
            base_experience INT,
            stats TEXT,
            moves TEXT,
            egg_groups TEXT,
            habitat TEXT,
            forms TEXT
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

def fetch_pokemon_species_data(species_url):
    response = requests.get(species_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching species data: {response.status_code}")
        return None

def get_pokemon_data(pokemon_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        species_data = fetch_pokemon_species_data(data['species']['url'])
        
        pokemon_info = {
            "id": data['id'],
            "name": data['name'].capitalize(),
            "height": data['height'],
            "weight": data['weight'],
            "types": ', '.join([type_info['type']['name'].capitalize() for type_info in data['types']]),
            "abilities": ', '.join([ability['ability']['name'].capitalize() for ability in data['abilities']]),
            "base_experience": data['base_experience'],
            # Collecting stats as a JSON string for easier storage
            "stats": json.dumps({stat['stat']['name'].capitalize(): {
                "base_stat": stat['base_stat'],
                "effort": stat['effort']
            } for stat in data['stats']}),
            "moves": ', '.join([move['move']['name'].capitalize() for move in data['moves']]),
            "egg_groups": ', '.join([egg_group['name'].capitalize() for egg_group in species_data.get('egg_groups', [])]),
            "habitat": species_data['habitat']['name'].capitalize() if species_data.get('habitat') else "Unknown",
            "forms": ', '.join([form['name'].capitalize() for form in species_data.get('forms', [])])  
        }
        return pokemon_info
    else:
        return None

# Insert fetched Pokémon data into MySQL database
def insert_pokemon_into_db(pokemon_info):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO pokemon (id, name, height, weight, types, abilities, base_experience, stats, moves, egg_groups, habitat, forms) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                      ON DUPLICATE KEY UPDATE
                      name=VALUES(name), height=VALUES(height), weight=VALUES(weight),
                      types=VALUES(types), abilities=VALUES(abilities), base_experience=VALUES(base_experience),
                      stats=VALUES(stats), moves=VALUES(moves), egg_groups=VALUES(egg_groups),
                      habitat=VALUES(habitat), forms=VALUES(forms)''', 
                    (pokemon_info['id'], pokemon_info['name'], pokemon_info['height'], 
                     pokemon_info['weight'], pokemon_info['types'], 
                     pokemon_info['abilities'], pokemon_info['base_experience'], 
                     pokemon_info['stats'], pokemon_info['moves'], 
                     pokemon_info['egg_groups'], pokemon_info['habitat'], 
                     pokemon_info['forms']))
    conn.commit()
    cursor.close()
    conn.close()

def list_all_pokemon():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pokemon")
    all_pokemon = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()
    return all_pokemon


# --- Streamlit Interface ---

# Ensure database and table are created
create_database()
create_table()

# Streamlit app title
st.title("Pokemon Pokedesk with MySQL")

# Sidebar: Fetch Pokémon from PokéAPI
st.sidebar.header("Fetch Pokémon Data")

pokemon_name = st.sidebar.text_input("Enter Pokémon name")

if st.sidebar.button("Fetch and Add to Database"):
    if pokemon_name:
        pokemon_info = get_pokemon_data(pokemon_name)
        if pokemon_info:
            insert_pokemon_into_db(pokemon_info)
            st.sidebar.success(f"{pokemon_info['name']} has been added to the database!")

            conn = create_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM pokemon WHERE name = %s", (pokemon_info['name'],))
            pokemon = cursor.fetchall()
            cursor.close()
            conn.close()
            
            for pokemon in pokemon:
                st.subheader(f"{pokemon[1]} (ID: {pokemon[0]})")
                st.text(f"Height: {pokemon[2]} decimetres")
                st.text(f"Weight: {pokemon[3]} hectograms")
                st.text(f"Types: {pokemon[4]}")
                st.text(f"Abilities: {pokemon[5]}")
                st.text(f"Base Experience: {pokemon[6]}")
                st.text(f"Stats: {pokemon[7]}")
                st.text(f"Moves: {pokemon[8]}")
                st.text(f"Egg Groups: {pokemon[9]}")
                st.text(f"Habitat: {pokemon[10]}")
                st.text(f"Forms: {pokemon[11]}")

        else:
            st.sidebar.error(f"Pokémon {pokemon_name} not found.")
    else:
        st.sidebar.error("Please enter a Pokémon name.")

# Main area: Display Pokémon in the database
st.header("Pokémon Stored in Database")



pokemon_list = list_all_pokemon()
if st.sidebar.button("Display all the Pokémon in Database"):
    if pokemon_list:
        for pokemon in pokemon_list:
            st.subheader(f"{pokemon[1]} (ID: {pokemon[0]})")
            st.text(f"Height: {pokemon[2]} decimetres")
            st.text(f"Weight: {pokemon[3]} hectograms")
            st.text(f"Types: {pokemon[4]}")
            st.text(f"Abilities: {pokemon[5]}")
            st.text(f"Base Experience: {pokemon[6]}")
            st.text(f"Stats: {pokemon[7]}")
            st.text(f"Moves: {pokemon[8]}")
            st.text(f"Egg Groups: {pokemon[9]}")
            st.text(f"Habitat: {pokemon[10]}")
            st.text(f"Forms: {pokemon[11]}")
    else:
        st.write("No Pokémon in the database.")

