#!/usr/bin/env python3
"""Build a static directory of public Nepal/Nepali-related GitHub creators and projects."""
import json, os, time, urllib.parse, urllib.request
from datetime import datetime, timezone
API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"Accept":"application/vnd.github+json", "User-Agent":"NepaliUsefulApps-Directory"}
if TOKEN: HEADERS["Authorization"] = "Bearer " + TOKEN
SEEDS = ["prabhashj07","ajaysinghnp","bimalstha23","prabin194","sahilkhatiwada","paraslamsong","iam8uman","yankeexe","rasik-nep","thegauravgiri","nirabpudasaini","LucIfer-mk","mrsushilshrestha","Nabinkdk7","ChandanShakya","UNIL-Agripath"]
def get(path):
    req=urllib.request.Request(API+path, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=25) as res: return json.load(res)
    except Exception as e:
        print("API request failed:", path, e); return None
def search_users(q):
    data=get("/search/users?q="+urllib.parse.quote(q)+"&per_page=100")
    return [x["login"] for x in (data or {}).get("items",[])]
def search_repos(q, sort="stars"):
    data=get("/search/repositories?q="+urllib.parse.quote(q)+"&sort="+sort+"&order=desc&per_page=100")
    return [x["owner"]["login"] for x in (data or {}).get("items",[]) if x.get("owner",{}).get("type")=="User"]
logins=set(SEEDS)
for query in [
    "location:Nepal", "Nepal developer", "Nepali", "Nepal language",
    "Nepal software developer", "Nepali developer", "Nepal programmer"
]:
    logins.update(search_users(query))
# Search by popularity as well as recency to discover established projects.
for query, sort in [
    ("Nepali", "stars"), ("Nepali", "updated"),
    ("Nepal language", "stars"), ("Nepal tools", "stars"),
    ("Nepal developer", "stars"), ("Nepal web app", "stars"),
    ("Nepali web app", "stars"), ("Nepal website", "stars"),
    ("Nepal open source", "stars"), ("Nepali app", "stars"),
    ("Nepal education", "stars"), ("Nepal fintech", "stars"),
    ("Nepal jobs", "stars"), ("Nepal health", "stars"),
    ("Nepal utility", "stars"), ("Nepali calendar", "stars"),
    ("Nepali OCR", "stars"), ("Nepali AI", "stars"),
    ("Nepal API", "stars"), ("Nepal dashboard", "stars"),
    ("location:Nepal", "stars")
]:
    logins.update(search_repos(query, sort))
creators=[]
for i,login in enumerate(sorted(logins, key=str.lower)):
    u=get("/users/"+urllib.parse.quote(login))
    if not u: continue
    repos=get("/users/"+urllib.parse.quote(login)+"/repos?per_page=100&sort=updated")
    repos=[r for r in (repos or []) if not r.get("fork") and not r.get("archived") and not r.get("private")]
    mapped=[]
    for r in repos:
        name=r["name"]
        description=(r.get("description") or "").strip()
        lower=(name+" "+description+" "+" ".join(r.get("topics") or [])).lower()
        # Exclude GitHub profile/config repositories that are not actual projects.
        if name.lower()==login.lower() and ("config files for my github profile" in lower or "profile readme" in lower or not r.get("homepage") and not r.get("stargazers_count") and not r.get("topics")):
            continue
        has_homepage=bool(r.get("homepage"))
        web_terms=["web-app","webapp","website","web application","dashboard","frontend","front-end","react","nextjs","next.js","vue","svelte","angular","html","css","javascript","streamlit","gradio"]
        mobile_terms=["android","ios","mobile-app","mobile app","flutter","react-native","react native"]
        api_terms=["api","endpoint","rest api","graphql","sdk"]
        if has_homepage or any(k in lower for k in web_terms):
            ptype="Web App"
        elif any(k in lower for k in api_terms):
            ptype="API"
        elif any(k in lower for k in mobile_terms):
            ptype="Mobile App"
        else:
            ptype="Open Source"
        mapped.append({
            "name":name, "title":name.replace("-"," ").replace("_"," "),
            "description":r.get("description") or "Open-source project by this creator.",
            "url":r["html_url"], "demo":r.get("homepage") or "", "homepage":r.get("homepage") or "",
            "type":ptype, "stars":r.get("stargazers_count",0), "forks":r.get("forks_count",0),
            "language":r.get("language") or "", "updated":r.get("updated_at") or "",
            "created":r.get("created_at") or "", "topics":r.get("topics",[])
        })
    mapped.sort(key=lambda r:(r["stars"],r["updated"]),reverse=True)
    creators.append({"login":login,"name":u.get("name") or login,"bio":u.get("bio") or "Public GitHub creator profile.",
                     "location":u.get("location") or "","avatar":u.get("avatar_url") or "",
                     "profile":u.get("html_url") or "https://github.com/"+login,
                     "repos":mapped})
    if i%20==0: print("Indexed",i+1,"/",len(logins))
# Merge maintainer-approved community submissions after discovery so daily refreshes preserve them.
approved_path=os.path.join("data","approved-submissions.json")
try:
    approved=json.load(open(approved_path,encoding="utf-8")).get("submissions",[])
except (OSError,ValueError):
    approved=[]
for entry in approved:
    login=entry.get("creatorLogin") or ""
    if not login or not entry.get("url"):
        continue
    creator=next((c for c in creators if c["login"].lower()==login.lower()),None)
    if creator is None:
        creator={"login":login,"name":entry.get("creatorName") or login,"bio":"Community-approved project creator.","location":"","avatar":entry.get("creatorAvatar") or "","profile":entry.get("creatorProfile") or "https://github.com/"+login,"repos":[]}
        creators.append(creator)
    repo={k:entry.get(k) for k in ["name","title","description","url","demo","homepage","type","stars","forks","language","updated","created","topics"]}
    repo["name"]=repo.get("name") or entry["url"].rstrip("/").split("/")[-1]
    repo["title"]=repo.get("title") or repo["name"]
    repo["description"]=repo.get("description") or "Community-approved public project."
    repo["url"]=entry["url"]
    repo["demo"]=repo.get("demo") or ""
    repo["homepage"]=repo.get("homepage") or repo["demo"]
    repo["type"]=repo.get("type") or ("Web App" if repo["homepage"] else "Open Source")
    repo["stars"]=repo.get("stars") or 0
    repo["forks"]=repo.get("forks") or 0
    repo["language"]=repo.get("language") or ""
    repo["updated"]=repo.get("updated") or ""
    repo["created"]=repo.get("created") or ""
    repo["topics"]=repo.get("topics") or []
    creator["repos"]=[old for old in creator["repos"] if old.get("url","").rstrip("/").lower()!=repo["url"].rstrip("/").lower()]
    creator["repos"].insert(0,repo)

projects=[]
for c in creators:
    for r in c["repos"]:
        projects.append({**r,"creatorLogin":c["login"],"creatorName":c["name"],"creatorAvatar":c["avatar"],"creatorProfile":c["profile"]})
def score(p):
    try:
        age=max(1,(datetime.now(timezone.utc)-datetime.fromisoformat(p["updated"].replace("Z","+00:00"))).days)
    except Exception: age=365
    return (p["stars"]*2 + p["forks"]*1.5 + (10 if p["demo"] else 0) + max(0,30-age)*0.25)
projects.sort(key=lambda p:(p.get("stars",0), score(p)),reverse=True)
for c in creators:
    c["totalStars"]=sum(r.get("stars",0) for r in c["repos"])
    c["projectCount"]=len(c["repos"])
creators.sort(key=lambda c:(c["totalStars"],c["projectCount"],c["login"].lower()),reverse=True)
os.makedirs("data",exist_ok=True)
payload={"generatedAt":datetime.now(timezone.utc).isoformat(),"discoveryNote":"Best-effort discovery from public GitHub search. This is not a complete list of Nepali developers; profile locations and search terms are self-reported/incomplete.","creatorCount":len(creators),"projectCount":len(projects),"creators":creators,"projects":projects,"trending":[p["url"] for p in projects[:100]],"mostStarred":[p["url"] for p in sorted(projects,key=lambda p:p.get("stars",0),reverse=True)[:100]],"topCreators":[c["login"] for c in creators[:100]]}
with open("data/directory.json","w",encoding="utf-8") as f: json.dump(payload,f,ensure_ascii=False,indent=2)
print("Wrote",len(creators),"creators and",len(projects),"projects.")
