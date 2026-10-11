
import os
import time
import requests

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

load_dotenv()

TMDB_TOKEN = os.getenv("TMDB_READ_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

TMDB_BASE_URL = "https://api.themoviedb.org/3"
GEMINI_MODEL = "gemini-3.5-flash-lite"


def search_dramas(query):
    """Search TMDB for real movies and TV shows."""

    if not TMDB_TOKEN:
        raise ValueError(
            "TMDB_READ_TOKEN is missing from .env"
        )

    response = requests.get(
        f"{TMDB_BASE_URL}/search/multi",
        headers={
            "Authorization": f"Bearer {TMDB_TOKEN}",
            "accept": "application/json",
        },
        params={
            "query": query,
            "include_adult": "false",
        },
        timeout=20,
    )

    response.raise_for_status()

    results = response.json().get("results", [])

    return [
        {
            "id": item["id"],
            "title": item.get("name") or item.get("title"),
            "type": item.get("media_type"),
            "overview": item.get("overview", ""),
            "rating": item.get("vote_average"),
            "release_date": (
                item.get("first_air_date")
                or item.get("release_date")
            ),
        }
        for item in results
        if item.get("media_type") in ("tv", "movie")
    ][:10]


def generate_with_retry(client, model, contents):
    """Retry temporary Gemini server failures."""

    for attempt in range(3):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
            )

        except ServerError as error:
            if error.code not in (500, 502, 503, 504):
                raise

            if attempt == 2:
                raise

            wait_seconds = 2 ** (attempt + 1)
            time.sleep(wait_seconds)


def ask_drama_assistant(user_message):
    """Understand user requests and recommend real TMDB titles."""

    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is missing from .env"
        )

    client = genai.Client(api_key=GEMINI_API_KEY)

    # STEP 1: Understand the user's request
    query_response = generate_with_retry(
        client=client,
        model=GEMINI_MODEL,
        contents=(
            "Convert this entertainment request into ONE "
            "short movie or TV title search query suitable "
            "for TMDB. Return only the query, with no "
            "explanation. If the request contains a specific "
            "movie or drama title, return that title. "
            f"Request: {user_message}"
        ),
    )

    search_query = (query_response.text or "").strip()

    if not search_query:
        return (
            "I couldn't understand the search request. "
            "Please try again."
        )

    # STEP 2: Search TMDB
    dramas = search_dramas(search_query)

    if not dramas:
        return (
            "I couldn't find matching titles in TMDB. "
            "Try mentioning a specific drama or movie title."
        )

    # STEP 3: Generate recommendations
    answer_response = generate_with_retry(
        client=client,
        model=GEMINI_MODEL,
        contents=(
            "You are VKJVerse AI, a friendly movie and drama "
            "discovery assistant.\n\n"
            f"User request: {user_message}\n\n"
            f"TMDB search results: {dramas}\n\n"
            "Recommend only titles present in the TMDB results. "
            "Explain how each recommendation relates to the "
            "user's preferences. Do not invent ratings, episode "
            "counts, endings, or release information. "
            "If the results don't sufficiently match the "
            "request, explain that limitation. "
            "Use a friendly, concise tone."
        ),
    )

    return (
        answer_response.text
        or "I couldn't generate an answer. Please try again."
    )
