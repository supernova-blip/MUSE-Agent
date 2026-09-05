import json

from google import genai
from google.genai import types
from dotenv import load_dotenv

from tools import search_music, analyze_song
from memory import (
    get_preferences,
    remember_preference
)


# ==========================================
# LOAD API KEY
# ==========================================

load_dotenv()

client = genai.Client()


# ==========================================
# TOOL FUNCTIONS
# ==========================================

def search_music_tool(
    mood: str = None,
    genre: str = None,
    theme: str = None
):
    """Search the music database."""

    print("\n[ACTION] search_music")

    print(
        f"[ARGUMENTS] mood={mood}, "
        f"genre={genre}, theme={theme}"
    )

    result = search_music(
        mood=mood,
        genre=genre,
        theme=theme
    )

    print("[OBSERVATION]")
    print(result)

    return result


def analyze_song_tool(title: str):
    """Analyze a song."""

    print("\n[ACTION] analyze_song")

    print(f"[ARGUMENTS] title={title}")

    result = analyze_song(title)

    print("[OBSERVATION]")
    print(result)

    return result


def remember_preference_tool(
    category: str,
    value: str
):
    """Store a user's music preference."""

    print("\n[ACTION] remember_preference")

    print(
        f"[ARGUMENTS] category={category}, "
        f"value={value}"
    )

    result = remember_preference(
        category,
        value
    )

    print("[OBSERVATION]")
    print(result)

    return result


def get_memory_tool():
    """Retrieve the user's long-term music memory."""

    print("\n[ACTION] get_memory")

    result = get_preferences()

    print("[OBSERVATION]")
    print(result)

    return result


# ==========================================
# TOOL DECLARATIONS
# ==========================================

search_music_declaration = types.FunctionDeclaration(
    name="search_music",
    description=(
        "Search the user's music database using "
        "mood, genre, or lyrical theme."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "mood": {
                "type": "string",
                "description": (
                    "Mood such as melancholic, "
                    "happy, or calm."
                )
            },
            "genre": {
                "type": "string",
                "description": (
                    "Genre such as K-pop, "
                    "Indie, or Pop."
                )
            },
            "theme": {
                "type": "string",
                "description": (
                    "Theme such as loneliness, "
                    "self-reflection, identity, "
                    "love, or life."
                )
            }
        }
    }
)


analyze_song_declaration = types.FunctionDeclaration(
    name="analyze_song",
    description=(
        "Analyze a song in the music database "
        "and return its characteristics."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The song title."
            }
        },
        "required": ["title"]
    }
)


remember_preference_declaration = types.FunctionDeclaration(
    name="remember_preference",
    description=(
        "Store a user's music preference in "
        "long-term memory."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": (
                    "Preference category: genres, "
                    "moods, artists, or themes."
                )
            },
            "value": {
                "type": "string",
                "description": (
                    "The preference value to remember."
                )
            }
        },
        "required": ["category", "value"]
    }
)


get_memory_declaration = types.FunctionDeclaration(
    name="get_memory",
    description=(
        "Retrieve the user's stored music "
        "preferences and listening history."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {}
    }
)


# ==========================================
# TOOL MAP
# ==========================================

TOOL_FUNCTIONS = {
    "search_music": search_music_tool,
    "analyze_song": analyze_song_tool,
    "remember_preference": remember_preference_tool,
    "get_memory": get_memory_tool
}


MUSE_TOOL = types.Tool(
    function_declarations=[
        search_music_declaration,
        analyze_song_declaration,
        remember_preference_declaration,
        get_memory_declaration
    ]
)


# ==========================================
# RUN MUSE AGENT
# ==========================================

def run_agent(user_input):

    print("\n===================================")
    print("        MUSE AGENT STARTED")
    print("===================================")

    # --------------------------------------
    # LOAD LONG-TERM MEMORY
    # --------------------------------------

    memory = get_preferences()

    print("\n[MEMORY]")
    print(memory)

    # --------------------------------------
    # SYSTEM INSTRUCTIONS
    # --------------------------------------

    system_instruction = f"""
You are Muse, a personalized music discovery agent.

Your purpose is to help users discover music based
on their preferences, emotions, and interests.

You have access to these tools:

1. get_memory
   - Retrieve the user's long-term music memory.

2. search_music
   - Search the music database.

3. analyze_song
   - Analyze a specific song.

4. remember_preference
   - Store a new user preference.

CURRENT LONG-TERM MEMORY:

{json.dumps(memory, indent=2)}

AGENT BEHAVIOR:

- Understand the user's request naturally.

- Use the user's stored memory when making
  personalized recommendations.

- If the user explicitly states a NEW preference,
  use remember_preference.

- If the user asks about a specific song,
  use analyze_song when appropriate.

- Use search_music when the user wants a
  recommendation.

- Do not invent songs that are not returned
  by search_music.

- Prefer a single well-targeted search.

- Do not repeatedly search using many slightly
  different combinations.

- If a search returns no results, work with the
  available information instead of repeatedly
  calling the search tool.

- Give a useful final response after receiving
  tool results.

- Do not reveal private chain-of-thought.

The current memory is already available above.
Do not call get_memory unless you specifically
need to retrieve it again.
"""

    # --------------------------------------
    # CONVERSATION CONTENT
    # --------------------------------------

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=user_input
                )
            ]
        )
    ]

    # --------------------------------------
    # REACT LOOP
    # --------------------------------------

    MAX_ITERATIONS = 2

    for iteration in range(MAX_ITERATIONS):

        print(
            f"\n[AGENT ITERATION "
            f"{iteration + 1}/{MAX_ITERATIONS}]"
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[MUSE_TOOL],
                automatic_function_calling=(
                    types.AutomaticFunctionCallingConfig(
                        disable=True
                    )
                )
            )
        )

        # ----------------------------------
        # CHECK FOR FUNCTION CALL
        # ----------------------------------

        if not response.function_calls:

            print("\n===================================")
            print("           FINAL RESPONSE")
            print("===================================")

            return response.text

        # ----------------------------------
        # ADD GEMINI RESPONSE TO HISTORY
        # ----------------------------------

        contents.append(
            response.candidates[0].content
        )

        # ----------------------------------
        # EXECUTE FUNCTION CALLS
        # ----------------------------------

        function_response_parts = []

        for function_call in response.function_calls:

            function_name = function_call.name
            arguments = dict(function_call.args)

            print(
                f"\n[LLM DECISION] "
                f"{function_name}"
            )

            if function_name not in TOOL_FUNCTIONS:

                result = {
                    "error":
                    f"Unknown tool: {function_name}"
                }

            else:

                try:

                    function_to_call = (
                        TOOL_FUNCTIONS[function_name]
                    )

                    result = function_to_call(
                        **arguments
                    )

                except Exception as e:

                    result = {
                        "error": str(e)
                    }

            # ----------------------------------
            # SEND TOOL RESULT BACK TO GEMINI
            # ----------------------------------

            function_response_parts.append(
                types.Part.from_function_response(
                    name=function_name,
                    response={
                        "result": result
                    }
                )
            )

        contents.append(
            types.Content(
                role="tool",
                parts=function_response_parts
            )
        )

    # --------------------------------------
    # MAX ITERATIONS REACHED
    # --------------------------------------

    print("\n[MAX ITERATIONS REACHED]")

    return (
        "I found some information, but I couldn't "
        "complete the recommendation within the "
        "agent's tool limit."
    )