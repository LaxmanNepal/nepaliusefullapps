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
def search_repos(q):
    data=get("/search/repositories?q="+urllib.parse.quote(q)+"&sort=updated&order=desc&per_page=100")
    return [x["owner"]["login"] for x in (data or {}).get("items",[]) if x.get("owner",{}).get("type")=="User"]
logins=set(SEEDS)
for query in ["location:Nepal","Nepal developer","Nepali","Nepal language"]:
    logins.update(search_users(query))
for query in ["Nepali","Nepal language","Nepal tools","Nepal developer"]:
    logins.update(search_repos(query))
creators=[]
for i,login in enumerate(sorted(logins, key=str.lower)):
    u=get("/users/"+urllib.parse.quote(login))
    if not u: continue
    # A public GitHub location is self-reported, so keep the directory inclusive but label discovery honestly.
    repos=get("/users/"+urllib.parse.quote(login)+"/repos?per_page=100&sort=updated")
    repos=[r for r in (repos or []) if not r.get("fork") and not r.get("archived") and not r.get("private")]
    mapped=[]
    for r in repos:
        mapped.append({
            "name":r["name"], "title":r["name"].replace("-"," ").replace("_"," "),
            "description":r.get("description") or "Open-source project by this creator.",
            "url":r["html_url"], "demo":r.get("homepage") or "", "homepage":r.get("homepage") or "",
            "type":("Web App" if r.get("homepage") else ("API" if any(k in (r["name"]+" "+str(r.get("description"))).lower() for k in ["api","endpoint"]) else "Open Source")),
            "stars":r.get("stargazers_count",0), "forks":r.get("forks_count",0),
            "language":r.get("language") or "", "updated":r.get("updated_at") or "",
            "created":r.get("created_at") or "", "topics":r.get("topics",[])
        })
    mapped.sort(key=lambda r:(r["stars"],r["updated"]),reverse=True)
    creators.append({"login":login,"name":u.get("name") or login,"bio":u.get("bio") or "Public GitHub creator profile.",
                     "location":u.get("location") or "","avatar":u.get("avatar_url") or "",
                     "profile":u.get("html_url") or "https://github.com/"+login,
                     "repos":mapped[:30]})
    if i%20==0: print("Indexed",i+1,"/",len(logins))
projects=[]
for c in creators:
    for r in c["repos"]:
        projects.append({**r,"creatorLogin":c["login"],"creatorName":c["name"],"creatorAvatar":c["avatar"],"creatorProfile":c["profile"]})
def score(p):
    try:
        age=max(1,(datetime.now(timezone.utc)-datetime.fromisoformat(p["updated"].replace("Z","+00:00"))).days)
    except Exception: age=365
    return (p["stars"]*2 + p["forks"]*1.5 + (10 if p["demo"] else 0) + max(0,30-age)*0.25)
projects.sort(key=score,reverse=True)
os.makedirs("data",exist_ok=True)
payload={"generatedAt":datetime.now(timezone.utc).isoformat(),"discoveryNote":"Best-effort discovery from public GitHub search. This is not a complete list of Nepali developers; profile locations and search terms are self-reported/incomplete.","creatorCount":len(creators),"projectCount":len(projects),"creators":creators,"projects":projects,"trending":[p["url"] for p in projects[:30]]}
with open("data/directory.json","w",encoding="utf-8") as f: json.dump(payload,f,ensure_ascii=False,indent=2)
print("Wrote",len(creators),"creators and",len(projects),"projects.")
