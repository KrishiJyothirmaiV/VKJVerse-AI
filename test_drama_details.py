
"""
VKJVerse AI - Drama Details Test

Tests:
1. TMDB drama search
2. Drama status and genres
3. Total seasons and episodes
4. Released episode dates
5. Upcoming episode dates
6. Next episode countdown
7. Cast information
"""

from datetime import date

from drama_details import (
    search_tv_series,
    get_complete_drama_report,
)


def show_episode(episode):
    """Display one episode."""

    season = episode.get("season_number", "?")
    number = episode.get("episode_number", "?")
    title = episode.get("title") or "Untitled"
    air_date = episode.get("air_date") or "Not announced"

    print(
        f"Season {season}, Episode {number} | "
        f"{title} | {air_date}"
    )


def main():
    print("\n" + "=" * 55, flush=True)
    print("💜 VKJVERSE AI - DRAMA DETAILS TEST", flush=True)
    print("=" * 55, flush=True)

    query = input(
        "\nEnter a drama name (e.g. Squid Game): "
    ).strip()

    if not query:
        print("❌ Please enter a drama name.")
        return

    try:
        print("\n🔎 Searching TMDB...", flush=True)

        results = search_tv_series(query)

        if not results:
            print("❌ No dramas found.")
            return

        print("\nSearch results:")

        for index, item in enumerate(results[:5], start=1):
            name = item.get("name", "Unknown")
            year = (
                item.get("first_air_date") or "N/A"
            )[:4]

            print(f"{index}. {name} ({year})")

        selection = input(
            "\nChoose a drama (1-5, default 1): "
        ).strip()

        if not selection:
            selected_index = 0
        elif (
            selection.isdigit()
            and 1 <= int(selection) <= min(5, len(results))
        ):
            selected_index = int(selection) - 1
        else:
            print("❌ Invalid selection.")
            return

        selected_drama = results[selected_index]

        print(
            "\n⏳ Fetching drama and episode details...",
            flush=True,
        )

        report = get_complete_drama_report(
            selected_drama["id"]
        )

        drama = report["drama"]

        print("\n" + "=" * 55)
        print("📺 DRAMA INFORMATION")
        print("=" * 55)

        print("Title:", drama["title"])
        print("Status:", drama["status"])
        print(
            "Genres:",
            ", ".join(drama["genres"]) or "Unknown",
        )
        print(
            "Countries:",
            ", ".join(drama["countries"]) or "Unknown",
        )
        print("Language:", drama["language"])
        print("Rating:", drama["rating"])
        print("Total Seasons:", drama["total_seasons"])
        print("TMDB Total Episodes:", drama["total_episodes"])

        print("\n" + "=" * 55)
        print("📊 EPISODE STATISTICS")
        print("=" * 55)

        print(
            "Episodes listed:",
            report["total_listed_episodes"],
        )
        print(
            "Released:",
            report["released_episode_count"],
        )
        print(
            "Upcoming with dates:",
            report["upcoming_episode_count"],
        )
        print(
            "Without dates:",
            report["unscheduled_episode_count"],
        )

        print("\n" + "=" * 55)
        print("✅ RELEASED EPISODES")
        print("=" * 55)

        released = report["released_episodes"]

        if released:
            for episode in released:
                show_episode(episode)
        else:
            print("No released episodes listed.")

        print("\n" + "=" * 55)
        print("📅 UPCOMING EPISODES")
        print("=" * 55)

        upcoming = report["upcoming_episodes"]

        if upcoming:
            for episode in upcoming:
                show_episode(episode)
        else:
            print(
                "No future episode dates currently "
                "available on TMDB."
            )

        print("\n" + "=" * 55)
        print("⏰ NEXT EPISODE")
        print("=" * 55)

        next_episode = report["next_episode"]

        if next_episode:
            show_episode(next_episode)
            print(
                "Days until release:",
                next_episode["days_until_release"],
            )
        else:
            print("No next episode date available.")

        print("\n" + "=" * 55)
        print("🎭 TOP CAST MEMBERS")
        print("=" * 55)

        cast = report.get("cast", [])

        if cast:
            for actor in cast[:10]:
                print(
                    f"{actor.get('name', 'Unknown')} "
                    f"as {actor.get('character') or 'Unknown'}"
                )
        else:
            print("No cast information available.")

        print("\n" + "=" * 55)
        print("🎉 TEST COMPLETED SUCCESSFULLY!")
        print("=" * 55)

        print(
            "\nNote: Episode dates are original "
            "broadcast dates from TMDB."
        )

    except Exception as error:
        print("\n❌ TEST FAILED")
        print("Error type:", type(error).__name__)
        print("Details:", error)
        raise


if __name__ == "__main__":
    main()