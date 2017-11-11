#########################################################   Importing Packages  #########################################################
#########################################################################################################################################
import requests
import json
#########################################################X X X X X X X X X X X X#########################################################










#####################################################   Function for getting Posts  #####################################################
#########################################################################################################################################
def get_posts(pagename, access_token, start_date="", end_date=""):

    url = "https://graph.facebook.com/v2.10/" + pagename

    if start_date != "" and end_date != "":
        url = url + "/feed?" + "since=" + start_date + "&until=" + end_date + "&access_token=" + access_token + "&limit=100"
    else:
        url = url + "/feed?" + "access_token=" + access_token + "&limit=100"    


    fulldata = []
    count = 0

    while True:
        page = requests.get(url)
        data = page.json()

        try:
            fulldata += data["data"]       
        except:
            try:
                fulldata += data["posts"]["data"]
            except:
                print(data["error"]["message"])
                break

        print("\r" + str(len(fulldata)) + " posts gathered.", end="")
    
        try:
            url = data["posts"]["paging"]["next"]
        
        except:
            try:
                url = data["paging"]["next"]
            
            except:
                break

    print("\r" + str(len(fulldata)) + " posts gathered.")
    return (fulldata)
#########################################################X X X X X X X X X X X X#########################################################










#####################################################   Function for getting likes  #####################################################
#########################################################################################################################################
def get_likes(post_id, access_token):

    url = "https://graph.facebook.com/v2.10/" + post_id

    url = url + "?fields=likes&access_token=" + access_token

    fulldata = []
    while True:

        page = requests.get(url)
        res = page.json()
        #print(res)

        try:
            fulldata += res["data"]       
        except:
            try:
                fulldata += res["likes"]["data"]
            except:
                pass

        print("\r" + str(len(fulldata)) + " likes gathered for " + post_id, end="")

        try:
            url = res["paging"]["next"]
        except:
            try:
                url = res["likes"]["paging"]["next"]
                url = url.replace("limit=25","limit=100")
            except:
                break

    print("\r" + str(len(fulldata)) + " likes gathered for " + post_id)
    return (fulldata)
#########################################################X X X X X X X X X X X X#########################################################










###################################################   Function for getting comments  ####################################################
#########################################################################################################################################
def get_comments(post_id, access_token):

    url = "https://graph.facebook.com/v2.10/" + post_id

    url = url + "?fields=comments&access_token=" + access_token

    fulldata = []
    while True:

        page = requests.get(url)
        res = page.json()
        #print(res)

        try:
            fulldata += res["data"]       
        except:
            try:
                fulldata += res["comments"]["data"]
            except:
                pass

        print("\r" + str(len(fulldata)) + " comments gathered for " + post_id, end="")

        try:
            url = res["paging"]["next"]
        except:
            try:
                url = res["comments"]["paging"]["next"]
                url = url.replace("limit=25","limit=100")
            except:
                break

    print("\r" + str(len(fulldata)) + " comments gathered for " + post_id)
    return (fulldata)
#########################################################X X X X X X X X X X X X#########################################################