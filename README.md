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

## Community submissions and moderation
- Developers can use the **Submit a project** page in the website or the [GitHub project submission issue form](https://github.com/LaxmanNepal/nepaliusefullapps/issues/new?template=project-submission.yml).
- Maintainers should follow [`docs/MODERATION.md`](docs/MODERATION.md) to verify submissions, request changes, reject spam, and avoid duplicates.
- Submissions are reviewed manually by a maintainer. When a valid submission issue has both `project-submission` and `approved` labels, the **Record approved project submission** workflow validates that the repository is public and enabled, checks the submitter's creator username against the repository owner, and records its metadata in `data/approved-submissions.json`. The next directory refresh merges approved entries into `data/directory.json` so they persist.


## Maintainer dashboard
The public `#/admin` route in the site provides shortcuts to the open submission queue, approval workflow runs, directory refresh workflow, approved data, and moderation guide. It is informational only and does not bypass GitHub permissions.
