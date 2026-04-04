import requests

def get_commit(repo):
    r = requests.get(f"https://api.github.com/repos/{repo}/commits")
    return r.json()[0]["sha"] if r.status_code == 200 else None
