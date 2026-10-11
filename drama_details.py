
"""
VKJVerse AI — Drama Details & Episode Tracker

Provides:
- Drama search
- Drama metadata and genres
- Ongoing/completed/upcoming status
- Episode counts and season information
- Past and future episode air dates
- Next episode countdown
- Episode release calendar
- Cast information
- Actor filmography

Data source: TMDB API
"""

import os
from datetime import date, datetime
from functools import lru_cache

import requests
from dotenv import load_dotenv

load_dotenv()

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

REQUEST_TIMEOUT = 20


# --------------------------------------------------
# 1. TMDB API CONNECTION
# --------------------------------------------------

def tmdb_get(endpoint, params=None):
    """Make an authenticated TMDB API request."""

    token = os.getenv("TMDB_READ_TOKEN", "").strip()

    if not token:
        raise ValueError(
            "TMDB_READ_TOKEN is missing from your .env file."
        )

    response = requests.get(
        f"{TMDB_BASE_URL}{endpoint}",
        headers={
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
        },
        params=params or {},
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()
    return response.json()


# --------------------------------------------------
# 2. HELPER FUNCTIONS
# --------------------------------------------------

def parse_air_date(value):
    """Convert YYYY-MM-DD into a Python date."""

    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def image_url(path):
    """Return a complete TMDB image URL."""

    if not path:
        return None

    return f"{TMDB_IMAGE_URL}{path}"


def get_genre_names(details):
    """Extract genre names from drama details."""

    return [
        genre.get("name", "Unknown")
        for genre in details.get("genres", [])
    ]


def get_country_names(details):
    """Extract countries of origin."""

    return details.get("origin_country", [])


def get_network_names(details):
    """Extract broadcasting or streaming networks."""

    return [
        network.get("name", "Unknown")
        for network in details.get("networks", [])
    ]


# --------------------------------------------------
# 3. SEARCH FOR DRAMAS
# --------------------------------------------------

def search_tv_series(query, page=1):
    """Search for television series by title."""

    if not query or not query.strip():
        return []

    data = tmdb_get(
        "/search/tv",
        {
            "query": query.strip(),
            "page": page,
            "include_adult": "false",
        },
    )

    return data.get("results", [])


# --------------------------------------------------
# 4. DRAMA DETAILS
# --------------------------------------------------

def get_drama_details(series_id):
    """Get full drama details from TMDB."""

    return tmdb_get(f"/tv/{int(series_id)}")


def get_drama_status(details):
    """
    Convert TMDB's status into a simpler category.

    TMDB examples:
    - Returning Series
    - Ended
    - Canceled
    - In Production
    - Planned
    - Pilot
    """

    status = details.get("status", "Unknown")

    status_mapping = {
        "Returning Series": "Ongoing / Returning",
        "Ended": "Completed",
        "Canceled": "Canceled",
        "In Production": "In Production",
        "Planned": "Upcoming / Planned",
        "Pilot": "Pilot",
    }

    return status_mapping.get(status, status)


def get_drama_summary(series_id):
    """
    Return a simplified drama profile for the UI.
    """

    details = get_drama_details(series_id)

    return {
        "id": details.get("id"),
        "title": details.get("name", "Unknown"),
        "original_title": details.get("original_name"),
        "overview": details.get("overview"),
        "status": get_drama_status(details),
        "original_status": details.get("status"),
        "genres": get_genre_names(details),
        "countries": get_country_names(details),
        "language": details.get("original_language"),
        "networks": get_network_names(details),
        "rating": details.get("vote_average"),
        "vote_count": details.get("vote_count"),
        "first_air_date": details.get("first_air_date"),
        "last_air_date": details.get("last_air_date"),
        "total_seasons": details.get("number_of_seasons"),
        "total_episodes": details.get("number_of_episodes"),
        "episode_runtime": details.get("episode_run_time", []),
        "poster_url": image_url(details.get("poster_path")),
        "backdrop_url": image_url(details.get("backdrop_path")),
        "next_episode": details.get("next_episode_to_air"),
        "last_episode": details.get("last_episode_to_air"),
        "seasons": details.get("seasons", []),
        "raw_details": details,
    }


# --------------------------------------------------
# 5. SEASONS AND EPISODES
# --------------------------------------------------

def get_drama_seasons(series_id):
    """
    Return normal seasons, excluding Season 0 specials.
    """

    details = get_drama_details(series_id)

    seasons = details.get("seasons", [])

    return sorted(
        [
            season
            for season in seasons
            if season.get("season_number", 0) > 0
        ],
        key=lambda season: season["season_number"],
    )


def get_season_episodes(series_id, season_number):
    """
    Fetch all listed episodes for one season.
    """

    data = tmdb_get(
        f"/tv/{int(series_id)}/season/{int(season_number)}"
    )

    return data.get("episodes", [])


def get_all_episodes(series_id, include_specials=False):
    """
    Collect episode details from all seasons.

    Each episode includes:
    - Season number
    - Episode number
    - Title
    - Original air date
    - Summary
    - Runtime
    - Rating
    - Still image
    """

    details = get_drama_details(series_id)
    seasons = details.get("seasons", [])

    all_episodes = []

    for season in seasons:

        season_number = season.get("season_number")

        if season_number is None:
            continue

        if season_number == 0 and not include_specials:
            continue

        episodes = get_season_episodes(
            series_id,
            season_number,
        )

        for episode in episodes:

            all_episodes.append({
                "id": episode.get("id"),
                "series_id": int(series_id),
                "season_number": season_number,
                "episode_number": episode.get(
                    "episode_number"
                ),
                "title": episode.get("name") or "Untitled",
                "air_date": episode.get("air_date"),
                "overview": episode.get("overview") or "",
                "runtime": episode.get("runtime"),
                "rating": episode.get("vote_average"),
                "still_url": image_url(
                    episode.get("still_path")
                ),
            })

    return sorted(
        all_episodes,
        key=lambda episode: (
            episode["season_number"],
            episode["episode_number"] or 0,
        ),
    )


# --------------------------------------------------
# 6. PAST AND FUTURE EPISODES
# --------------------------------------------------

def get_released_episodes(series_id, today=None):
    """Return episodes that have already aired."""

    today = today or date.today()

    episodes = get_all_episodes(series_id)

    return [
        episode
        for episode in episodes
        if (
            parse_air_date(episode["air_date"]) is not None
            and parse_air_date(episode["air_date"]) <= today
        )
    ]


def get_upcoming_episodes(series_id, today=None):
    """
    Return future episodes with known air dates.

    Episodes without a published date cannot be
    placed on a release calendar.
    """

    today = today or date.today()

    episodes = get_all_episodes(series_id)

    upcoming = [
        episode
        for episode in episodes
        if (
            parse_air_date(episode["air_date"]) is not None
            and parse_air_date(episode["air_date"]) > today
        )
    ]

    return sorted(
        upcoming,
        key=lambda episode: (
            episode["air_date"],
            episode["season_number"],
            episode["episode_number"] or 0,
        ),
    )


def get_unscheduled_episodes(series_id):
    """
    Return listed episodes without a confirmed date.
    """

    episodes = get_all_episodes(series_id)

    return [
        episode
        for episode in episodes
        if not parse_air_date(episode["air_date"])
    ]


# --------------------------------------------------
# 7. NEXT EPISODE AND COUNTDOWN
# --------------------------------------------------

def get_next_episode(series_id, today=None):
    """
    Find the next scheduled episode.

    Uses TMDB's next_episode_to_air first when its
    date is in the future, otherwise checks season
    episode data.
    """

    today = today or date.today()

    details = get_drama_details(series_id)

    next_episode = details.get("next_episode_to_air")

    if next_episode:
        air_date = parse_air_date(
            next_episode.get("air_date")
        )

        if air_date and air_date > today:
            return {
                "season_number": next_episode.get(
                    "season_number"
                ),
                "episode_number": next_episode.get(
                    "episode_number"
                ),
                "title": next_episode.get("name"),
                "air_date": next_episode.get("air_date"),
                "days_until_release": (
                    air_date - today
                ).days,
            }

    upcoming = get_upcoming_episodes(
        series_id,
        today=today,
    )

    if not upcoming:
        return None

    next_item = upcoming[0]

    air_date = parse_air_date(
        next_item["air_date"]
    )

    return {
        **next_item,
        "days_until_release": (
            air_date - today
        ).days,
    }


# --------------------------------------------------
# 8. EPISODE RELEASE CALENDAR
# --------------------------------------------------

def get_episode_calendar(series_id, today=None):
    """
    Group upcoming episodes by original air date.

    Example:
    {
        "2026-10-15": [
            {
                "season_number": 1,
                "episode_number": 7,
                ...
            }
        ]
    }
    """

    episodes = get_upcoming_episodes(
        series_id,
        today=today,
    )

    calendar = {}

    for episode in episodes:

        air_date = episode["air_date"]

        calendar.setdefault(
            air_date, []
        ).append(episode)

    return calendar


# --------------------------------------------------
# 9. CAST AND ACTORS
# --------------------------------------------------

def get_drama_cast(series_id):
    """Return cast members and their character names."""

    data = tmdb_get(
        f"/tv/{int(series_id)}/credits"
    )

    return data.get("cast", [])


def get_actor_details(person_id):
    """Return actor or actress profile details."""

    return tmdb_get(
        f"/person/{int(person_id)}"
    )


def get_actor_filmography(person_id):
    """
    Return movies and series featuring this actor.
    """

    data = tmdb_get(
        f"/person/{int(person_id)}/combined_credits"
    )

    return sorted(
        data.get("cast", []),
        key=lambda credit: (
            credit.get("popularity") or 0
        ),
        reverse=True,
    )


# --------------------------------------------------
# 10. COMPLETE DRAMA REPORT
# --------------------------------------------------

def get_complete_drama_report(series_id):
    """
    Build a complete report for one drama.

    Useful for:
    - Streamlit Cast Explorer
    - Episode Guide
    - Release Calendar
    - AI recommendations
    """

    summary = get_drama_summary(series_id)

    episodes = get_all_episodes(series_id)

    today = date.today()

    released = []
    upcoming = []
    unscheduled = []

    for episode in episodes:

        air_date = parse_air_date(
            episode["air_date"]
        )

        if air_date is None:
            unscheduled.append(episode)

        elif air_date <= today:
            released.append(episode)

        else:
            upcoming.append(episode)

    upcoming.sort(
        key=lambda episode: episode["air_date"]
    )

    next_episode = get_next_episode(
        series_id,
        today=today,
    )

    return {
        "drama": summary,
        "total_listed_episodes": len(episodes),
        "released_episode_count": len(released),
        "upcoming_episode_count": len(upcoming),
        "unscheduled_episode_count": len(unscheduled),
        "released_episodes": released,
        "upcoming_episodes": upcoming,
        "unscheduled_episodes": unscheduled,
        "next_episode": next_episode,
        "cast": get_drama_cast(series_id),
    }