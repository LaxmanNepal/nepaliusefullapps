#!/usr/bin/env python3
"""Validate an approved submission issue and append verified public repo metadata."""
import json, os, re, sys, urllib.request
from pathlib import Path

event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
issue = event.get("issue", {})
if issue.get("pull_request"):
    raise SystemExit("Pull requests are not submission issues.")
body = issue.get("body") or ""

def section(*names):
    # Accept GitHub issue-form headings (### Label) and the website's
    # prefilled Markdown body (## headings plus bold-label bullets).
    for name in names:
        heading = re.search(
            r"^#{2,3}\s+" + re.escape(name) + r"\s*\n+([\s\S]*?)(?=^#{2,3}\s+|\Z)",
            body, re.M | re.I,
        )
        if heading:
            value = heading.group(1).strip()
            if value and value.lower() not in {"_no response_", "n/a", "none", "not provided"}:
                return value
        bullet = re.search(
            r"^\s*[-*]\s*\*\*" + re.escape(name) + r"\s*:\*\*\s*(.*?)\s*$",
            body, re.M | re.I,
        )
        if bullet:
            value = bullet.group(1).strip()
            if value.lower() not in {"_no response_", "n/a", "none", "not provided"}:
                return value
    return ""

repo_url = section("Repository URL", "Repository")
creator = section("Creator GitHub username", "Creator GitHub")
creator = creator.strip()
creator_match = re.fullmatch(r"(?:https?://(?:www\.)?github\.com/)?@?([A-Za-z0-9-]+)/?", creator, re.I)
if creator_match:
    creator = creator_match.group(1)
title = section("Project name", "Project name")
description = section("Project description", "Description")
demo = section("Live demo URL (optional)", "Live demo")
category = section("Category")
match = re.fullmatch(r"https?://github\.com/([^/]+)/([^/#?]+)/?", repo_url, re.I)
if not match:
    raise SystemExit("Could not validate repository URL from issue body.")
owner, repo = match.group(1), match.group(2)
if repo.endswith(".git"):
    repo = repo[:-4]
token = os.environ.get("GITHUB_TOKEN", "")
headers = {"Accept": "application/vnd.github+json", "User-Agent": "NepaliUsefulApps-Approval"}
if token:
    headers["Authorization"] = "Bearer " + token
req = urllib.request.Request(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
with urllib.request.urlopen(req, timeout=25) as response:
    metadata = json.load(response)
if metadata.get("private") or metadata.get("disabled"):
    raise SystemExit("Repository must be public and enabled.")
canonical = metadata.get("html_url", "")
if not canonical:
    raise SystemExit("GitHub did not return a canonical repository URL.")
if creator and creator.strip().lstrip("@").lower() != owner.lower():
    raise SystemExit("Creator username must match the repository owner; review and correct the issue before approving.")
homepage = demo if demo.startswith(("https://", "http://")) else (metadata.get("homepage") or "")
entry = {
    "name": metadata["name"],
    "title": title or metadata["name"].replace("-", " ").replace("_", " "),
    "description": description or metadata.get("description") or "Community-submitted public project.",
    "url": canonical,
    "demo": homepage,
    "homepage": homepage,
    "type": category or ("Web App" if homepage else "Open Source"),
    "stars": metadata.get("stargazers_count", 0),
    "forks": metadata.get("forks_count", 0),
    "language": metadata.get("language") or "",
    "updated": metadata.get("updated_at") or "",
    "created": metadata.get("created_at") or "",
    "topics": metadata.get("topics", []),
    "creatorLogin": metadata["owner"]["login"],
    "creatorName": metadata["owner"].get("login", owner),
    "creatorAvatar": metadata["owner"].get("avatar_url", ""),
    "creatorProfile": metadata["owner"].get("html_url", f"https://github.com/{owner}"),
    "approvedIssue": issue.get("html_url", ""),
}
path = Path("data/approved-submissions.json")
data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"submissions": []}
items = data.setdefault("submissions", [])
items = [p for p in items if p.get("url", "").rstrip("/").lower() != canonical.rstrip("/").lower()]
items.append(entry)
data["submissions"] = items
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Approved repository metadata recorded: {canonical}")
