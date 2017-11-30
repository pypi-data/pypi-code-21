from broth import Broth
from os.path import isfile
from requests import get
from urllib.request import urlretrieve

def clean_title(title):
    return title.replace("'","\\'").replace("`","\\`").replace('"','\\"').rstrip("\\")

def download_if_necessary(url, debug=False):
    if debug: print("starting download_if_necessary with: " + url) 
    path_to_downloaded_file = "/tmp/" + url.split("/")[-1] 
    if not isfile(path_to_downloaded_file): 
        urlretrieve(url, path_to_downloaded_file) 
        print("downloaded:", url, "to", path_to_downloaded_file) 
    return path_to_downloaded_file 
 

def get_most_recent_available_dump():

    try:

        enwiki_url = "https://dumps.wikimedia.org/enwiki/"

        broth = Broth(get(enwiki_url).text)
        print("broth:", type(broth))
        dumps = [a.get("href").rstrip("/") for a in broth.select("a") if not a.text.startswith("latest") and a.get("href") != "../"]
        dumps.reverse()
        print("dumps:", dumps)

        for dump in dumps:
           jobs = get(enwiki_url + dump + "/dumpstatus.json").json()['jobs']
           if jobs['geotagstable']['status'] == "done" and jobs['pagepropstable']['status'] == "done" and jobs['articlesdump']['status'] == "done":
               print("geotags dump on " + dump + " is ready")
               return dump, jobs

    except Exception as e:
        print(e)
        raise e

def run_sql(sql_statement, debug=False):
    try:
        if debug: print("starting run_sql with:", sql_statement)
        sql_statement = sql_statement.replace('"', '\\"')
        bash_command = '''mysql -u root genesis -e "''' + sql_statement + '''"'''
        if debug: print("bash_command:", bash_command)
        output = check_output(bash_command, shell=True).decode("utf-8")
        if debug: print("output: " + output)
        # format as rows of dictionary objects
        lines = output.strip().split("\n")
        if lines:
            header = lines[0].split("\t")
            if debug: print("header:", header)
            if len(lines) > 1:
                result = [dict(zip(header, line.split("\t"))) for line in lines[1:]]
                if debug: print("result:", str(result))
                return result
    except Exception as e:
        print("[wake] run_sql caught exception " + str(e) + " while trying to run " + sql_statement)
        raise e


