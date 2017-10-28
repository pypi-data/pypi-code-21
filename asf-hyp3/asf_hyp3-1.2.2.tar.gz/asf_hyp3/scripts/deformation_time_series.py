# deformation_time_series.py
# Rohan Weeden
# Created: June 16, 2017

# Uses the API gateway to do a deformation time series analyis

import json
import requests


def run(list):
    r = requests.post(url="https://bnvvpyvaw9.execute-api.us-west-2.amazonaws.com/Test/get_nearest_neighbor_pairs", data=json.dumps({"granule_list": list}))
    nearest_neighbors = json.loads(r.text)
    r = requests.post(url="https://bnvvpyvaw9.execute-api.us-west-2.amazonaws.com/Test/get_nearest_neighbor_pairs", data=json.dumps({"granule_list": list, "pair_gap": 2}))
    next_nearest_neighbors = json.loads(r.text)
    print(nearest_neighbors)
    return next_nearest_neighbors


if __name__ == "__main__":
    print("Enter a list of granules: ")
    pass
