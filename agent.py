
import json
import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import search_music, analyze_song
from memory import get_preferences, remember_preference


# ==========================================
# CONFIGURATION
# ==========================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY was not found. "
        "Check that your .env file exists."
    )

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.5-flash-lite"
MAX_ITERATIONS = 4


# ==========================================
# GOOGLE SEARCH
# ==========================================

GOOGLE_SEARCH_TOOL = types.Tool(
    google_search=types.GoogleSearch()
)


def should_use_web_search(user_input):
    """Identify requests that need external web information."""

    patterns = [
        r"\blatest\b",
        r"\bcurrent\b",
        r"\bcurrently\b",
        r"\brecent\b",
        r"\bnews\b",
        r"\btoday\b",
        r"\byesterday\b",
        r"\bthis week\b",
        r"\bthis month\b",
        r"\bnew releases?\b",
        r"\breleased recently\b",
        r"\btrending\b",
        r"\bup.to.date\b",
        r"\breal.time\b",
        r"\bsearch the web\b",
        r"\bsearch online\b",
        r"\blook up\b",
        r"\bfind online\b",
        r"\bon the internet\b",
        r"\bsource links?\b",
        r"\breliable sources?\b",
        r"\bcite sources?\b",
        r"\bwith citations?\b",
        r"\bwho is\b",
        r"\bwhat happened\b",
        r"\bwhat are the updates\b",
        r"\bprice of\b",
        r"\bcompare\b",
        r"\bresearch\b",
    ]

    text = user_input.lower()

    return any(re.search(pattern, text) for pattern in patterns)


def extract_sources(response):
    """Extract grounded web sources from Gemini's response."""

    sources = []
    seen_urls = set()

    candidates = getattr(response, "candidates", None) or []

    for candidate in candidates:
        metadata = getattr(
            candidate, "grounding_metadata", None
        )

        if not metadata:
            continue

        chunks = getattr(metadata, "grounding_chunks", None) or []

        for chunk in chunks:
            web_source = getattr(chunk, "web", None)

            if not web_source:
                continue

            url = getattr(web_source, "uri", None)
            title = getattr(web_source, "title", None)

            if url and url not in seen_urls:
                seen_urls.add(url)

                sources.append({
                    "title": title or "Web source",
                    "url": url,
                })

    return sources


def answer_with_web_search(user_input):
    """Answer a web-oriented request using Google Search grounding."""

    print("\n[MODE] Google Search grounding")
    print("[ACTION] Searching the web through Gemini")

    instructions = """
You are Muse, an intelligent music discovery assistant.

Answer the user's request using Google Search grounding.

Requirements:
- Search for current information when requested.
- Prioritize relevant, recent and reliable sources.
- Answer the actual question, not just describe your capabilities.
- Do not invent news, release dates, facts or URLs.
- Distinguish verified facts from opinions and interpretation.
- For music news, identify artists, releases and dates when
  those details can be verified.
- If reliable information cannot be found, say so honestly.
- Keep the answer clear, organized and useful.
- Never claim that you searched if no search was performed.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=user_input,
        config=types.GenerateContentConfig(
            system_instruction=instructions,
            tools=[GOOGLE_SEARCH_TOOL],
        ),
    )

    answer = response.text or (
        "I couldn't generate a text response. Please try again."
    )

    print("\n===================================")
    print("           WEB RESPONSE")
    print("===================================")
    print(answer)

    sources = extract_sources(response)

    if sources:
        print("\nSources:")

        for index, source in enumerate(sources, start=1):
            print(
                f"{index}. {source['title']}\n"
                f"   {source['url']}"
            )
    else:
        print(
            "\n[NOTICE] No source URLs were exposed in the "
            "response's grounding metadata."
        )

    return answer


# ==========================================
# CUSTOM PYTHON TOOLS
# ==========================================


def search_music_tool(
    mood: str = None,
    genre: str = None,
    theme: str = None,
):
    """Search local songs using the user's saved preferences."""

    print("\n[ACTION] search_music")
    print(
        f"[ARGUMENTS] mood={mood}, "
        f"genre={genre}, theme={theme}"
    )

    memory = get_preferences()

    result = search_music(
        mood=mood,
        genre=genre,
        theme=theme,
        preferences=memory.get("preferences", {}),
    )

    print("[OBSERVATION]")
    print(result)

    return result

def analyze_song_tool(title: str):
    """Analyze a song in the existing music database."""

    print("\n[ACTION] analyze_song")
    print(f"[ARGUMENTS] title={title}")

    result = analyze_song(title)

    print("[OBSERVATION]")
    print(result)

    return result


def remember_preference_tool(
    category: str,
    value: str,
):
    """Save a user preference using the existing memory module."""

    print("\n[ACTION] remember_preference")
    print(f"[ARGUMENTS] category={category}, value={value}")

    result = remember_preference(category, value)

    print("[OBSERVATION]")
    print(result)

    return result


def get_memory_tool():
    """Retrieve saved user preferences."""

    print("\n[ACTION] get_memory")

    result = get_preferences()

    print("[OBSERVATION]")
    print(result)

    return result


# ==========================================
# CUSTOM TOOL DECLARATIONS
# ==========================================

search_music_declaration = types.FunctionDeclaration(
    name="search_music",
    description=(
        "Search the available music database by mood, "
        "genre or lyrical theme. Results are limited "
        "to songs present in that database."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "mood": {
                "type": "string",
                "description": "Mood such as melancholic, happy or calm.",
            },
            "genre": {
                "type": "string",
                "description": "Genre such as K-pop, Indie or Pop.",
            },
            "theme": {
                "type": "string",
                "description": (
                    "Theme such as loneliness, self-reflection, "
                    "identity, love or life."
                ),
            },
        },
    },
)

analyze_song_declaration = types.FunctionDeclaration(
    name="analyze_song",
    description=(
        "Retrieve characteristics of a song in the available "
        "music database."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Song title.",
            },
        },
        "required": ["title"],
    },
)

remember_preference_declaration = types.FunctionDeclaration(
    name="remember_preference",
    description="Save a user's music preference.",
    parameters_json_schema={
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": ["genres", "moods", "artists", "themes"],
                "description": "Preference category.",
            },
            "value": {
                "type": "string",
                "description": "Preference value to remember.",
            },
        },
        "required": ["category", "value"],
    },
)

get_memory_declaration = types.FunctionDeclaration(
    name="get_memory",
    description="Retrieve the user's saved music preferences and history.",
    parameters_json_schema={
        "type": "object",
        "properties": {},
    },
)


TOOL_FUNCTIONS = {
    "search_music": search_music_tool,
    "analyze_song": analyze_song_tool,
    "remember_preference": remember_preference_tool,
    "get_memory": get_memory_tool,
}

MUSE_TOOL = types.Tool(
    function_declarations=[
        search_music_declaration,
        analyze_song_declaration,
        remember_preference_declaration,
        get_memory_declaration,
    ]
)


# ==========================================
# CUSTOM-TOOL REACT LOOP
# ==========================================

def answer_with_custom_tools(user_input):
    """Run the existing manual tool-calling loop."""

    print("\n[MODE] Muse custom-tool agent")

    memory = get_preferences()

    print("\n[MEMORY]")
    print(memory)

    system_instruction = f"""
You are Muse, a personalized music discovery agent.

You can use these Python tools:
- search_music: search the available local song database.
- analyze_song: analyze a song in that database.
- get_memory: retrieve saved user preferences.
- remember_preference: save a new user preference.

CURRENT SAVED MEMORY:
{json.dumps(memory, indent=2)}

Rules:
- Use the appropriate tool when needed.
- For recommendations from the local database, only recommend
  songs actually returned by search_music.
- Explain that local song search is limited to its database.
- Never claim the local database contains every song.
- Use get_memory when the user asks what you remember.
- Save explicit new preferences with remember_preference.
- Do not repeatedly call the same tool without a reason.
- Do not invent tool results.
- After receiving tool results, provide a clear final answer.
- Do not reveal private chain-of-thought.
"""

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_input)],
        )
    ]

    for iteration in range(MAX_ITERATIONS):
        print(
            f"\n[AGENT ITERATION {iteration + 1}/{MAX_ITERATIONS}]"
        )

        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[MUSE_TOOL],
                automatic_function_calling=(
                    types.AutomaticFunctionCallingConfig(
                        disable=True
                    )
                ),
            ),
        )

        function_calls = response.function_calls or []

        if not function_calls:
            answer = response.text or (
                "I couldn't generate a response. Please try again."
            )

            print("\n===================================")
            print("           FINAL RESPONSE")
            print("===================================")
            print(answer)

            return answer

        # Preserve the model's function-call message.
        contents.append(response.candidates[0].content)

        function_response_parts = []

        for function_call in function_calls:
            function_name = function_call.name
            arguments = dict(function_call.args or {})

            print(f"\n[LLM DECISION] {function_name}")

            function_to_call = TOOL_FUNCTIONS.get(function_name)

            if function_to_call is None:
                result = {"error": f"Unknown tool: {function_name}"}
            else:
                try:
                    result = function_to_call(**arguments)
                except Exception as exc:
                    print(f"[TOOL ERROR] {exc}")
                    result = {"error": str(exc)}

            # Send the result back to Gemini for the next turn.
            function_response_parts.append(
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": result},
                )
            )

        contents.append(
            types.Content(
                role="user",
                parts=function_response_parts,
            )
        )

    print("\n[MAX ITERATIONS REACHED]")

    return (
        "I couldn't complete the request within the tool-call "
        "limit. Please try a more specific request."
    )


# ==========================================
# PUBLIC AGENT ENTRY POINT
# ==========================================

def run_agent(user_input):
    """Route the user's request to web search or custom tools."""

    user_input = user_input.strip()

    if not user_input:
        return "Please enter a question."

    print("\n===================================")
    print("        MUSE AGENT STARTED")
    print("===================================")

    try:
        if should_use_web_search(user_input):
            return answer_with_web_search(user_input)

        return answer_with_custom_tools(user_input)

    except Exception as exc:
        print(f"\n[ERROR] {type(exc).__name__}: {exc}")

        return (
            "Muse encountered an error while processing your request. "
            "Please check the error above and try again."
        )