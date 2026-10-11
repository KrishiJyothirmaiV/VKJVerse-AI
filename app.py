
import os
import sqlite3
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv
from ai_assistant import ask_drama_assistant

# ==========================================
# VKJVERSE AI - PURPLE CUTE EDITION
# ==========================================

load_dotenv()

st.set_page_config(
    page_title="VKJVerse AI | Your Drama Universe",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)

TMDB_TOKEN = os.getenv("TMDB_READ_TOKEN", "").strip()
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_URL = "https://image.tmdb.org/t/p/w500"
DB_PATH = Path(__file__).resolve().parent / "vkjverse_watchlist.db"

# ==========================================
# PURPLE THEME + CUTE FONTS
# ==========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Quicksand:wght@400;500;600;700&display=swap');

html, body, .stApp {
    font-family: 'Quicksand', sans-serif !important;
    color: #F5EEFF;
}

.stApp {
    background:
        radial-gradient(
            ellipse at 90% 0%,
            rgba(135, 75, 208, 0.20),
            transparent 43%
        ),
        linear-gradient(
            135deg,
            #10091E 0%,
            #190F2B 55%,
            #10091E 100%
        );
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4,
.vkj-hero-title,
.vkj-eyebrow {
    font-family: 'Fredoka', sans-serif !important;
}

h1, h2, h3 {
    color: #E3C7FF !important;
    letter-spacing: 0.2px !important;
}

h1 {
    font-size: clamp(2rem, 4vw, 3rem) !important;
}

h2 {
    font-size: 1.8rem !important;
    margin-top: 1.5rem !important;
}

p, label, input, textarea, button,
[data-testid="stMarkdownContainer"] {
    font-family: 'Quicksand', sans-serif !important;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #29173F 0%,
        #150C24 100%
    );
    border-right: 1px solid #50336F;
}

/* SIDEBAR NAVIGATION - CORRECTED */

section[data-testid="stSidebar"] [role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 4px !important;
    width: 100% !important;
}

section[data-testid="stSidebar"] [role="radiogroup"] label {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: flex-start !important;
    width: 100% !important;
    padding: 10px 8px !important;
    border-radius: 12px !important;
    gap: 8px !important;
}

section[data-testid="stSidebar"] [role="radiogroup"] label p {
    margin: 0 !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    font-size: 14px !important;
}

section[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {
    flex-shrink: 0 !important;
}

/* INPUTS */

div[data-baseweb="input"],
div[data-baseweb="select"] > div {
    background-color: #28193C !important;
    border: 1px solid #68468B !important;
    border-radius: 14px !important;
}

input {
    color: #FFFFFF !important;
}

/* BUTTONS */

.stButton > button {
    background: linear-gradient(
        120deg,
        #9D68EC,
        #C6A2FF
    ) !important;
    color: #190D2C !important;
    border: none !important;
    border-radius: 16px !important;
    font-family: 'Fredoka', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.55rem 1rem !important;
    transition: transform 0.2s ease,
                box-shadow 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 7px 24px rgba(173, 122, 249, 0.35);
}

/* MOVIE POSTERS */

div[data-testid="stImage"] img {
    border-radius: 15px;
    transition: transform 0.25s ease;
}

div[data-testid="stImage"] img:hover {
    transform: scale(1.025);
}

/* EXPANDERS */

div[data-testid="stExpander"] {
    background: rgba(43, 26, 65, 0.7);
    border: 1px solid #513670;
    border-radius: 14px;
}

/* ALERTS */

div[data-testid="stAlert"] {
    border-radius: 14px;
}

/* DIVIDERS */

hr {
    border-color: #50336F !important;
}

/* HERO BANNER */

.vkj-hero {
    background:
        radial-gradient(
            circle at 88% 18%,
            rgba(230, 199, 255, 0.20),
            transparent 35%
        ),
        linear-gradient(
            115deg,
            #54288B,
            #30194D 65%,
            #241438
        );
    border: 1px solid #8155B2;
    border-radius: 26px;
    padding: 3rem 2.5rem;
    margin-bottom: 1.8rem;
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.15);
}

.vkj-eyebrow {
    color: #EAD7FF;
    font-size: 0.85rem;
    letter-spacing: 2px;
    font-weight: 500;
}

.vkj-hero-title {
    color: #FFFFFF;
    font-size: clamp(2rem, 4vw, 3.4rem);
    line-height: 1.15;
    font-weight: 600;
    margin: 0.7rem 0;
}

.vkj-hero-subtitle {
    color: #E9DDF5;
    font-size: 1.05rem;
    line-height: 1.8;
    max-width: 750px;
}

/* CATEGORY CHIPS */

.vkj-chips {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 1.3rem;
}

.vkj-chip {
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.20);
    color: #F7EEFF;
    border-radius: 50px;
    padding: 7px 14px;
    font-size: 0.85rem;
    font-weight: 600;
}

.vkj-section-note {
    color: #C6B1DB;
    margin-top: -0.5rem;
    margin-bottom: 1.5rem;
}

.vkj-footer {
    text-align: center;
    color: #BDA9D2;
    font-size: 0.85rem;
    padding: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# TMDB API FUNCTIONS
# ==========================================

@st.cache_data(ttl=1800, show_spinner=False)
def tmdb_request(endpoint, token, params=None):
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json",
    }

    try:
        response = requests.get(
            BASE_URL + endpoint,
            headers=headers,
            params=params or {},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        st.error(f"TMDB request failed: {error}")
        return {}


def get_data(endpoint, params=None):
    if not TMDB_TOKEN:
        return {}

    return tmdb_request(endpoint, TMDB_TOKEN, params)


# ==========================================
# WATCHLIST DATABASE
# ==========================================

def database():
    connection = sqlite3.connect(DB_PATH)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            tmdb_id INTEGER NOT NULL,
            media_type TEXT NOT NULL,
            title TEXT,
            poster TEXT,
            PRIMARY KEY (tmdb_id, media_type)
        )
    """)

    connection.commit()
    return connection


def get_media_type(item):
    media_type = item.get("media_type")

    if media_type in ("movie", "tv"):
        return media_type

    if "title" in item:
        return "movie"

    return "tv"


def add_to_watchlist(item):
    title = (
        item.get("title")
        or item.get("name")
        or "Unknown"
    )

    media_type = get_media_type(item)

    with database() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO watchlist
            (tmdb_id, media_type, title, poster)
            VALUES (?, ?, ?, ?)
        """, (
            item["id"],
            media_type,
            title,
            item.get("poster_path"),
        ))

    st.toast(f"💜 Added {title} to your watchlist!")


# ==========================================
# DISPLAY MOVIE AND DRAMA CARDS
# ==========================================

def display_titles(items, section_key):
    if not items:
        st.info("No titles found. Try another search!")
        return

    items = items[:24]

    for start in range(0, len(items), 4):
        columns = st.columns(4, gap="medium")

        for offset, item in enumerate(items[start:start + 4]):
            index = start + offset

            with columns[offset]:
                poster = item.get("poster_path")

                if poster:
                    st.image(
                        IMAGE_URL + poster,
                        use_container_width=True,
                    )
                else:
                    st.caption("🎞️ Poster unavailable")

                title = (
                    item.get("title")
                    or item.get("name")
                    or "Unknown title"
                )

                rating = item.get("vote_average") or 0

                release_date = (
                    item.get("release_date")
                    or item.get("first_air_date")
                    or "Unknown"
                )

                st.markdown(f"**{title}**")
                st.caption(
                    f"⭐ {rating:.1f}/10 · 📅 {release_date}"
                )

                with st.expander("💜 About this title"):
                    st.write(
                        item.get("overview")
                        or "No description available."
                    )

                if st.button(
                    "♡ Add to Watchlist",
                    key=f"{section_key}_{index}_{item['id']}",
                    use_container_width=True,
                ):
                    add_to_watchlist(item)


# ==========================================
# HERO BANNER
# ==========================================

st.markdown("""
<div class="vkj-hero">
    <div class="vkj-eyebrow">
        ✦ WELCOME TO VKJVERSE AI ✦
    </div>
    <div class="vkj-hero-title">
        Your Universe of Stories. ♡
    </div>
    <div class="vkj-hero-subtitle">
        Discover your next obsession! From dreamy K-dramas
        and Thai BL/GL series to C-dramas, J-dramas,
        Indian cinema and Hollywood, your favorite
        stories live here.
    </div>
    <div class="vkj-chips">
        <span class="vkj-chip">♡ K-Dramas</span>
        <span class="vkj-chip">✦ C-Dramas</span>
        <span class="vkj-chip">♡ Thai BL/GL</span>
        <span class="vkj-chip">✦ J-Dramas</span>
        <span class="vkj-chip">♡ Global Cinema</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# CHECK TMDB CONNECTION
# ==========================================

if not TMDB_TOKEN:
    st.error(
        "TMDB token not found. Add your API Read "
        "Access Token to the .env file as "
        "TMDB_READ_TOKEN=your_token, then restart."
    )
    st.stop()


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.markdown("## 💜 VKJVerse AI")
st.sidebar.caption("Your cozy corner of entertainment ✨")

page = st.sidebar.radio(
    "Explore your universe",
    [
        "🏠 Home",
        "🔥 Trending",
        "🔎 Search",
        "🌏 World Explorer",
        "📅 Episode Radar",
        "🤖 Recommendations",
        "❤️ My Watchlist",
        "💬 AI Drama Assistant",
    ],
)

st.sidebar.divider()
st.sidebar.caption("Made for drama lovers ♡")


# ==========================================
# HOME
# ==========================================

if page == "🏠 Home":
    st.header("🔥 Trending This Week")

    st.markdown(
        '<div class="vkj-section-note">'
        'The stories everyone is talking about ✨'
        '</div>',
        unsafe_allow_html=True,
    )

    trending = get_data("/trending/all/week")
    display_titles(
        trending.get("results", []),
        "home_trending",
    )

    st.header("💜 Popular TV Series")

    popular = get_data(
        "/tv/popular",
        {
            "language": "en-US",
            "page": 1,
        },
    )

    display_titles(
        popular.get("results", [])[:8],
        "home_popular",
    )


# ==========================================
# TRENDING
# ==========================================

elif page == "🔥 Trending":
    st.header("🔥 What's Trending?")

    category = st.selectbox(
        "Choose your category",
        ["All", "Movies", "TV Series"],
    )

    period = st.selectbox(
        "Trending period",
        ["Today", "This Week"],
    )

    media_map = {
        "All": "all",
        "Movies": "movie",
        "TV Series": "tv",
    }

    period_code = (
        "day" if period == "Today"
        else "week"
    )

    data = get_data(
        f"/trending/{media_map[category]}/{period_code}"
    )

    display_titles(
        data.get("results", []),
        "trending",
    )


# ==========================================
# SEARCH
# ==========================================

elif page == "🔎 Search":
    st.header("🔎 Find Your Next Favorite")

    query = st.text_input(
        "Search movies and dramas",
        placeholder="Lovely Runner, The Untamed, 2gether...",
    )

    if query.strip():
        results = get_data(
            "/search/multi",
            {
                "query": query.strip(),
                "include_adult": "false",
            },
        )

        titles = [
            item
            for item in results.get("results", [])
            if item.get("media_type") in ("movie", "tv")
        ]

        st.caption(
            f"Showing {len(titles)} results from this page"
        )

        display_titles(titles, "search")

    else:
        st.info("💜 Search for something you love!")


# ==========================================
# WORLD EXPLORER
# ==========================================

elif page == "🌏 World Explorer":
    st.header("🌏 Around the World")

    countries = {
        "🇰🇷 South Korea": "KR",
        "🇨🇳 China": "CN",
        "🇯🇵 Japan": "JP",
        "🇹🇭 Thailand": "TH",
        "🇮🇳 India": "IN",
        "🇹🇼 Taiwan": "TW",
        "🇵🇭 Philippines": "PH",
        "🇺🇸 United States": "US",
        "🇬🇧 United Kingdom": "GB",
        "🇹🇷 Turkey": "TR",
    }

    country = st.selectbox(
        "Pick a country",
        list(countries.keys()),
    )

    content_type = st.radio(
        "What would you like to explore?",
        ["TV Series", "Movies"],
        horizontal=True,
    )

    media_type = (
        "tv" if content_type == "TV Series"
        else "movie"
    )

    data = get_data(
        f"/discover/{media_type}",
        {
            "with_origin_country": countries[country],
            "sort_by": "popularity.desc",
            "include_adult": "false",
            "page": 1,
        },
    )

    st.caption(
        "Titles are ordered by TMDB popularity."
    )

    display_titles(
        data.get("results", []),
        "world",
    )

    st.info(
        "Dedicated BL/GL filtering is planned "
        "for a future update."
    )


# ==========================================
# EPISODE RADAR
# ==========================================

elif page == "📅 Episode Radar":
    st.header("📅 Episode Radar")

    st.write(
        "Find out when the next episode of your "
        "favorite drama is scheduled!"
    )

    drama_name = st.text_input(
        "Search a TV series",
        placeholder="Enter an ongoing drama",
    )

    if drama_name.strip():
        results = get_data(
            "/search/tv",
            {"query": drama_name.strip()},
        )

        shows = results.get("results", [])[:15]

        if shows:
            selected = st.selectbox(
                "Choose your drama",
                range(len(shows)),
                format_func=lambda i: (
                    f"{shows[i].get('name', 'Unknown')} "
                    f"({(shows[i].get('first_air_date') or 'Unknown')[:4]})"
                ),
            )

            show = shows[selected]
            details = get_data(f"/tv/{show['id']}")

            st.subheader(
                details.get("name", "TV Series")
            )

            if details.get("poster_path"):
                st.image(
                    IMAGE_URL + details["poster_path"],
                    width=230,
                )

            st.write(
                details.get("overview")
                or "Description unavailable."
            )

            next_episode = details.get(
                "next_episode_to_air"
            )

            if next_episode:
                st.success(
                    f"💜 Season "
                    f"{next_episode.get('season_number')} "
                    f"Episode "
                    f"{next_episode.get('episode_number')}"
                )

                st.write(
                    "📅 Release date:",
                    next_episode.get("air_date")
                    or "Unknown",
                )

                st.write(
                    "Episode title:",
                    next_episode.get("name")
                    or "Not available",
                )

            else:
                st.warning(
                    "TMDB does not currently list "
                    "an upcoming episode."
                )

            last_episode = details.get(
                "last_episode_to_air"
            )

            if last_episode:
                st.caption(
                    "Last listed episode: "
                    f"S{last_episode.get('season_number')} "
                    f"E{last_episode.get('episode_number')} "
                    f"— {last_episode.get('air_date') or 'Unknown'}"
                )

        else:
            st.info("No matching series found.")


# ==========================================
# RECOMMENDATIONS
# ==========================================

elif page == "🤖 Recommendations":
    st.header("🤖 Your Next Obsession")

    st.write(
        "Tell us a movie or drama you love, "
        "and we'll find similar titles!"
    )

    favorite = st.text_input(
        "Your favorite title",
        placeholder="Crash Landing on You",
    )

    if favorite.strip():
        results = get_data(
            "/search/multi",
            {
                "query": favorite.strip(),
                "include_adult": "false",
            },
        )

        matches = [
            item
            for item in results.get("results", [])
            if item.get("media_type") in ("movie", "tv")
        ][:12]

        if matches:
            selected = st.selectbox(
                "Choose the correct title",
                range(len(matches)),
                format_func=lambda i: (
                    matches[i].get("title")
                    or matches[i].get("name")
                    or "Unknown"
                ),
            )

            chosen = matches[selected]
            media_type = get_media_type(chosen)

            recommendations = get_data(
                f"/{media_type}/{chosen['id']}/recommendations"
            )

            st.subheader("♡ You might also love")

            display_titles(
                recommendations.get("results", []),
                "recommendations",
            )

            st.caption(
                "Recommendations are powered by TMDB "
                "similarity data, not a generative AI model."
            )

        else:
            st.info("No matching titles found.")


# ==========================================
# MY WATCHLIST
# ==========================================

elif page == "❤️ My Watchlist":
    st.header("❤️ My Little Watchlist")

    st.write(
        "All the stories you've saved in one place ♡"
    )

    with database() as conn:
        saved_items = conn.execute("""
            SELECT tmdb_id, media_type, title, poster
            FROM watchlist
            ORDER BY title
        """).fetchall()

    if not saved_items:
        st.info(
            "Your watchlist is empty. "
            "Start adding your favorite titles!"
        )

    for tmdb_id, media_type, title, poster in saved_items:
        col1, col2, col3 = st.columns([1, 4, 2])

        with col1:
            if poster:
                st.image(
                    IMAGE_URL + poster,
                    width=90,
                )

        with col2:
            st.markdown(f"**{title}**")
            st.caption(media_type.upper())

        with col3:
            if st.button(
                "Remove ♡",
                key=f"remove_{media_type}_{tmdb_id}",
            ):
                with database() as conn:
                    conn.execute("""
                        DELETE FROM watchlist
                        WHERE tmdb_id = ?
                        AND media_type = ?
                    """, (tmdb_id, media_type))

                st.rerun()


# ==========================================
# AI DRAMA ASSISTANT - UPDATED ERROR HANDLING
# ==========================================

elif page == "💬 AI Drama Assistant":
    st.header("💬 VKJVerse AI Drama Assistant")

    st.caption(
        "Your personal AI companion for discovering "
        "movies and dramas around the world 💜"
    )

    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []

    for message in st.session_state.ai_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input(
        "Ask me about K-dramas, C-dramas, BL/GL, movies..."
    )

    if user_prompt:
        st.session_state.ai_chat_history.append(
            {"role": "user", "content": user_prompt}
        )

        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Finding your next obsession... 💜"):
                try:
                    answer = ask_drama_assistant(user_prompt)

                except Exception as error:
                    if (
                        "503" in str(error)
                        or "UNAVAILABLE" in str(error)
                    ):
                        st.warning(
                            "💜 Gemini is currently experiencing "
                            "high demand. Please try again "
                            "in a few minutes."
                        )
                    else:
                        st.error(
                            "The AI request failed. "
                            "Please check your API configuration."
                        )

                    answer = None

            if answer:
                st.markdown(answer)

                st.session_state.ai_chat_history.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.markdown("""
<div class="vkj-footer">
    💜 VKJVerse AI · Your cozy entertainment universe ♡
    <br>
    This product uses the TMDB API but is not
    endorsed or certified by TMDB.
</div>
""", unsafe_allow_html=True)