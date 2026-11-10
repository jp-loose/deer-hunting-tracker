
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
    """Store the information used by the website."""
    sightings: list[Sighting]
    selected_location: str
    search_text: str
    total_hunts: int
    hunts: list[Hunt]


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def get_locations(state: State) -> list[str]:
    """Return a list of unique hunting locations."""

    locations = []

    for sighting in state.sightings:
        if sighting.location not in locations:
            locations.append(sighting.location)

    for hunt in state.hunts:
        if hunt.location not in locations:
            locations.append(hunt.location)

    locations.sort()
    return locations


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@route
def index(state: State) -> Page:
    """Display the home dashboard."""

    return Page(state, [
        Header("DEER HUNTING TRACKER"),
        Text("Your personal deer hunting journal."),
        HorizontalRule(),

        Header("Dashboard"),
        Text("Total deer sightings: " + str(len(state.sightings))),
        Text("Hunts logged: " + str(state.total_hunts)),
        Text("Hunting locations: " + str(len(get_locations(state)))),

        HorizontalRule(),
        Header("Navigation"),

        Link("View All Sightings", "sightings_page"),
        Link("Add a Sighting", "add_sighting"),
        Link("Hunting Locations", "locations_page"),
        Link("Search Sightings", "search_page"),
        Link("Log a Hunt", "log_hunt"),
        Link("Statistics", "stats_page")
    ])


# --------------------------------------------------
# VIEW SIGHTINGS
# --------------------------------------------------

@route
def sightings_page(state: State) -> Page:
    """Display all recorded deer sightings."""

    contents = [
        Header("All Deer Sightings"),
        Link("Home", "index"),
        HorizontalRule()
    ]

    if len(state.sightings) == 0:
        contents.append(Text("No sightings recorded yet."))

    else:
        for number, sighting in enumerate(state.sightings):
            contents.append(Header("Sighting " + str(number + 1)))
            contents.append(Text("Location: " + sighting.location))
            contents.append(Text(
                "Antler points: " + str(sighting.buck_points)
            ))
            contents.append(Text("Time: " + sighting.time_seen))
            contents.append(Text("Notes: " + sighting.notes))
            contents.append(HorizontalRule())

    contents.append(Link("Add Another Sighting", "add_sighting"))

    return Page(state, contents)


# --------------------------------------------------
# ADD SIGHTING
# --------------------------------------------------

@route
def add_sighting(state: State) -> Page:
    """Display the form for adding a deer sighting."""

    return Page(state, [
        Header("Add a Deer Sighting"),
        Link("Home", "index"),
        HorizontalRule(),

        Text("Hunting Location:"),
        TextBox("location"),

        Text("Buck Antler Points:"),
        TextBox("buck_points"),

        Text("Time Seen:"),
        TextBox("time_seen"),

        Text("Additional Notes:"),
        TextArea("notes"),

        Button("Save Sighting", "save_sighting")
    ])


@route
def save_sighting(state: State, location: str,
                  buck_points: str, time_seen: str,
                  notes: str) -> Page:
    """Save a new deer sighting."""

    location = location.strip()
    time_seen = time_seen.strip()

    try:
        points = int(buck_points)
    except ValueError:
        return Page(state, [
            Header("Invalid Antler Points"),
            Text("Please enter a whole number."),
            Link("Try Again", "add_sighting")
        ])

    if location == "" or time_seen == "":
        return Page(state, [
            Header("Missing Information"),
            Text("Please enter a location and time."),
            Link("Try Again", "add_sighting")
        ])

    if points < 0:
        return Page(state, [
            Header("Invalid Antler Points"),
            Text("Antler points cannot be negative."),
            Link("Try Again", "add_sighting")
        ])

    new_sighting = Sighting(
        location,
        points,
        time_seen,
        notes.strip()
    )

    state.sightings.append(new_sighting)

    return Page(state, [
        Header("Sighting Saved!"),
        Text("Your deer sighting has been recorded."),
        Text("Location: " + location),
        Text("Antler points: " + str(points)),
        Link("View All Sightings", "sightings_page"),
        Link("Add Another Sighting", "add_sighting"),
        Link("Home", "index")
    ])


# --------------------------------------------------
# HUNTING LOCATIONS
# --------------------------------------------------

@route
def locations_page(state: State) -> Page:
    """Display hunting locations and their sightings."""

    locations = get_locations(state)
    options = ["All Locations"] + locations

    if state.selected_location not in options:
        state.selected_location = "All Locations"

    contents = [
        Header("Hunting Locations"),
        Link("Home", "index"),
        HorizontalRule(),
        Text("Choose a location to view its sightings:"),

        SelectBox("location_choice", options),

        Button("View Location", "filter_location"),
        HorizontalRule()
    ]

    matching_sightings = []

    for sighting in state.sightings:
        if (state.selected_location == "All Locations"
                or sighting.location == state.selected_location):
            matching_sightings.append(sighting)

    if len(matching_sightings) == 0:
        contents.append(Text("No sightings at this location."))

    else:
        for sighting in matching_sightings:
            contents.append(Text("Location: " + sighting.location))
            contents.append(Text(
                "Antler points: " + str(sighting.buck_points)
            ))
            contents.append(Text("Time: " + sighting.time_seen))
            contents.append(Text("Notes: " + sighting.notes))
            contents.append(HorizontalRule())

    return Page(state, contents)


@route
def filter_location(state: State, location_choice: str) -> Page:
    """Filter sightings by selected location."""

    state.selected_location = location_choice

    return locations_page(state)


# --------------------------------------------------
# SEARCH SIGHTINGS
# --------------------------------------------------

@route
def search_page(state: State) -> Page:
    """Display the search page."""

    contents = [
        Header("Search Deer Sightings"),
        Link("Home", "index"),
        HorizontalRule(),

        Text("Search by location, time, notes, or antler points:"),

        TextBox("search_text"),
        Button("Search", "run_search"),
        HorizontalRule()
    ]

    if state.search_text != "":
        results = []

        for sighting in state.sightings:
            searchable_text = (
                sighting.location + " "
                + sighting.time_seen + " "
                + sighting.notes + " "
                + str(sighting.buck_points)
            )

            if state.search_text.lower() in searchable_text.lower():
                results.append(sighting)

        contents.append(Header(
            "Search Results: " + str(len(results))
        ))

        if len(results) == 0:
            contents.append(Text("No matching sightings found."))

        else:
            for sighting in results:
                contents.append(Text(
                    "Location: " + sighting.location
                ))
                contents.append(Text(
                    "Antler points: " + str(sighting.buck_points)
                ))
                contents.append(Text(
                    "Time: " + sighting.time_seen
                ))
                contents.append(Text(
                    "Notes: " + sighting.notes
                ))
                contents.append(HorizontalRule())

    contents.append(Link("Clear Search", "clear_search"))

    return Page(state, contents)


@route
def run_search(state: State, search_text: str) -> Page:
    """Save and run the search."""

    state.search_text = search_text.strip()

    return search_page(state)


@route
def clear_search(state: State) -> Page:
    """Clear the search."""

    state.search_text = ""

    return search_page(state)


# --------------------------------------------------
# LOG A HUNT
# --------------------------------------------------

@route
def log_hunt(state: State) -> Page:
    """Display the hunting trip form and history."""

    contents = [
        Header("Log a Hunting Trip"),
        Link("Home", "index"),
        HorizontalRule(),

        Text("Hunting Location:"),
        TextBox("hunt_location"),

        Text("Date of Hunt:"),
        TextBox("hunt_date"),

        Text("Hunt Notes:"),
        TextArea("hunt_notes"),

        Button("Save Hunt", "save_hunt"),
        HorizontalRule(),

        Header("Previous Hunts")
    ]

    if len(state.hunts) == 0:
        contents.append(Text("No hunts have been logged."))

    else:
        for hunt in state.hunts:
            contents.append(Text("Location: " + hunt.location))
            contents.append(Text("Date: " + hunt.date))
            contents.append(Text("Notes: " + hunt.notes))
            contents.append(HorizontalRule())

    return Page(state, contents)


@route
def save_hunt(state: State, hunt_location: str,
              hunt_date: str, hunt_notes: str) -> Page:
    """Save a hunting trip."""

    hunt_location = hunt_location.strip()
    hunt_date = hunt_date.strip()

    if hunt_location == "" or hunt_date == "":
        return Page(state, [
            Header("Missing Information"),
            Text("Please enter a location and date."),
            Link("Try Again", "log_hunt")
        ])

    new_hunt = Hunt(
        hunt_location,
        hunt_date,
        hunt_notes.strip()
    )

    state.hunts.append(new_hunt)
    state.total_hunts = state.total_hunts + 1

    return Page(state, [
        Header("Hunt Successfully Logged!"),
        Text("Your hunting trip has been saved."),
        Text("Location: " + hunt_location),
        Text("Date: " + hunt_date),
        Link("View Hunting Trips", "log_hunt"),
        Link("Home", "index")
    ])


# --------------------------------------------------
# STATISTICS
# --------------------------------------------------

@route
def stats_page(state: State) -> Page:
    """Display hunting statistics."""

    total_sightings = len(state.sightings)
    locations = get_locations(state)

    buck_sightings = 0
    total_points = 0
    highest_points = 0

    for sighting in state.sightings:
        if sighting.buck_points > 0:
            buck_sightings = buck_sightings + 1

        total_points = total_points + sighting.buck_points

        if sighting.buck_points > highest_points:
            highest_points = sighting.buck_points

    if total_sightings > 0:
        average_points = total_points / total_sightings
    else:
        average_points = 0

    contents = [
        Header("Hunting Statistics"),
        Link("Home", "index"),
        HorizontalRule(),

        Header("Overall Statistics"),
        Text("Total sightings: " + str(total_sightings)),
        Text("Total hunts: " + str(state.total_hunts)),
        Text("Unique hunting locations: " + str(len(locations))),
        Text("Buck sightings: " + str(buck_sightings)),
        Text("Average antler points: " + str(round(average_points, 2))),
        Text("Highest antler point count: " + str(highest_points)),

        HorizontalRule(),
        Header("Sightings By Location")
    ]

    if len(locations) == 0:
        contents.append(Text("No hunting locations recorded."))

    else:
        for location in locations:
            location_count = 0

            for sighting in state.sightings:
                if sighting.location == location:
                    location_count = location_count + 1

            contents.append(Text(
                location + ": " + str(location_count) + " sightings"
            ))

    contents.append(HorizontalRule())
    contents.append(Header("Hunt History"))

    if len(state.hunts) == 0:
        contents.append(Text("No hunting trips recorded."))

    else:
        for hunt in state.hunts:
            contents.append(Text(
                hunt.date + " - " + hunt.location
            ))

    return Page(state, contents)


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

start_server(State([], "All Locations", "", 0, []))

