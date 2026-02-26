{#- Security Champions README template — powered by Jinja2.
    Edit this file to change the landing page layout.
    Available context variables:
      - active              : list of active champion dicts
      - alumni              : list of alumni champion dicts
      - active_by_team      : dict mapping team name → list of champion dicts
      - teams               : list of all registered team dicts
      - covered_teams       : set of team names that have ≥1 active champion
      - active_count        : int
      - total_teams         : int
      - covered_count       : int
      - coverage_pct        : int (0-100)
      - coverage_color      : str (brightgreen | yellow | red)
      - threat_models_count : int
      - timestamp           : str (UTC)
--#}
{%- macro bool_emoji(value) -%}
  {%- if value == 'N/A' -%}—
  {%- elif value == True -%}✅
  {%- else -%}❌
  {%- endif -%}
{%- endmacro -%}

# Security Champions Program

> A community of security-minded engineers embedded across product and
> platform teams, driving a culture of secure development from within.

![Champions](https://img.shields.io/badge/active_champions-{{ active_count }}-blue)
![Coverage](https://img.shields.io/badge/team_coverage-{{ coverage_pct }}%25-{{ coverage_color }})


---

## What is a Security Champion?

A **Security Champion** is a developer who volunteers to be the security
point-of-contact for their team. Champions help with threat modeling,
secure code reviews, incident triage, and raising security awareness — all
while continuing their normal engineering work.

---

## Current Champions
{% for team_name in active_by_team | sort %}

### {{ team_name }}

| Name | GitHub | Joined | Points |
|------|--------|--------|--------|
  {% for c in active_by_team[team_name] | sort(attribute='name') %}
| [{{ c.name }}](https://github.com/{{ c.github }}) | `@{{ c.github }}` | {{ c.joined | default('—') }} | {{ c.points | default(0) }} |
  {% endfor %}
{% endfor %}
{% if alumni %}
## Alumni

Champions who have moved on — thank you for your contributions!

| Name | GitHub | Joined | Points |
|------|--------|--------|--------|
  {% for c in alumni | sort(attribute='name') %}
| [{{ c.name }}](https://github.com/{{ c.github }}) | `@{{ c.github }}` | {{ c.joined | default('—') }} | {{ c.points | default(0) }} |
  {% endfor %}

{% endif %}
---

## Team Coverage

{{ covered_count }} of {{ total_teams }} registered teams have at least one active security champion.

| Team | Champions | SAST | Secret Scanning | SCA | DAST | IaC | Threat Models |
|------|:---------:|:----:|:---------------:|:---:|:----:|:---:|---------------|
{% for t in teams | sort(attribute='name') %}
  {% if t.name in covered_teams %}
| {{ t.name }} | ✅ | {{bool_emoji(t.SAST) }} | {{ bool_emoji(t.secret_scanning) }} | {{ bool_emoji(t.SCA) }} | {{ bool_emoji(t.DAST) }} | {{ bool_emoji(t.IaC) }} | {{ t.threat_models | default('N/A') }} |
  {% else %}
| {{ t.name }} | ❌ | {{ bool_emoji(t.SAST) }} | {{ bool_emoji(t.secret_scanning) }} | {{ bool_emoji(t.SCA) }} | {{ bool_emoji(t.DAST) }} | {{ bool_emoji(t.IaC) }} | {{ t.threat_models | default('N/A') }} |
  {% endif %}
{% endfor %}

---

## Program Stats

| Metric | Count |
|--------|-------|
| Active Champions | {{ active_count }} |
| Teams | {{ total_teams }} |
| Teams Covered | {{ covered_count }} / {{ total_teams }} ({{ coverage_pct }}%) |
| Threat Models | {{ threat_models_total }} |

<sub>Last generated: {{ timestamp }}</sub>
