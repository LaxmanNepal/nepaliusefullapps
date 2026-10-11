# Project submission moderation

## Review queue
New submissions should have the `project-submission` and `needs-review` labels. Review them in the repository's [open issues](https://github.com/LaxmanNepal/nepaliusefullapps/issues).

## Review checklist
1. Confirm the repository is public and the URL resolves to the named owner and repository.
2. Check that the project is useful/relevant to the Nepali creator ecosystem and is not spam, a duplicate, malware, or a misleading download.
3. Verify that the description and category are accurate. Open the live demo in a separate tab; some sites intentionally block iframe previews.
4. If details are missing, comment on the issue and keep `needs-review`.
5. When approved, add the `approved` label while keeping `project-submission`. The approval workflow validates the repository and records it in `data/approved-submissions.json`; the next successful directory refresh publishes it. Check the Actions run if validation fails.
6. If rejected, explain briefly and close the issue. For duplicates, link the existing project and close it as a duplicate.

## Labels
- `project-submission`: community-submitted project
- `needs-review`: waiting for a maintainer
- `approved`: maintainer-approved; triggers automated validation and recording
- `rejected`: rejected or spam (optional label)

Only trusted maintainers should apply `approved`. Do not approve projects just because a submitter requests it.
