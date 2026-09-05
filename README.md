# Muse: An Agentic AI for Personalized Music Discovery

Muse is an Agentic AI system designed to provide personalized music discovery based on a user's musical preferences, moods, themes, and listening history.

Unlike a traditional recommendation system, Muse uses an LLM-powered agent that interprets the user's request, decides which tool to use, executes the tool, observes its result, and generates a personalized response.

## Key Features

- LLM-powered music discovery agent
- Tool calling for music search and song analysis
- Persistent user memory
- ReAct-style reasoning and action loop
- Mood, genre, and theme-based music search
- Individual song analysis
- Persistent storage of user preferences
- Conversational CLI interface

## System Architecture

```text
                         +------------------+
                         |       USER       |
                         +--------+---------+
                                  |
                                  v
                         +------------------+
                         |    MUSE AGENT    |
                         |    Gemini LLM    |
                         +--------+---------+
                                  |
                         ReAct-style Loop
                                  |
                  +---------------+---------------+
                  |                               |
                  v                               v
          +---------------+               +---------------+
          |     TOOLS     |               |    MEMORY     |
          +---------------+               +---------------+
          | search_music  |               | Preferences  |
          | analyze_song  |               | Liked Songs  |
          | remember_     |               | Disliked     |
          | preference    |               | Songs        |
          | get_memory    |               +---------------+
          +-------+-------+
                  |
                  v
          +---------------+
          | Music Database|
          +---------------+
