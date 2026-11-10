
from dataclasses import dataclass
from drafter import *


# --------------------------------------------------
# DATA CLASSES
# --------------------------------------------------

@dataclass
class Sighting:
    """Store information about one deer sighting."""

    location: str
    buck_points: int
    time_seen: str
    notes: str


@dataclass
class Hunt:
    """Store information about one hunting trip."""

    location: str
    date: str
    notes: str


@dataclass
class State:
    """Store all information used by the website."""

    sightings: list[Sighting]
    selected_location: str
    search_text: str
    total_hunts: int
    hunts: list[Hunt]


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def page_header(title: str, subtitle: str) -> list:
    """Create a consistent heading for each website page."""

    return [
        Header(title),
        subtitle,
        "\n"
    ]


def navigation() -> list:
    """Create navigation buttons for the website."""

    return [
        Button("Home", "index"),
        Button("Sightings", "sightings_page"),
        Button("Add Sighting", "add_sighting"),
        Button("Locations", "locations_page"),
        Button("Search", "search_page"),
        Button("Log Hunt", "log_hunt"),
        Button("Statistics", "stats_page"),
        "\n"
    ]


def get_locations(state: State) -> list[str]:
    """Return an alphabetically sorted list of hunting locations."""

    locations = []

    for sighting in state.sightings:
        if sighting.location not in locations:
            locations.append(sighting.location)

    for hunt in state.hunts:
        if hunt.location not in locations:
            locations.append(hunt.location)

    locations.sort()
    return locations


def get_matching_sightings(
    state: State,
    location: str
) -> list[Sighting]:
    """Return sightings from the selected location."""

    matching_sightings = []

    for sighting in state.sightings:
        if location == "All Locations":
            matching_sightings.append(sighting)
        elif sighting.location == location:
            matching_sightings.append(sighting)

    return matching_sightings


def search_sightings(
    state: State,
    search_text: str
) -> list[Sighting]:
    """Find sightings that match the search text."""

    matching_sightings = []
    search_text = search_text.lower()

    for sighting in state.sightings:
        searchable_text = (
            sighting.location + " "
            + str(sighting.buck_points) + " "
            + sighting.time_seen + " "
            + sighting.notes
        )

        if search_text in searchable_text.lower():
            matching_sightings.append(sighting)

    return matching_sightings


def calculate_buck_statistics(
    sightings: list[Sighting]
) -> tuple[int, float, int]:
    """Calculate buck count, average points, and highest points."""

    buck_count = 0
    total_points = 0
    highest_points = 0

    for sighting in sightings:
        if sighting.buck_points > 0:
            buck_count += 1
            total_points += sighting.buck_points

            if sighting.buck_points > highest_points:
                highest_points = sighting.buck_points

    if buck_count > 0:
        average_points = total_points / buck_count
    else:
        average_points = 0.0

    return buck_count, average_points, highest_points


def format_sighting(sighting: Sighting) -> str:
    """Format one sighting for display."""

    if sighting.buck_points == 0:
        deer_type = "Doe or unidentified deer"
    else:
        deer_type = str(sighting.buck_points) + "-point buck"

    return (
        "Location: " + sighting.location
        + " | Deer: " + deer_type
        + " | Time: " + sighting.time_seen
        + " | Notes: " + sighting.notes
    )


def format_hunt(hunt: Hunt) -> str:
    """Format one hunting trip for display."""

    return (
        "Location: " + hunt.location
        + " | Date: " + hunt.date
        + " | Notes: " + hunt.notes
    )


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@route
def index(state: State) -> Page:
    """Display the main dashboard."""

    content = page_header(
        "DEER HUNTING TRACKER",
        "Your personal hunting journal and deer management log."
    )

    content += navigation()

    buck_count, average_points, highest_points = (
        calculate_buck_statistics(state.sightings)
    )

    content += [
        Header("Your Hunting Dashboard"),
        "Total deer sightings: " + str(len(state.sightings)),
        "Total hunting trips: " + str(state.total_hunts),
        "Bucks recorded: " + str(buck_count),
        "Average buck points: " + str(round(average_points, 1)),
        "Highest point buck: " + str(highest_points),
        "\n",
        Header("Quick Actions"),
        Button("Record a Sighting", "add_sighting"),
        Button("Log a Hunting Trip", "log_hunt"),
        Button("View Your Sightings", "sightings_page"),
        "\n",
        Header("Recent Sightings")
    ]

    if len(state.sightings) == 0:
        content.append("You have not recorded any sightings yet.")
    else:
        for sighting in state.sightings[-3:]:
            content.append(format_sighting(sighting))

    return Page(state, content)


# --------------------------------------------------
# SIGHTINGS PAGE
# --------------------------------------------------

@route
def sightings_page(state: State) -> Page:
    """Display sightings from all or one location."""

    content = page_header(
        "ALL DEER SIGHTINGS",
        "Review every deer recorded in your hunting journal."
    )

    content += navigation()

    matching_sightings = get_matching_sightings(
        state,
        state.selected_location
    )

    content.append(
        "Currently viewing: " + state.selected_location
    )
    content.append("\n")

    if len(matching_sightings) == 0:
        content.append("No sightings have been recorded here.")
    else:
        for sighting in matching_sightings:
            content.append(format_sighting(sighting))
            content.append("\n")

    content.append(Button("Add a Sighting", "add_sighting"))

    return Page(state, content)


# --------------------------------------------------
# ADD SIGHTING PAGE
# --------------------------------------------------

@route
def add_sighting(state: State) -> Page:
    """Display the form for recording a deer sighting."""

    content = page_header(
        "RECORD A DEER SIGHTING",
        "Add a new deer observation to your hunting journal."
    )

    content += navigation()

    content += [
        Header("Sighting Information"),
        "Hunting location:",
        TextBox("location", ""),
        "\n",
        "Number of antler points (enter 0 for a doe or unknown):",
        TextBox("buck_points", 0, "number"),
        "\n",
        "Time of sighting:",
        TextBox("time_seen", ""),
        "\n",
        "Additional notes:",
        TextArea("notes", ""),
        "\n",
        Button("Save Sighting", "save_sighting")
    ]

    return Page(state, content)


@route
def save_sighting(
    state: State,
    location: str,
    buck_points: int,
    time_seen: str,
    notes: str
) -> Page:
    """Save a new deer sighting."""

    if location.strip() == "":
        location = "Unknown Location"

    if buck_points < 0:
        buck_points = 0

    if time_seen.strip() == "":
        time_seen = "Not recorded"

    if notes.strip() == "":
        notes = "No additional notes"

    new_sighting = Sighting(
        location,
        buck_points,
        time_seen,
        notes
    )

    state.sightings.append(new_sighting)
    state.selected_location = "All Locations"

    return sightings_page(state)


# --------------------------------------------------
# LOCATIONS PAGE
# --------------------------------------------------

@route
def locations_page(state: State) -> Page:
    """Display available hunting locations."""

    content = page_header(
        "HUNTING LOCATIONS",
        "Explore the places where you have hunted and seen deer."
    )

    content += navigation()

    locations = get_locations(state)
    options = ["All Locations"] + locations

    if state.selected_location not in options:
        state.selected_location = "All Locations"

    content += [
        Header("Choose a Location"),
        "Select a location to view its sightings:",
        SelectBox(
            "location_choice",
            options,
            state.selected_location
        ),
        "\n",
        Button("View Location", "filter_location"),
        "\n",
        Header("Saved Locations")
    ]

    if len(locations) == 0:
        content.append("No hunting locations have been recorded.")
    else:
        for location in locations:
            content.append(location)

    return Page(state, content)


@route
def filter_location(
    state: State,
    location_choice: str
) -> Page:
    """Change the selected hunting location."""

    state.selected_location = location_choice

    return sightings_page(state)


# --------------------------------------------------
# SEARCH PAGE
# --------------------------------------------------

@route
def search_page(state: State) -> Page:
    """Display the sighting search page."""

    content = page_header(
        "SEARCH SIGHTINGS",
        "Find a deer using its location, time, notes, or points."
    )

    content += navigation()

    content += [
        Header("Search Your Journal"),
        "Enter a location, number of points, time, or keyword:",
        TextBox("search_text", state.search_text),
        "\n",
        Button("Search", "run_search"),
        Button("Clear Search", "clear_search"),
        "\n",
        Header("Search Results")
    ]

    matching_sightings = search_sightings(
        state,
        state.search_text
    )

    if state.search_text == "":
        content.append("Enter something above to search your journal.")
    elif len(matching_sightings) == 0:
        content.append("No matching sightings were found.")
    else:
        for sighting in matching_sightings:
            content.append(format_sighting(sighting))
            content.append("\n")

    return Page(state, content)


@route
def run_search(state: State, search_text: str) -> Page:
    """Save the search text and display matching results."""

    state.search_text = search_text

    return search_page(state)


@route
def clear_search(state: State) -> Page:
    """Clear the current search."""

    state.search_text = ""

    return search_page(state)


# --------------------------------------------------
# HUNTING TRIP PAGE
# --------------------------------------------------

@route
def log_hunt(state: State) -> Page:
    """Display the form for logging a hunting trip."""

    content = page_header(
        "LOG A HUNTING TRIP",
        "Keep a record of your time spent in the woods."
    )

    content += navigation()

    content += [
        Header("Hunting Trip Information"),
        "Hunting location:",
        TextBox("location", ""),
        "\n",
        "Date of hunt:",
        TextBox("date", ""),
        "\n",
        "Hunting notes:",
        TextArea("notes", ""),
        "\n",
        Button("Save Hunting Trip", "save_hunt"),
        "\n",
        Header("Previous Hunting Trips")
    ]

    if len(state.hunts) == 0:
        content.append("You have not logged any hunting trips.")
    else:
        for hunt in state.hunts:
            content.append(format_hunt(hunt))
            content.append("\n")

    return Page(state, content)


@route
def save_hunt(
    state: State,
    location: str,
    date: str,
    notes: str
) -> Page:
    """Save a hunting trip and update the hunt count."""

    if location.strip() == "":
        location = "Unknown Location"

    if date.strip() == "":
        date = "Date not recorded"

    if notes.strip() == "":
        notes = "No additional notes"

    new_hunt = Hunt(location, date, notes)

    state.hunts.append(new_hunt)
    state.total_hunts += 1

    return log_hunt(state)


# --------------------------------------------------
# STATISTICS PAGE
# --------------------------------------------------

@route
def stats_page(state: State) -> Page:
    """Display hunting and deer sighting statistics."""

    content = page_header(
        "HUNTING STATISTICS",
        "Review your hunting activity and deer observations."
    )

    content += navigation()

    buck_count, average_points, highest_points = (
        calculate_buck_statistics(state.sightings)
    )

    content += [
        Header("Hunting Activity"),
        "Total hunting trips: " + str(state.total_hunts),
        "Total deer sightings: " + str(len(state.sightings)),
        "\n",
        Header("Buck Statistics"),
        "Total bucks recorded: " + str(buck_count),
        "Average antler points: " + str(round(average_points, 1)),
        "Highest point buck: " + str(highest_points),
        "\n",
        Header("Location Statistics")
    ]

    locations = get_locations(state)

    if len(locations) == 0:
        content.append("No hunting locations have been recorded.")
    else:
        for location in locations:
            location_sightings = get_matching_sightings(
                state,
                location
            )

            content.append(
                location + ": "
                + str(len(location_sightings))
                + " deer sightings"
            )

    return Page(state, content)


# --------------------------------------------------
# UNIT TESTS
# --------------------------------------------------

def test_get_locations() -> None:
    """Test that unique hunting locations are returned."""

    state = State(
        [
            Sighting("Oak Ridge", 8, "6 AM", "Large buck"),
            Sighting("North Field", 6, "7 AM", "Small buck"),
            Sighting("Oak Ridge", 10, "8 AM", "Wide buck")
        ],
        "All Locations",
        "",
        0,
        [Hunt("South Woods", "November 10", "Morning hunt")]
    )

    assert_equal(
        get_locations(state),
        ["North Field", "Oak Ridge", "South Woods"]
    )


def test_get_matching_sightings() -> None:
    """Test that sightings are filtered by location."""

    state = State(
        [
            Sighting("Oak Ridge", 8, "6 AM", "Large buck"),
            Sighting("North Field", 6, "7 AM", "Small buck")
        ],
        "All Locations",
        "",
        0,
        []
    )

    assert_equal(
        get_matching_sightings(state, "Oak Ridge"),
        [Sighting("Oak Ridge", 8, "6 AM", "Large buck")]
    )


def test_search_sightings() -> None:
    """Test that searching finds matching sightings."""

    state = State(
        [
            Sighting("Oak Ridge", 8, "6 AM", "Large buck"),
            Sighting("North Field", 6, "7 AM", "Small buck")
        ],
        "All Locations",
        "",
        0,
        []
    )

    assert_equal(
        search_sightings(state, "large"),
        [Sighting("Oak Ridge", 8, "6 AM", "Large buck")]
    )


def test_calculate_buck_statistics() -> None:
    """Test the buck count, average, and highest antler points."""

    sightings = [
        Sighting("Oak Ridge", 8, "6 AM", "Large buck"),
        Sighting("North Field", 6, "7 AM", "Small buck"),
        Sighting("South Woods", 0, "8 AM", "Doe")
    ]

    assert_equal(
        calculate_buck_statistics(sightings),
        (2, 7.0, 8)
    )


def test_index() -> None:
    """Test that the home page is displayed."""

    state = State([], "All Locations", "", 0, [])
    page = index(state)

    assert_equal(page.state, state)
    assert_equal(page.content[0], Header("DEER HUNTING TRACKER"))


def test_sightings_page() -> None:
    """Test that the sightings page is displayed."""

    state = State([], "All Locations", "", 0, [])
    page = sightings_page(state)

    assert_equal(page.state, state)
    assert_equal(page.content[0], Header("ALL DEER SIGHTINGS"))


def test_add_sighting() -> None:
    """Test that the add sighting page is displayed."""

    state = State([], "All Locations", "", 0, [])
    page = add_sighting(state)

    assert_equal(page.state, state)
    assert_equal(page.content[0], Header("RECORD A DEER SIGHTING"))


def test_save_sighting() -> None:
    """Test that a new sighting is saved."""

    state = State([], "All Locations", "", 0, [])

    page = save_sighting(
        state,
        "Oak Ridge",
        8,
        "6 AM",
        "Large buck"
    )

    expected = State(
        [Sighting("Oak Ridge", 8, "6 AM", "Large buck")],
        "All Locations",
        "",
        0,
        []
    )

    assert_equal(page.state, expected)


def test_locations_page() -> None:
    """Test that the locations page is displayed."""

    state = State([], "All Locations", "", 0, [])
    page = locations_page(state)

    assert_equal(page.state, state)
    assert_equal(page.content[0], Header("HUNTING LOCATIONS"))


def test_filter_location() -> None:
    """Test that selecting a location changes the state."""

    state = State(
        [
            Sighting("Oak Ridge", 8, "6 AM", "Large buck"),
            Sighting("North Field", 6, "7 AM", "Small buck")
        ],
        "All Locations",
        "",
        0,
        []
    )

    page = filter_location(state, "Oak Ridge")

    expected = State(
        [
            Sighting("Oak Ridge", 8, "6 AM", "Large buck"),
            Sighting("North Field", 6, "7 AM", "Small buck")
        ],
        "Oak Ridge",
        "",
        0,
        []
    )

    assert_equal(page.state, expected)


def test_search_page() -> None:
    """Test that the search page is displayed."""

    state = State([], "All Locations", "", 0, [])
    page = search_page(state)

    assert_equal(page.state, state)
    assert_equal(page.content[0], Header("SEARCH SIGHTINGS"))


def test_run_search() -> None:
    """Test that the search text is saved."""

    state = State([], "All Locations", "", 0, [])

    page = run_search(state, "Oak Ridge")

    expected = State(
        [],
        "All Locations",
        "Oak Ridge",
        0,
        []
    )

    assert_equal(page.state, expected)


def test_clear_search() -> None:
    """Test that the search text is cleared."""

    state = State([], "All Locations", "Oak Ridge", 0, [])

    page = clear_search(state)

    expected = State([], "All Locations", "", 0, [])

    assert_equal(page.state, expected)


def test_log_hunt() -> None:
    """Test that the hunting trip page is displayed."""

    state = State([], "All Locations", "", 0, [])
    page = log_hunt(state)

    assert_equal(page.state, state)
    assert_equal(page.content[0], Header("LOG A HUNTING TRIP"))


def test_save_hunt() -> None:
    """Test that a hunting trip is saved and counted."""

    state = State([], "All Locations", "", 0, [])

    page = save_hunt(
        state,
        "Oak Ridge",
        "November 10",
        "Morning hunt"
    )

    expected = State(
        [],
        "All Locations",
        "",
        1,
        [Hunt("Oak Ridge", "November 10", "Morning hunt")]
    )

    assert_equal(page.state, expected)


def test_stats_page() -> None:
    """Test that the statistics page is displayed."""

    state = State([], "All Locations", "", 0, [])
    page = stats_page(state)

    assert_equal(page.state, state)
    assert_equal(page.content[0], Header("HUNTING STATISTICS"))


# --------------------------------------------------
# RUN ALL UNIT TESTS
# --------------------------------------------------

test_get_locations()
test_get_matching_sightings()
test_search_sightings()
test_calculate_buck_statistics()

test_index()
test_sightings_page()
test_add_sighting()
test_save_sighting()
test_locations_page()
test_filter_location()
test_search_page()
test_run_search()
test_clear_search()
test_log_hunt()
test_save_hunt()
test_stats_page()


# --------------------------------------------------
# WEBSITE APPEARANCE
# --------------------------------------------------

set_website_title("Deer Hunting Tracker")
set_website_style("none")
set_website_framed(False)

add_website_css("""
html, body {
    background-color: #17251b !important;
    color: #eee8d5 !important;
    min-height: 100%;
}

#drafter-body-- {
    background-color: #17251b !important;
    color: #eee8d5 !important;
    font-family: Georgia, serif;
    max-width: 1100px;
    margin: auto;
    padding: 30px;
    line-height: 1.7;
}

#drafter-body-- h1 {
    color: #d6bd8a !important;
    font-size: 2.5em;
    text-align: center;
    letter-spacing: 2px;
    border-bottom: 2px solid #65764b;
    padding-bottom: 15px;
}

#drafter-body-- h2 {
    color: #c5a875 !important;
    border-bottom: 1px solid #536447;
    padding-bottom: 8px;
    margin-top: 28px;
}

#drafter-body-- h3 {
    color: #d6bd8a !important;
}

#drafter-body-- p,
#drafter-body-- li,
#drafter-body-- label,
#drafter-body-- span,
#drafter-body-- div {
    color: #eee8d5;
}

#drafter-body-- button {
    background-color: #405b3c !important;
    color: #ffffff !important;
    border: 1px solid #75845c;
    border-radius: 7px;
    padding: 10px 16px;
    margin: 5px;
    font-weight: bold;
}

#drafter-body-- button:hover {
    background-color: #65764b !important;
}

#drafter-body-- input,
#drafter-body-- textarea,
#drafter-body-- select {
    background-color: #eee8d5 !important;
    color: #263326 !important;
    border: 1px solid #9b895f;
    border-radius: 5px;
    padding: 9px;
}

#drafter-body-- a {
    color: #d6bd8a !important;
}

#drafter-body-- hr {
    border-color: #65764b;
}

@media (max-width: 650px) {
    #drafter-body-- {
        padding: 15px;
    }

    #drafter-body-- h1 {
        font-size: 1.8em;
    }
}
""")


# --------------------------------------------------
# WEBSITE INFORMATION
# --------------------------------------------------

set_site_information(
    "Your Name",
    "A personal deer hunting journal for tracking sightings, "
    "hunting locations, trips, and buck statistics.",
    [],
    "The website includes a hunting dashboard, sighting journal, "
    "location filter, search tool, hunting trip log, and statistics.",
    []
)


# --------------------------------------------------
# START WEBSITE
# --------------------------------------------------

start_server(
    State([], "All Locations", "", 0, [])
)
