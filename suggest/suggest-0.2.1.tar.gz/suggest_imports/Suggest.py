import os
import sys
import json
import math
import toml
import argparse
import urllib.request
from enum import Enum
from tabulate import tabulate

def usage():
    print("suggest must be called within a valid project directory")
    sys.exit(0)

def parse_pip():
    print("Parsing PIP yet to be implemented.")


def parse_npm():
    print("Parsing NPM yet to be implemented.")


# Parse a local cargo repo and produce a valid index file
# @ ldir : String = Directory path of local cargo repo to parse_cargo
# @ res_out : String = File relative path/name to store resulting index
# @ tot_out : String = File relative path/name to store total usage data
def parse_cargo(ldir, res_out, tot_out):
    print("Parsing Cargo")
    result = {}
    for root, dirs, files in os.walk(ldir):
        for name in files:
            try:
                with open(os.path.join(root, name)) as json_file:
                    json_data = json.load(json_file)
                    packages = [
                        x["name"] for x in json_data["deps"] if x["name"]
                    ]
                    packages.append(json_data["name"])
                    for p1 in packages:
                        cur_p = result.setdefault(p1, {})
                        for p2 in packages:
                            if p1 != p2:
                                cur_n = result[p1].setdefault(p2, 0)
                                cur_p[p2] = cur_n + 1
            except (KeyError, UnicodeDecodeError, json.decoder.JSONDecodeError):
                print ("Ignoring %s" % name)

    total_usage = {}
    for i in result.items():
        for j in i[1].items():
            x = total_usage.setdefault(j[0], 0)
            total_usage[j[0]] = x + j[1]

    # create/populate file for 'result' var
    with open(res_out, 'w+') as res_outfile:
        json.dump(result, res_outfile)

    # create/populate file for 'total_usage' var
    with open(tot_out, 'w+') as tot_outfile:
        json.dump(total_usage, tot_outfile)


# Helper for extracting suggestions from a commonly structured 'index'
# @ index : {}<String, {}<String, Int> > = Listing of package relationships
# @ current : [String] = Names of packages used to build suggestions list.
def get_suggestions(index, current):
    suggestions = {}
    for c in current:
        specific_index = index.setdefault(c, {})
        for i in specific_index.items():
            if i[0] not in current:
                cur_num = suggestions.setdefault(i[0], 0)
                suggestions[i[0]] = cur_num + i[1]
    suggestions_list = [x for x in suggestions.items()]
    suggestions_list.sort(key=lambda x: x[1], reverse=True)
    return suggestions_list


def get_index(index_path, remote=True):
    if not remote:
        with open(index_path) as index_file:
            index_data = json.load(index_file)
    else:
        with urllib.request.urlopen(index_path) as url_res:
            index_data = json.loads(url_res.read().decode())
    return index_data


def get_index_remote(index_uri):
    print ("Coming soon!")


def suggest_pip():
    print("Suggesting for python imports yet to be implemented.")
    # from modulefinder import ModuleFinder
    # finder = ModuleFinder()
    # finder.run_script("myscript.py")
    # for name, mod in finder.modules.iteritems():
    #     print(name)

def suggest_npm():
    print("Suggesting for NPM imports yet to be implemented.")


def suggest_cargo(index, projectDirs=[], cargoTomls=[], specificPackages=[]):
    packages = []
    for d in projectDirs:
        try:
            with open("Cargo.toml") as cargo_toml:
                cargo_data = toml.load(cargo_toml)
                to_parse = [cargo_data]
                for obj in to_parse:
                    for k in obj.keys():
                        if "dependenc" in k:
                            packages = packages + list(obj[k].keys())
                        if isinstance(obj[k], dict):
                            to_parse.append(obj[k])
        except:
            usage()
    return get_suggestions(index, packages)


def format_suggestions(suggestions, max_s = 10):
    suggestions = suggestions[:max_s]
    total_points = sum([x[1] for x in suggestions])
    suggestions = [(x[0], str(math.ceil((x[1]/total_points)*1000)/10) + '%') for x in suggestions]
    return tabulate(suggestions, headers=["Package","Relevance"], tablefmt="rst")



def main():
    # Testing Constants
    # cargoPath = "/home/not-inept/Documents/Projects/crates.io-index/"
    # indexName = "cargo_index.json"
    # totalName = "cargo_total.json"
    # indexPath = "./" + indexName
    projectPath = os.getcwd()

    # parse_cargo(cargoPath, indexName, totalName)
    indexPath = "https://gist.githubusercontent.com/not-inept/96fe224c826eb61d07c2ac498ce750d1/raw/4889c6b254dd3bbd34ad33a5ed3fe10bac074f6e/cargo_index.json"

    index = get_index(indexPath)
    suggestions = suggest_cargo(index, projectDirs=[projectPath])
    print()
    print(format_suggestions(suggestions))
    print()


if __name__ == "__main__":
    main()
