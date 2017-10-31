import pprint

import pandas as pd

from openergy import get_client


def get_series_info(uuid, detailed=True):
    """
    Returns
    -------
    info: comes from list view, not detailed
    """
    client = get_client()

    flat_info = None

    # project_name, generator_model, generator_name, name => retrieve flat info and series_id
    if isinstance(uuid, (tuple, list)):
        project_name, generator_model, generator_name, name = uuid
        all_series = client.list(
            "odata/series",
            params=dict(
                project_name=project_name,
                generator_model=generator_model,
                generator_name=generator_name,
                name=name
            ))
        assert len(all_series["data"]) == 1, "Request did not return one and only one element: %s" % pprint.pformat(
            all_series["data"])
        flat_info = all_series["data"][0]

        # detailed
        series_id = all_series["data"][0]["id"]
    else:
        series_id = uuid

    # detailed route
    if detailed:
        detailed_info = client.retrieve("odata/series", series_id)
        return detailed_info

    # not detailed
    if flat_info is None:
        all_series = client.list(
            "odata/series",
            params=dict(
                id=uuid
            ))
        assert len(all_series["data"]) == 1, "Request did not return one and only one element: %s" % pprint.pformat(
            all_series["data"])
        flat_info = all_series['data'][0]
    return flat_info


def select_series(uuid, **select_kwargs):
    """
    Parameters
    ----------
    uuid: series_id or (project_name, generator_model, generator_name, name)
    """
    client = get_client()

    # get id and name
    info = get_series_info(uuid)
    series_id, name = info["id"], info["name"]

    # select data
    rep = client.detail_route("odata/series", series_id, "GET", "select", params=select_kwargs, return_json=False)

    # transform to pandas series
    se = pd.read_json(rep, orient="split", typ="series")

    # put correct name
    se.name = series_id if name is None else name

    return se

