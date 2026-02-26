#!/usr/bin/env python3
"""
generate_readme.py — Reads all team and champion YAML files, loads the
Jinja2 template from scripts/readme_template.md, and renders the final
README.md.

Usage:
    python scripts/generate_readme.py

The script is designed to be run from the repo root or from CI.

Dependencies:
    pip install -r requirements.txt   # Jinja2, PyYAML
"""

import datetime
import os
import sys

import jinja2
import yaml

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(SCRIPTS_DIR, ".."))
CHAMPIONS_DIR = os.path.join(REPO_ROOT, "champions")
TEAMS_DIR = os.path.join(REPO_ROOT, "teams")
TEMPLATE_PATH = os.path.join(SCRIPTS_DIR, "readme_template.md")
README_PATH = os.path.join(REPO_ROOT, "README.md")


def _load_required_fields(template_path: str) -> set[str]:
    """Extract required field names from a _template.yaml file.

    Required fields are those that appear after a '# Required fields' comment
    and before the first '# Optional fields' comment (or end of file).
    """
    required: set[str] = set()
    in_required_section = False

    with open(template_path, "r", encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if stripped == "# Required fields":
                in_required_section = True
                continue
            if stripped == "# Optional fields":
                break
            if in_required_section and stripped and not stripped.startswith("#"):
                key = stripped.split(":")[0].strip()
                if key:
                    required.add(key)

    return required


def _load_yaml_dir(
    directory: str,
    required_fields: set[str],
    label: str,
) -> list[dict]:
    """Load all non-template YAML files from *directory*, validating fields."""
    items: list[dict] = []

    if not os.path.isdir(directory):
        print(
            f"ERROR: {label} directory not found: {directory}",
            file=sys.stderr,
        )
        sys.exit(1)

    for filename in sorted(os.listdir(directory)):
        if filename.startswith("_") or not filename.endswith(".yaml"):
            continue
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                item = yaml.safe_load(fh) or {}
            for field in required_fields:
                if field not in item:
                    print(
                        f"WARNING: {filepath} missing required field "
                        f"'{field}' — skipping",
                        file=sys.stderr,
                    )
                    raise ValueError(f"Missing {field}")
            items.append(item)
        except ValueError:
            continue
        except Exception as exc:
            print(
                f"WARNING: failed to parse {filepath}: {exc}",
                file=sys.stderr,
            )
            continue

    return items


def load_teams() -> list[dict]:
    """Load and return all registered team profiles."""
    template_path = os.path.join(TEAMS_DIR, "_template.yaml")
    required_fields = _load_required_fields(template_path)
    return _load_yaml_dir(TEAMS_DIR, required_fields, "Teams")


def load_champions() -> list[dict]:
    """Load and return all champion profiles."""
    template_path = os.path.join(CHAMPIONS_DIR, "_template.yaml")
    required_fields = _load_required_fields(template_path)
    return _load_yaml_dir(CHAMPIONS_DIR, required_fields, "Champions")


def build_context(
    champions: list[dict],
    teams: list[dict],
) -> dict:
    """Build the full Jinja2 template context from raw data."""
    active = [c for c in champions if c["status"] == "active"]
    alumni = [c for c in champions if c["status"] == "alumni"]

    registered_team_names = {t["name"] for t in teams}

    active_by_team: dict[str, list[dict]] = {}
    for c in active:
        active_by_team.setdefault(c["team"], []).append(c)

    threat_models_total = 0
    for team in teams:
        value = team.get("threat_models", 0)
        threat_models_total += int(value)

    for team_name in sorted(active_by_team):
        if team_name not in registered_team_names:
            print(
                f"WARNING: team '{team_name}' is referenced by champions "
                f"but has no file in teams/ — it will appear in the "
                f"champions list but not in coverage",
                file=sys.stderr,
            )

    covered_teams = registered_team_names & set(active_by_team)
    total_teams = len(registered_team_names)
    covered_count = len(covered_teams)
    coverage_pct = round(covered_count / total_teams * 100) if total_teams else 0

    if coverage_pct >= 80:
        coverage_color = "brightgreen"
    elif coverage_pct >= 50:
        coverage_color = "yellow"
    else:
        coverage_color = "red"

    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%d %H:%M UTC"
    )

    return {
        "active": active,
        "alumni": alumni,
        "active_by_team": active_by_team,
        "teams": teams,
        "covered_teams": covered_teams,
        "active_count": len(active),
        "total_teams": total_teams,
        "covered_count": covered_count,
        "coverage_pct": coverage_pct,
        "coverage_color": coverage_color,
        "threat_models_total": threat_models_total,
        "timestamp": timestamp,
    }


def render_template(context: dict) -> str:
    """Load the Jinja2 template and render it with the given context."""
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(SCRIPTS_DIR),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=jinja2.StrictUndefined,
    )

    template = env.get_template("readme_template.md")
    return template.render(context)


def main() -> None:
    teams = load_teams()
    champions = load_champions()

    if not teams:
        print(
            "No team files found in teams/. Nothing to generate.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not champions:
        print(
            "No champion files found in champions/. Nothing to generate.",
            file=sys.stderr,
        )
        sys.exit(1)

    context = build_context(champions, teams)
    readme = render_template(context)

    with open(README_PATH, "w", encoding="utf-8") as fh:
        fh.write(readme)

    print(
        f"README.md generated — {context['active_count']} active champions, "
        f"{context['covered_count']}/{context['total_teams']} teams covered "
        f"({context['coverage_pct']}%)."
    )


if __name__ == "__main__":
    main()
