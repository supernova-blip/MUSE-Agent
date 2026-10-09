
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
        "themes": ["peace", "love", "life"]
    },
    {
        "title": "Wildflower",
        "artist": "Billie Elish",
        "genre": "Melody",
        "mood": "sad",
        "themes": ["friendship", "love", "guilt"]
    }
    ,
    {
        "title": "The Night We Met",
        "artist": "Lord Huron",
        "genre": "Indie",
        "mood": "melancholic",
        "themes": ["love", "longing", "memories", "regret"]
    }
]


def search_music(mood=None, genre=None, theme=None, preferences=None):
    """Find and rank songs by request and saved preferences."""

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
        "feeling alone": "loneliness",
        "being alone": "loneliness"
    }

    mood = mood_map.get(mood.lower(), mood.lower()) if mood else None
    theme = theme_map.get(theme.lower(), theme.lower()) if theme else None
    genre = genre.lower().strip() if genre else None

    preferences = preferences or {}
    preferred_genres = [
        item.lower() for item in preferences.get("genres", [])
    ]
    preferred_moods = [
        item.lower() for item in preferences.get("moods", [])
    ]
    preferred_artists = [
        item.lower() for item in preferences.get("artists", [])
    ]
    preferred_themes = [
        item.lower() for item in preferences.get("themes", [])
    ]

    results = []

    for song in music_database:
        song_genre = song["genre"].lower()
        song_mood = song["mood"].lower()
        song_artist = song["artist"].lower()
        song_themes = [item.lower() for item in song["themes"]]

        # Requested mood and genre remain strict filters.
        if mood and song_mood != mood:
            continue
        if genre and song_genre != genre:
            continue

        # A theme can match any related theme rather than only one exact phrase.
        if theme and theme not in song_themes:
            related = theme_map.get(theme)
            if not related or related not in song_themes:
                continue

        # Rank matching songs using the user's saved preferences.
        score = 0

        if song_genre in preferred_genres:
            score += 3
        if song_mood in preferred_moods:
            score += 2
        if song_artist in preferred_artists:
            score += 4
        score += sum(
            2 for preferred_theme in preferred_themes
            if preferred_theme in song_themes
        )

        results.append((score, song))

    # Best personalization matches appear first.
    results.sort(key=lambda item: item[0], reverse=True)

    return [song for score, song in results]


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

    return {"error": f"Song '{title}' was not found."}