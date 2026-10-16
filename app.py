from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import streamlit as st


@dataclass(frozen=True)
class Pathway:
    start: str
    end: str
    minutes: int
    distance_m: int
    surface: str
    stairs: bool
    slope: int
    crowd: str
    lighting: str
    instruction: str


PLACES = {
    "Main Entrance": {
        "category": "Arrival",
        "icon": "🚪",
        "description": "The main entrance and visitor drop-off point.",
        "access": "Automatic doors · step-free entry",
    },
    "Welcome Plaza": {
        "category": "Information",
        "icon": "🧭",
        "description": "An open plaza with a staffed information desk.",
        "access": "Step-free · seating · information desk",
    },
    "Library": {
        "category": "Learning",
        "icon": "📚",
        "description": "A quiet indoor space with reading areas.",
        "access": "Step-free entrance · lift · accessible restroom",
    },
    "Cafe": {
        "category": "Food & drink",
        "icon": "☕",
        "description": "The central cafe, with indoor and outdoor seating.",
        "access": "Step-free entrance · accessible counter",
    },
    "Garden": {
        "category": "Outdoors",
        "icon": "🌿",
        "description": "A landscaped garden with places to sit.",
        "access": "Step-free access by the Welcome Plaza ramp",
    },
    "Quiet Room": {
        "category": "Wellbeing",
        "icon": "🌙",
        "description": "A low-stimulation room for rest and sensory breaks.",
        "access": "Step-free · low noise · adjustable lighting",
    },
}

PATHWAYS = [
    Pathway("Main Entrance", "Welcome Plaza", 3, 180, "Smooth paving", False, 0, "Low", "Bright", "Continue straight along the covered path."),
    Pathway("Main Entrance", "Cafe", 2, 120, "Stairs", True, 0, "Medium", "Bright", "Take the short staircase beside the entrance."),
    Pathway("Welcome Plaza", "Library", 4, 240, "Smooth paving", False, 0, "Low", "Bright", "Follow the paved path past the information desk."),
    Pathway("Welcome Plaza", "Cafe", 3, 170, "Smooth paving", False, 0, "High", "Bright", "Walk toward the cafe entrance across the plaza."),
    Pathway("Welcome Plaza", "Garden", 6, 360, "Smooth ramp", False, 1, "Low", "Bright", "Take the gradual ramp down to the garden gate."),
    Pathway("Cafe", "Library", 4, 250, "Smooth paving", False, 0, "Medium", "Bright", "Follow the indoor corridor toward the library."),
    Pathway("Cafe", "Garden", 3, 160, "Steep paving", False, 2, "Medium", "Bright", "Follow the sloped path to the garden entrance."),
    Pathway("Library", "Quiet Room", 2, 100, "Indoor flooring", False, 0, "Low", "Soft", "Continue along the quiet corridor to the second door."),
    Pathway("Library", "Garden", 5, 290, "Uneven paving", False, 0, "Low", "Bright", "Follow the side path past the library windows."),
    Pathway("Garden", "Quiet Room", 4, 230, "Gravel", False, 0, "Low", "Soft", "Take the garden path to the quiet room entrance."),
]


def find_route(
    origin: str,
    destination: str,
    step_free: bool,
    avoid_stairs: bool,
    avoid_steep: bool,
    prefer_quiet: bool,
) -> Optional[List[Pathway]]:
    """Find a route with hard access requirements and preference-based costs."""
    if origin == destination:
        return []

    graph: Dict[str, List[Pathway]] = {place: [] for place in PLACES}
    for pathway in PATHWAYS:
        graph[pathway.start].append(pathway)
        graph[pathway.end].append(
            Pathway(
                pathway.end,
                pathway.start,
                pathway.minutes,
                pathway.distance_m,
                pathway.surface,
                pathway.stairs,
                pathway.slope,
                pathway.crowd,
                pathway.lighting,
                "Return along the same path.",
            )
        )

    queue: List[Tuple[float, str]] = [(0, origin)]
    costs = {origin: 0.0}
    previous: Dict[str, Tuple[str, Pathway]] = {}

    while queue:
        cost, current = heapq.heappop(queue)
        if current == destination:
            break
        if cost > costs[current]:
            continue

        for pathway in graph[current]:
            if step_free and (pathway.stairs or pathway.surface in {"Gravel", "Uneven paving"}):
                continue
            if avoid_stairs and pathway.stairs:
                continue
            if avoid_steep and pathway.slope > 1:
                continue

            extra = 0.0
            if prefer_quiet and pathway.crowd == "High":
                extra += 5
            if pathway.slope == 1:
                extra += 1
            next_cost = cost + pathway.minutes + extra
            if next_cost < costs.get(pathway.end, float("inf")):
                costs[pathway.end] = next_cost
                previous[pathway.end] = (current, pathway)
                heapq.heappush(queue, (next_cost, pathway.end))

    if destination not in previous:
        return None

    route: List[Pathway] = []
    current = destination
    while current != origin:
        prior, pathway = previous[current]
        route.append(pathway)
        current = prior
    route.reverse()
    return route


def route_totals(route: List[Pathway]) -> Tuple[int, int]:
    return sum(path.minutes for path in route), sum(path.distance_m for path in route)


def render_place_card(name: str) -> None:
    place = PLACES[name]
    st.markdown(
        f"""
        <div class="place-card">
          <div class="place-icon">{place['icon']}</div>
          <div class="place-category">{place['category']}</div>
          <div class="place-name">{name}</div>
          <div class="place-description">{place['description']}</div>
          <div class="place-access">{place['access']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="Pathways · AI Accessibility Navigation",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      :root { --ink: #18332e; --muted: #647873; --green: #176b55; --mint: #eaf4ef; --line: #e5ece8; }
      html, body, [class*="css"] { font-family: "Segoe UI", sans-serif; }
      .stApp { background: #f7f9f7; color: var(--ink); }
      [data-testid="stSidebar"] { background: #f0f5f1; border-right: 1px solid var(--line); }
      [data-testid="stSidebar"] .block-container { padding-top: 2rem; }
      h1, h2, h3 { font-family: "Segoe UI", sans-serif !important; color: var(--ink) !important; letter-spacing: -0.035em; }
      h1 { font-size: 2.35rem !important; }
      .eyebrow { color: var(--green); text-transform: uppercase; font-weight: 700; font-size: .72rem; letter-spacing: .12em; }
      .subhead { color: var(--muted); font-size: 1.05rem; margin-top: -.7rem; }
      .topline { display: flex; align-items: center; gap: 9px; color: var(--muted); font-size: .85rem; margin: .4rem 0 1.4rem; }
      .status-dot { background: #43a87a; width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
      .surface-card, .place-card { background: white; border: 1px solid var(--line); border-radius: 18px; padding: 1.25rem 1.4rem; margin-bottom: 1rem; box-shadow: 0 4px 16px rgba(24,51,46,.035); }
      .place-card { min-height: 215px; }
      .place-icon { font-size: 1.5rem; }
      .place-category { color: var(--green); text-transform: uppercase; letter-spacing: .08em; font-weight: 700; font-size: .68rem; margin-top: .8rem; }
      .place-name { color: var(--ink); font: 700 1.15rem "Segoe UI", sans-serif; margin: .15rem 0 .4rem; }
      .place-description, .place-access { color: var(--muted); font-size: .88rem; line-height: 1.5; }
      .place-access { border-top: 1px solid var(--line); padding-top: .65rem; margin-top: .75rem; font-size: .78rem; }
      .insight { background: var(--mint); border-left: 4px solid var(--green); border-radius: 10px; padding: 1rem 1.1rem; color: #28473e; margin: .8rem 0 1.2rem; }
      .step { display: flex; gap: 1rem; padding: .9rem .5rem; border-bottom: 1px solid var(--line); }
      .step-number { background: var(--mint); color: var(--green); min-width: 2rem; height: 2rem; border-radius: 50%; display: grid; place-items: center; font-weight: 700; }
      .step-title { font-weight: 700; color: var(--ink); }
      .step-detail { color: var(--muted); font-size: .86rem; margin-top: .15rem; line-height: 1.5; }
      .map-stop { display: flex; align-items: center; gap: .75rem; padding: .55rem .3rem; font-weight: 600; }
      .map-line { border-left: 2px dashed #9ac7b2; height: 22px; margin-left: 14px; }
      .fine-print { color: var(--muted); font-size: .8rem; line-height: 1.55; }
      .brand { color: var(--ink); font: 800 1.25rem "Segoe UI", sans-serif; letter-spacing: -.04em; }
      .brand-mark { color: var(--green); }
      div.stButton > button[kind="primary"] { background: var(--green); border-color: var(--green); border-radius: 10px; font-weight: 700; padding: .55rem 1rem; }
      div.stButton > button { border-radius: 10px; }
      [data-testid="stMetric"] { background: white; border: 1px solid var(--line); border-radius: 14px; padding: .9rem 1rem; }
      @media (prefers-reduced-motion: reduce) { *, *::before, *::after { scroll-behavior: auto !important; animation-duration: .01ms !important; } }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark">✳</span> pathways</div>', unsafe_allow_html=True)
    st.caption("ACCESSIBLE WAYFINDING")
    st.divider()
    page = st.radio(
        "Main menu",
        ["Plan a route", "Explore places", "Accessibility guide"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("**Your privacy matters**")
    st.markdown(
        '<p class="fine-print">No GPS or external AI service is used. Route choices stay in the current app session.</p>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="fine-print">Sample venue · Route details are illustrative</div>', unsafe_allow_html=True)

st.markdown('<div class="eyebrow">A more welcoming way around</div>', unsafe_allow_html=True)
st.title("AI accessibility navigation assistant")
st.markdown(
    '<div class="subhead">Find a route that works for you, with clear directions and access details at every step.</div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="topline"><span class="status-dot"></span> Sample venue map · Recommendations update to match your access needs</div>', unsafe_allow_html=True)

if page == "Plan a route":
    st.markdown("### Where would you like to go?")
    with st.form("route_planner"):
        first_row = st.columns(2)
        origin = first_row[0].selectbox("Starting point", list(PLACES), index=0)
        destination = first_row[1].selectbox("Destination", list(PLACES), index=5)
        second_row = st.columns(4)
        step_free = second_row[0].checkbox("Step-free paths only", value=True)
        avoid_stairs = second_row[1].checkbox("Avoid stairs", value=True)
        avoid_steep = second_row[2].checkbox("Avoid steep slopes", value=False)
        prefer_quiet = second_row[3].checkbox("Prefer less-crowded paths", value=False)
        submitted = st.form_submit_button("Find my accessible route", type="primary", use_container_width=True)

    if submitted:
        route = find_route(origin, destination, step_free, avoid_stairs, avoid_steep, prefer_quiet)
        st.session_state["route_request"] = {
            "origin": origin,
            "destination": destination,
            "route": route,
            "step_free": step_free,
            "avoid_stairs": avoid_stairs,
            "avoid_steep": avoid_steep,
            "prefer_quiet": prefer_quiet,
        }

    request = st.session_state.get("route_request")
    if not request:
        st.markdown(
            '<div class="insight"><strong>Personalized by design.</strong> Choose your start, destination, and access preferences to see a route with step-by-step directions.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("### Popular places")
        popular = st.columns(3)
        for column, name in zip(popular, ["Library", "Garden", "Quiet Room"]):
            with column:
                render_place_card(name)
    elif request["route"] is None:
        st.error("No route matches those access preferences. Try allowing a gradual slope or changing your destination.")
    elif request["origin"] == request["destination"]:
        st.info("You are already at your selected destination. Choose a different destination to plan a route.")
    else:
        route = request["route"]
        duration, distance = route_totals(route)
        st.markdown(f"### Your route to {request['destination']}")
        metrics = st.columns(3)
        metrics[0].metric("Estimated time", f"{duration} min")
        metrics[1].metric("Distance", f"{distance} m")
        metrics[2].metric("Path segments", len(route))

        if request["step_free"]:
            insight = "This route follows step-free paths and avoids stairs."
        elif request["avoid_stairs"]:
            insight = "This route avoids stairs. Check the path details below for surface and slope information."
        else:
            insight = "This route is selected to balance walking time and your chosen preferences."
        if request["prefer_quiet"] and all(path.crowd != "High" for path in route):
            insight += " It also avoids the busiest mapped path."
        if any(path.slope > 1 for path in route):
            insight += " Note: one segment has a steeper slope."
        st.markdown(f'<div class="insight"><strong>Route insight</strong><br>{insight}</div>', unsafe_allow_html=True)

        map_column, directions_column = st.columns([.85, 1.4], gap="large")
        with map_column:
            st.markdown("#### Route overview")
            with st.container(border=True):
                st.markdown(f'<div class="map-stop">🟢 <span>{request["origin"]}</span></div>', unsafe_allow_html=True)
                for path in route:
                    st.markdown('<div class="map-line"></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="map-stop">📍 <span>{path.end}</span></div>', unsafe_allow_html=True)
            st.caption("Illustrative route overview — not a live map.")
        with directions_column:
            st.markdown("#### Step-by-step directions")
            for number, path in enumerate(route, start=1):
                slope_text = " · gradual slope" if path.slope == 1 else (" · steep slope" if path.slope > 1 else "")
                st.markdown(
                    f"""
                    <div class="step">
                      <div class="step-number">{number}</div>
                      <div>
                        <div class="step-title">{path.instruction}</div>
                        <div class="step-detail">{path.minutes} min · {path.distance_m} m · {path.surface}{slope_text} · {path.crowd.lower()} traffic</div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown(
                '<p class="fine-print">Times and access conditions are estimates for this sample venue. Confirm current conditions with venue staff.</p>',
                unsafe_allow_html=True,
            )

elif page == "Explore places":
    st.markdown("### Find a place")
    st.markdown('<p class="fine-print">Browse the sample venue and review access information before setting out.</p>', unsafe_allow_html=True)
    for row_start in range(0, len(PLACES), 3):
        columns = st.columns(3)
        for column, name in zip(columns, list(PLACES)[row_start : row_start + 3]):
            with column:
                render_place_card(name)

else:
    st.markdown("### Designed around different access needs")
    st.markdown(
        """
        <div class="surface-card">
          <h4>What the route planner considers</h4>
          <p class="fine-print">Select step-free paths, avoid stairs, avoid steep slopes, or prefer less-crowded routes. Recommendations are calculated from the sample venue's pathway information and the preferences you choose.</p>
          <h4>Using this demo</h4>
          <p class="fine-print">Choose <b>Plan a route</b>, select a start and destination, then set your preferences. Each route includes estimated time, surface, slope, crowd level, and plain-language directions.</p>
          <h4>Accessibility and safety</h4>
          <p class="fine-print">This prototype is not a live navigation service. It has no GPS or live construction, elevator, weather, or crowd updates. Route information is illustrative; please confirm current conditions with venue staff.</p>
          <h4>Keyboard and screen-reader use</h4>
          <p class="fine-print">The app uses standard Streamlit controls, visible form labels, text-based directions, and does not rely on color alone to communicate route details. Use your browser's normal keyboard navigation and zoom controls.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("**A note on the AI assistant**")
    st.markdown(
        '<p class="fine-print">This self-contained demo uses transparent, preference-based route scoring. It does not send data to an external AI model, and its sample pathways should not be used as real-world navigation.</p>',
        unsafe_allow_html=True,
    )

st.divider()
st.markdown(
    '<p class="fine-print">Pathways · AI accessibility navigation assistant · A prototype for inclusive wayfinding</p>',
    unsafe_allow_html=True,
)
