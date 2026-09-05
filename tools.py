# tools.py

music_database = [
    {
        "title": "Alien",
        "artist": "Han",
        "genre": "K-pop",
        "mood": "melancholic",
        "themes": ["loneliness", "self-reflection", "identity"]
    },
    {
        "title": "Space song",
        "artist": "Artist A",
        "genre": "Alternative",
        "mood": "melancholic",
        "themes": ["love", "loneliness", "memories"]
    },
    {
        "title": "Apocolypse",
        "artist": "cigarettes after sex",
        "genre": "Jazz",
        "mood": "calm",
        "themes": ["peace", "Love", "life"]
    },
    {
        "title": "Wildflower",
        "artist": "Billie Elish",
        "genre": "Melody",
        "mood": "sad",
        "themes": ["friendship", "Love", "Guilt"]
    }
]


def search_music(mood=None, genre=None, theme=None):
    """Search for songs using flexible preference matching."""

    # Synonyms / related concepts
    mood_map = {
        "sad": "melancholic",
        "depressing": "melancholic",
        "emotional": "melancholic",
        "low": "melancholic",
        "peaceful": "calm",
        "joyful": "happy"
    }

    theme_map = {
        "introspection": "self-reflection",
        "introspective": "self-reflection",
        "self reflection": "self-reflection",
        "meaningful lyrics": "self-reflection",
        "deep lyrics": "self-reflection",
        "identity": "identity",
        "feeling alone": "loneliness",
        "being alone": "loneliness"
    }

    if mood:
        mood = mood_map.get(
            mood.lower(),
            mood.lower()
        )

    if theme:
        theme = theme_map.get(
            theme.lower(),
            theme.lower()
        )

    results = []

    for song in music_database:

        # Match mood
        if mood and song["mood"].lower() != mood:
            continue

        # Match genre
        if genre and song["genre"].lower() != genre.lower():
            continue

        # Match theme
        if theme:
            song_themes = [
                t.lower()
                for t in song["themes"]
            ]

            if theme not in song_themes:
                continue

        results.append(song)

    return results


def analyze_song(title):
    """Analyze a song and return its characteristics."""

    for song in music_database:

        if song["title"].lower() == title.lower():
            return {
                "title": song["title"],
                "artist": song["artist"],
                "genre": song["genre"],
                "mood": song["mood"],
                "themes": song["themes"]
            }

    return {
        "error": f"Song '{title}' was not found."
    }