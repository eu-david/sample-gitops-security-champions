# How This Repo Works

```
teams/               # Registered teams (the canonical team list)
  _template.yaml     # Copy this to register a new team
  payments.yaml
  mobile.yaml
  ...
champions/           # One YAML file per champion (the source of truth)
  _template.yaml     # Copy this to create a new champion profile
  amorales.yaml
  jchen.yaml
  ...
scripts/
  readme_template.md # Jinja2 template used to generate the README
  generate_readme.py # Reads teams/ + champions/ and regenerates this README
.github/workflows/
  update-readme.yml  # CI job that runs the generator on every push
```

1. **Add a team** — copy `teams/_template.yaml` to
   `teams/<team-slug>.yaml`, fill it in.
2. **Add a champion** — copy `champions/_template.yaml` to
   `champions/<github-username>.yaml`.
   The `team` field must match a registered team name.
3. **Customize team/champion profiles** — add any additional fields you like to the according `_template.yaml` YAML
   files. They will be available as variables in the README template. When extending the `readme_template.md`, make sure to set default values for any new variables you add, e.g. `{{ champion.linkedin | default('') }}`, otherwise add it to the `# Required fields` section of the template.
4. **README auto-updates** — a GitHub Actions workflow regenerates this
   file whenever team or champion files change on the default branch.
5. **Customize the page** — edit `scripts/readme_template.md` to change
   headings, descriptions, or layout. Uses
   [Jinja2](https://jinja.palletsprojects.com/) syntax.
