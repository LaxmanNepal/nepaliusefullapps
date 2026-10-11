# NepaliUsefulApps

A community directory for discovering public projects by Nepali creators.

## How it works
- The static front end is hosted without a build step.
- `scripts/build_directory.py` searches public GitHub user and repository metadata, then creates `data/directory.json`.
- GitHub Actions refreshes the directory daily and can also be run manually from **Actions → Refresh creator and project directory → Run workflow**.
- The ranking is a lightweight discovery score using stars, forks, recent activity, and whether a project lists a homepage/demo.
- Creator location and search results are incomplete/self-reported; this directory is a best-effort index, not a complete census of Nepali developers.

## Demo previews
Some sites block iframe embedding via their security headers. In those cases, use the repository/homepage link to open the project in a new tab. Do not try to bypass a site's frame restrictions.

## Manual refresh
Run:
```bash
python scripts/build_directory.py
```
