#!/usr/bin/env python3

import argparse
import json
import math
import time
import urllib.error
import urllib.request
from pathlib import Path


# ============================================================
# GitHub API
# ============================================================

def api(url, retries=4):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "binit-github-profile",
    }

    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(request, timeout=45) as response:
                return json.load(response)

        except urllib.error.HTTPError as error:
            print(
                f"GitHub API error: HTTP {error.code} "
                f"(attempt {attempt}/{retries})"
            )

            if error.code in (500, 502, 503, 504) and attempt < retries:
                wait = attempt * 3
                print(f"Retrying in {wait} seconds...")
                time.sleep(wait)
                continue

            raise

        except urllib.error.URLError as error:
            print(
                f"Network error: {error.reason} "
                f"(attempt {attempt}/{retries})"
            )

            if attempt < retries:
                wait = attempt * 3
                print(f"Retrying in {wait} seconds...")
                time.sleep(wait)
                continue

            raise

    raise RuntimeError("GitHub API request failed.")


# ============================================================
# Fetch GitHub language statistics
# ============================================================

def get_language_totals(username):

    print(f"Fetching repositories for @{username}...")

    repositories = []
    page = 1

    while True:

        url = (
            f"https://api.github.com/users/{username}/repos"
            f"?per_page=100&page={page}&type=owner"
        )

        data = api(url)

        if not data:
            break

        repositories.extend(data)

        print(
            f"Loaded {len(data)} repositories "
            f"(page {page})"
        )

        if len(data) < 100:
            break

        page += 1

    print(f"Found {len(repositories)} repositories.")

    totals = {}

    for index, repo in enumerate(repositories, start=1):

        # Ignore forks
        if repo.get("fork"):
            continue

        name = repo.get("name", "unknown")

        print(
            f"[{index}/{len(repositories)}] "
            f"Reading languages: {name}"
        )

        try:

            languages_url = repo.get("languages_url")

            if not languages_url:
                continue

            languages = api(languages_url)

            for language, byte_count in languages.items():

                totals[language] = (
                    totals.get(language, 0)
                    + int(byte_count)
                )

        except Exception as error:

            print(
                f"Warning: skipped {name}: {error}"
            )

    return totals


# ============================================================
# Load local JSON language data
# ============================================================

def load_local_data(filename):

    print(f"Loading local language data: {filename}")

    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Format:
    #
    # {
    #   "languages": [
    #       {"name": "Python", "value": 85}
    #   ]
    # }

    if isinstance(data, dict) and "languages" in data:

        languages = data["languages"]

        totals = {}

        for item in languages:

            name = item.get("name")
            value = item.get("value", 0)

            if name:
                totals[name] = float(value)

        return totals

    # Also support:
    #
    # {
    #   "Python": 85,
    #   "JavaScript": 70
    # }

    if isinstance(data, dict):

        return {
            str(name): float(value)
            for name, value in data.items()
        }

    raise ValueError(
        "Invalid language JSON format."
    )


# ============================================================
# Normalize values
# ============================================================

def normalize(values, curve=1.0):

    if not values:
        return []

    maximum = max(values)

    if maximum <= 0:
        maximum = 1

    result = []

    for value in values:

        normalized = (
            (value / maximum) ** curve
        ) * 100

        result.append(normalized)

    return result


# ============================================================
# SVG helpers
# ============================================================

def escape(text):

    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def point(
    cx,
    cy,
    radius,
    index,
    count,
    value
):

    angle = (
        -math.pi / 2
        + 2 * math.pi * index / count
    )

    r = radius * value / 100

    x = cx + r * math.cos(angle)
    y = cy + r * math.sin(angle)

    return x, y


# ============================================================
# Create SVG radar
# ============================================================

def render_radar(
    labels,
    values,
    title,
    dark=True
):

    width = 620
    height = 520

    cx = 310
    cy = 275

    radius = 165

    if dark:

        background = "#0D1117"
        foreground = "#F0F6FC"
        muted = "#8B949E"
        grid = "#30363D"

    else:

        background = "#FFFFFF"
        foreground = "#24292F"
        muted = "#57606A"
        grid = "#D0D7DE"

    accent = "#0285FF"

    parts = []

    parts.append(
        f'''<svg
xmlns="http://www.w3.org/2000/svg"
viewBox="0 0 {width} {height}"
role="img"
aria-label="{escape(title)}">
'''
    )

    # Background
    parts.append(
        f'''
<rect
width="{width}"
height="{height}"
rx="22"
fill="{background}"
/>
'''
    )

    # Title
    parts.append(
        f'''
<text
x="310"
y="45"
text-anchor="middle"
fill="{foreground}"
font-family="system-ui,-apple-system,Segoe UI,sans-serif"
font-size="22"
font-weight="700">
{escape(title)}
</text>
'''
    )

    count = len(labels)

    # Radar grid
    for level in [20, 40, 60, 80, 100]:

        points = []

        for index in range(count):

            x, y = point(
                cx,
                cy,
                radius,
                index,
                count,
                level
            )

            points.append(
                f"{x:.1f},{y:.1f}"
            )

        parts.append(
            f'''
<polygon
points="{" ".join(points)}"
fill="none"
stroke="{grid}"
stroke-width="1"
/>
'''
        )

    # Axes and labels
    for index, label in enumerate(labels):

        x, y = point(
            cx,
            cy,
            radius,
            index,
            count,
            100
        )

        parts.append(
            f'''
<line
x1="{cx}"
y1="{cy}"
x2="{x:.1f}"
y2="{y:.1f}"
stroke="{grid}"
stroke-width="1"
/>
'''
        )

        label_x, label_y = point(
            cx,
            cy,
            radius + 32,
            index,
            count,
            100
        )

        if label_x < cx - 60:
            anchor = "end"

        elif label_x > cx + 60:
            anchor = "start"

        else:
            anchor = "middle"

        parts.append(
            f'''
<text
x="{label_x:.1f}"
y="{label_y:.1f}"
text-anchor="{anchor}"
fill="{foreground}"
font-family="system-ui,-apple-system,Segoe UI,sans-serif"
font-size="13">
{escape(label)}
</text>
'''
        )

    # Radar data
    polygon = []

    for index, value in enumerate(values):

        x, y = point(
            cx,
            cy,
            radius,
            index,
            count,
            value
        )

        polygon.append(
            f"{x:.1f},{y:.1f}"
        )

    parts.append(
        f'''
<polygon
points="{" ".join(polygon)}"
fill="{accent}"
fill-opacity="0.20"
stroke="{accent}"
stroke-width="3"
/>
'''
    )

    # Data points
    for index, value in enumerate(values):

        x, y = point(
            cx,
            cy,
            radius,
            index,
            count,
            value
        )

        parts.append(
            f'''
<circle
cx="{x:.1f}"
cy="{y:.1f}"
r="5"
fill="{accent}"
/>
'''
        )

    # Footer
    parts.append(
        f'''
<text
x="310"
y="485"
text-anchor="middle"
fill="{muted}"
font-family="system-ui,-apple-system,Segoe UI,sans-serif"
font-size="12">
GitHub language usage • generated automatically
</text>
'''
    )

    parts.append("</svg>")

    return "\n".join(parts)


# ============================================================
# Main
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="Generate GitHub language radar SVGs."
    )

    # GitHub username
    parser.add_argument(
        "--github",
        required=False,
        help="GitHub username"
    )

    # Local JSON
    parser.add_argument(
        "--data",
        required=False,
        help="Local JSON language data file"
    )

    # Output
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output path prefix"
    )

    # Maximum languages
    parser.add_argument(
        "--limit",
        type=int,
        default=7,
        help="Number of languages to display"
    )

    # Kept for compatibility
    parser.add_argument(
        "--values",
        action="store_true",
        help="Compatibility option"
    )

    # Curve
    parser.add_argument(
        "--curve",
        type=float,
        default=1.0,
        help="Radar curve"
    )

    # Exclude
    parser.add_argument(
        "--exclude",
        default="",
        help="Comma-separated languages to exclude"
    )

    args = parser.parse_args()

    # Must provide either GitHub or local data
    if not args.github and not args.data:

        raise SystemExit(
            "ERROR: Provide either "
            "--github USERNAME or --data FILE"
        )

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    if args.data:

        totals = load_local_data(
            args.data
        )

    else:

        totals = get_language_totals(
            args.github
        )

    # --------------------------------------------------------
    # Exclusions
    # --------------------------------------------------------

    excluded = {
        item.strip().lower()
        for item in args.exclude.split(",")
        if item.strip()
    }

    totals = {
        language: value
        for language, value in totals.items()
        if language.lower() not in excluded
    }

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    selected = sorted(
        totals.items(),
        key=lambda item: item[1],
        reverse=True
    )[:args.limit]

    if len(selected) < 3:

        raise SystemExit(
            "ERROR: At least 3 languages are required "
            "to create the radar."
        )

    labels = [
        language
        for language, _ in selected
    ]

    raw_values = [
        value
        for _, value in selected
    ]

    values = normalize(
        raw_values,
        args.curve
    )

    # --------------------------------------------------------
    # Display data
    # --------------------------------------------------------

    print()
    print("Languages used:")
    print()

    for language, value in selected:

        print(
            f"{language:<20} {value:g}"
        )

    print()

    # --------------------------------------------------------
    # Output files
    # --------------------------------------------------------

    output = Path(args.output)

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dark_file = output.with_name(
        output.name + "-dark.svg"
    )

    light_file = output.with_name(
        output.name + "-light.svg"
    )

    # --------------------------------------------------------
    # Dark SVG
    # --------------------------------------------------------

    dark_file.write_text(
        render_radar(
            labels,
            values,
            "GitHub Language Usage",
            dark=True
        ),
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Light SVG
    # --------------------------------------------------------

    light_file.write_text(
        render_radar(
            labels,
            values,
            "GitHub Language Usage",
            dark=False
        ),
        encoding="utf-8"
    )

    print(
        f"Created: {dark_file}"
    )

    print(
        f"Created: {light_file}"
    )


if __name__ == "__main__":
    main()