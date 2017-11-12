import requests
import truffleHog

r = requests.get("https://api.github.com/search/repositories?q=coinbase&page=2")

items = r.json()["items"]

r = requests.get("https://api.github.com/orgs/squarespace/repos?page=4")

items = r.json()

for item in items:
    git_url = item["git_url"]
    if item["fork"]:
        continue
    print git_url
    truffleHog.find_strings(git_url, printJson=False, do_regex=True, do_entropy=False)
