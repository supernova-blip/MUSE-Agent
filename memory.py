# memory.py

import json
import os

MEMORY_FILE = "memory.json"


def load_memory():
    """Load user memory from the JSON file."""

    if not os.path.exists(MEMORY_FILE):
        return {
            "preferences": {
                "genres": [],
                "moods": [],
                "artists": [],
                "themes": []
            },
            "liked_songs": [],
            "disliked_songs": []
        }

    with open(MEMORY_FILE, "r") as file:
        return json.load(file)


def save_memory(memory):
    """Save user memory to the JSON file."""

    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)


def update_memory(category, value):
    """Add a new preference to memory."""

    memory = load_memory()

    if category in memory["preferences"]:
        if value not in memory["preferences"][category]:
            memory["preferences"][category].append(value)

    save_memory(memory)


def add_liked_song(song):
    """Remember a song liked by the user."""

    memory = load_memory()

    if song not in memory["liked_songs"]:
        memory["liked_songs"].append(song)

    save_memory(memory)


def get_preferences():
    """Retrieve all stored user preferences."""

    memory = load_memory()

    return memory

def remember_preference(category, value):
    """Store a user's music preference in memory."""

    memory = load_memory()

    if category in memory["preferences"]:
        if value not in memory["preferences"][category]:
            memory["preferences"][category].append(value)

    save_memory(memory)

    return {
        "success": True,
        "message": f"Remembered that the user likes {value} ({category})."
    }