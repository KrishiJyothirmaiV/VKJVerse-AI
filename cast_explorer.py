
"""
VKJVerse AI - Enhanced Cast Explorer

TMDB + Wikidata + Wikipedia + Gemini
"""

import streamlit as st

from drama_details import (
    search_tv_series,
    get_drama_details,
    get_drama_cast,
    image_url,
)

from cast_research import (
    build_actor_research,
    generate_ai_career_summary,
)


@st.cache_data(ttl=1800, show_spinner=False)
def cached_search(query):
    return search_tv_series(query)


@st.cache_data(ttl=1800, show_spinner=False)
def cached_details(series_id):
    return get_drama_details(series_id)


@st.cache_data(ttl=1800, show_spinner=False)
def cached_cast(series_id):
    return get_drama_cast(series_id)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_research(person_id):
    return build_actor_research(person_id)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_ai_summary(person_id):
    research = cached_research(person_id)
    return generate_ai_career_summary(research)


def display_project_cards(projects, key_prefix):
    if not projects:
        st.info("No projects listed in TMDB.")
        return

    st.caption(
        f"{len(projects)} unique projects in "
        "the available TMDB cast records."
    )

    limit = st.selectbox(
        "Projects to display",
        [12, 24, 48, 100],
        key=f"{key_prefix}_limit",
    )

    selected = projects[:limit]

    for start in range(0, len(selected), 4):
        columns = st.columns(4)

        for offset, project in enumerate(
            selected[start:start + 4]
        ):
            with columns[offset]:
                poster = image_url(
                    project.get("poster_path")
                )

                if poster:
                    st.image(
                        poster,
                        use_container_width=True,
                    )
                else:
                    st.caption("Poster unavailable")

                st.markdown(
                    f"**{project['title']}**"
                )

                st.caption(
                    f"📅 {project['year'] or 'Unknown year'}"
                )

                original_title = project.get(
                    "original_title"
                )

                if (
                    original_title
                    and original_title != project["title"]
                ):
                    st.caption(original_title)

                if project.get("character"):
                    st.caption(
                        f"🎭 As {project['character']}"
                    )

                st.markdown(
                    f"[View on TMDB]"
                    f"({project['tmdb_url']})"
                )


def show_enhanced_actor_profile(person_id):
    with st.spinner(
        "Researching actor details across sources..."
    ):
        research = cached_research(person_id)

    actor = research["actor"]
    wikidata = research["wikidata"]
    wikipedia = research["wikipedia"]

    st.divider()
    st.header(
        f"💜 {actor.get('name', 'Actor Profile')}"
    )

    photo_col, info_col = st.columns(
        [1, 2],
        gap="large",
    )

    with photo_col:
        photo = image_url(
            actor.get("profile_path")
        )

        if photo:
            st.image(
                photo,
                use_container_width=True,
            )
        else:
            st.info("No profile photo available.")

    with info_col:
        st.subheader("🎭 Personal Details")

        st.write(
            "**Full / Display Name:**",
            actor.get("name") or "Unknown",
        )

        st.write(
            "**Birthday:**",
            actor.get("birthday") or "Not listed",
        )

        st.write(
            "**Birthplace:**",
            actor.get("place_of_birth")
            or "Not listed",
        )

        st.write(
            "**Known For:**",
            actor.get("known_for_department")
            or "Not listed",
        )

        if wikidata.get("name"):
            st.write(
                "**Wikidata Name:**",
                wikidata["name"],
            )

        alternate_names = wikidata.get(
            "alternate_names", []
        )

        if alternate_names:
            st.write(
                "**Other Names:**",
                ", ".join(alternate_names[:12]),
            )

        st.caption(
            "Personal details are primarily from "
            "TMDB. Wikidata names are shown separately."
        )

    # -------------------------------------
    # SOURCE STATUS
    # -------------------------------------

    st.divider()
    st.subheader("🔍 Research Sources")

    if wikidata:
        st.success(
            "Wikidata identity linked through TMDB."
        )
    else:
        st.warning(
            "No linked Wikidata identity found. "
            "Wikipedia information will not be "
            "matched by name alone."
        )

    if wikipedia:
        st.success(
            f"Wikipedia article found "
            f"({wikipedia['language']})."
        )
    else:
        st.info(
            "No matching Wikipedia summary "
            "was retrieved."
        )

    sources = research["sources"]

    st.markdown(
        f"[TMDB Profile]({sources['tmdb']})"
    )

    if sources.get("wikidata"):
        st.markdown(
            f"[Wikidata Record]"
            f"({sources['wikidata']})"
        )

    if sources.get("wikipedia"):
        st.markdown(
            f"[Wikipedia Article]"
            f"({sources['wikipedia']})"
        )

    # -------------------------------------
    # BIOGRAPHIES
    # -------------------------------------

    st.divider()
    st.subheader("📖 Biography & Career")

    tab_tmdb, tab_wiki = st.tabs([
        "🎬 TMDB Biography",
        "🌐 Wikipedia",
    ])

    with tab_tmdb:
        biography = actor.get("biography")

        if biography:
            st.write(biography)
        else:
            st.info(
                "No biography available on TMDB."
            )

    with tab_wiki:
        if wikipedia:
            st.write(wikipedia["summary"])
            st.caption(
                f"Source: Wikipedia "
                f"({wikipedia['language']})"
            )
            st.markdown(
                f"[Read full article]"
                f"({wikipedia['url']})"
            )
        else:
            st.info(
                "No linked Wikipedia article "
                "was retrieved for this actor."
            )

    # -------------------------------------
    # FILMOGRAPHY
    # -------------------------------------

    st.divider()
    st.subheader("🎬 Previous & Current Projects")

    tv_projects = research["tv_projects"]
    movie_projects = research["movie_projects"]

    metric1, metric2 = st.columns(2)

    with metric1:
        st.metric(
            "📺 TV Series",
            len(tv_projects),
        )

    with metric2:
        st.metric(
            "🎥 Movies",
            len(movie_projects),
        )

    st.caption(
        "These counts reflect unique TMDB cast "
        "credits, not necessarily the actor's "
        "complete professional filmography."
    )

    tv_tab, movie_tab, timeline_tab = st.tabs([
        "📺 TV Series",
        "🎥 Movies",
        "🗓️ Career Timeline",
    ])

    with tv_tab:
        display_project_cards(
            tv_projects,
            f"actor_{person_id}_tv",
        )

    with movie_tab:
        display_project_cards(
            movie_projects,
            f"actor_{person_id}_movies",
        )

    with timeline_tab:
        if research["projects"]:
            for project in research["projects"][:100]:
                kind = (
                    "📺"
                    if project["type"] == "tv"
                    else "🎥"
                )

                character = (
                    f" — as {project['character']}"
                    if project.get("character")
                    else ""
                )

                st.write(
                    f"{kind} "
                    f"**{project['year'] or 'Unknown'}** "
                    f"— {project['title']}"
                    f"{character}"
                )
        else:
            st.info("No dated projects available.")

    # -------------------------------------
    # GEMINI AI CAREER SUMMARY
    # -------------------------------------

    st.divider()
    st.subheader("🤖 AI Career Overview")

    st.write(
        "Generate a career summary using the "
        "available TMDB, Wikidata, and Wikipedia "
        "information."
    )

    if st.button(
        "✨ Generate AI Career Overview",
        key=f"ai_career_{person_id}",
        use_container_width=True,
    ):
        with st.spinner(
            "Gemini is preparing the career overview..."
        ):
            try:
                summary = cached_ai_summary(
                    person_id
                )

                st.session_state[
                    f"career_summary_{person_id}"
                ] = summary

            except Exception as error:
                st.warning(
                    "The AI overview could not be "
                    "generated. You can still view "
                    "the sourced information above."
                )
                st.caption(str(error))

    saved_summary = st.session_state.get(
        f"career_summary_{person_id}"
    )

    if saved_summary:
        st.markdown(saved_summary)

        st.caption(
            "AI-generated synthesis, not independently "
            "verified. Check the source records for "
            "important facts."
        )


def show_cast_explorer():
    st.title(
        "🎭 VKJVerse AI — Enhanced Cast Explorer"
    )

    st.write(
        "Explore drama casts, actor biographies, "
        "previous projects, and AI-powered "
        "career overviews. 💜"
    )

    query = st.text_input(
        "🔎 Search for a drama",
        placeholder=(
            "Lovely Runner, Squid Game, "
            "The Untamed, 2gether..."
        ),
        key="enhanced_cast_search",
    )

    if not query.strip():
        st.info(
            "Enter a drama name to explore its cast."
        )
        return

    try:
        with st.spinner("Searching dramas..."):
            results = cached_search(
                query.strip()
            )

        if not results:
            st.warning("No dramas found.")
            return

        shows = results[:15]

        selected_index = st.selectbox(
            "Choose a drama",
            range(len(shows)),
            format_func=lambda i: (
                f"{shows[i].get('name', 'Unknown')} "
                f"({(shows[i].get('first_air_date') or 'N/A')[:4]}) "
                f"— TMDB {shows[i]['id']}"
            ),
            key="enhanced_cast_drama",
        )

        series_id = shows[selected_index]["id"]

        with st.spinner("Loading cast..."):
            details = cached_details(series_id)
            cast = cached_cast(series_id)

        st.divider()

        st.header(
            details.get("name", "Drama Cast")
        )

        st.write(
            details.get("overview")
            or "No description available."
        )

        st.caption(
            f"{len(cast)} cast entries listed by TMDB"
        )

        if not cast:
            st.info(
                "No cast information is currently "
                "available for this drama."
            )
            return

        st.subheader("✨ Meet the Cast")

        limit = st.selectbox(
            "Number of cast members to show",
            [8, 12, 20, 40],
            index=1,
            key="enhanced_cast_limit",
        )

        displayed_cast = cast[:limit]

        for start in range(
            0, len(displayed_cast), 4
        ):
            columns = st.columns(4)

            for offset, actor in enumerate(
                displayed_cast[start:start + 4]
            ):
                with columns[offset]:
                    photo = image_url(
                        actor.get("profile_path")
                    )

                    if photo:
                        st.image(
                            photo,
                            use_container_width=True,
                        )
                    else:
                        st.caption(
                            "Photo unavailable"
                        )

                    st.markdown(
                        f"**{actor.get('name', 'Unknown')}**"
                    )

                    st.caption(
                        "🎭 As "
                        + (
                            actor.get("character")
                            or "Character not listed"
                        )
                    )

        # ----------------------------------
        # ACTOR SELECTION
        # ----------------------------------

        st.divider()
        st.subheader("🔎 Research an Actor")

        actor_ids = []
        seen_ids = set()

        for actor in cast:
            person_id = actor.get("id")

            if (
                person_id is not None
                and person_id not in seen_ids
            ):
                actor_ids.append(person_id)
                seen_ids.add(person_id)

        actor_by_id = {
            actor["id"]: actor
            for actor in cast
            if actor.get("id") is not None
        }

        selected_person = st.selectbox(
            "Choose an actor or actress",
            actor_ids,
            format_func=lambda person_id: (
                f"{actor_by_id[person_id].get('name', 'Unknown')} "
                f"— {actor_by_id[person_id].get('character') or 'Cast'}"
            ),
            key="enhanced_cast_actor",
        )

        if st.button(
            "💜 View Detailed Actor Profile",
            key=f"view_actor_{selected_person}",
            use_container_width=True,
        ):
            st.session_state[
                "active_cast_profile"
            ] = selected_person

        active_person = st.session_state.get(
            "active_cast_profile"
        )

        if active_person == selected_person:
            show_enhanced_actor_profile(
                selected_person
            )
        else:
            st.info(
                "Select an actor and click "
                "'View Detailed Actor Profile' "
                "to load their research."
            )

    except Exception as error:
        st.error(
            "Unable to load cast information. "
            "Please check your API configuration."
        )
        st.caption(
            f"{type(error).__name__}: {error}"
        )