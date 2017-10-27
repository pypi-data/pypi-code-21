# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import time
import json
import logging

from . import entity_json

from .exceptions import TimeoutWhileWaitingForRunningIndexToFinishUpdatingException
from .entitybase import EntityBase
from .utils import validate_response_is_ok

logger = logging.getLogger(__name__)


class Dataset(EntityBase):
    """
    This class represents a dataset.
    """

    def __str__(self):
        result = super().__str__()
        return result

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_entities_as_stream(self, since=None, limit=None, start=0, history=True, deleted=True):
        """This returns a http stream for getting the entities of this dataset. (The returned object is a file-like
        stream from the 'requests' library, i.e response.raw)

        :param since: The opaque value that can be used to efficiently skip already seen entities.

        :param limit: The "limit" parameter specifies the maximum number of entities to return.
                      If this is not specified, all available entities are returned.

        :param start: The "start" parameter is a positive integer that specified how many entities to skip from the
                      start of where the "since"-parameters starts. This is far less efficient than using the
                      "since"-parameter, but it can be manually set in a gui to explore the dataset. NOTE: Clients
                      should use the "since"-parameter whenever possible.

        :param history: If this is true (the default) all entities, including replaced ones, will be returned. \
                        If this is false, only the latest version of the entities will be returned.

        :param deleted: If this is True (the default) deleted entities will also be returned. \
                        If this is False, only the non-deleted entities will be returned.
        """
        url = self._connection.get_dataset_entities_url(self.id)

        params = {}
        if since is not None:
            params["since"] = since
        if limit is not None:
            params["limit"] = limit
        if start is not None:
            params["start"] = start
        if history is not None:
            params["history"] = history
        if deleted is not None:
            params["deleted"] = deleted

        # The entities are streamed from the server, so we have to enable streaming here.
        response = self._connection.do_get_request(url, stream=True, params=params)
        validate_response_is_ok(response)

        return response.raw

    def get_entities(self, since=None, limit=None, start=0, history=True, deleted=True):
        """This returns a generator for iterating over the entities of this dataset.

        :param since: The opaque value that can be used to efficiently skip already seen entities.

        :param limit: The "limit" parameter specifies the maximum number of entities to return.
                      If this is not specified, all available entities are returned.

        :param start: The "start" parameter is a positive integer that specified how many entities to skip from the
                      start of where the "since"-parameters starts. This is far less efficient than using the
                      "since"-parameter, but it can be manually set in a gui to explore the dataset. NOTE: Clients
                      should use the "since"-parameter whenever possible.

        :param history: If this is True (the default) all entities, including replaced ones, will be returned. \
                        If this is False, only the latest version of the entities will be returned.

        :param deleted: If this is True (the default) deleted entities will also be returned. \
                        If this is False, only the non-deleted entities will be returned.


        Note: If you just need the raw bytes, consider using the get_entities_as_stream() method instead. That will be
        faster.
        """
        entities_stream = self.get_entities_as_stream(since=since, limit=limit, start=start, history=history,
                                                      deleted=deleted)

        return entity_json.parse_json_stream(entities_stream)

    def get_entity(self, entity_id):
        """Returns the specified entity if it exist, or None if the entity does not exist.

        :param entity_id:
        """
        url = self._connection.get_dataset_entity_url(self.id)
        response = self._connection.do_get_request(url,
                                                   allowable_response_status_codes=[200, 404],
                                                   params={"entity_id": entity_id})
        if response.status_code == 404:
            # No such element.
            return None
        return entity_json.parse_entity(response.text)

    @property
    def num_entities_in_index(self):
        return self._raw_jsondata["runtime"]["count-index-exists"]

    @property
    def num_entities_in_log(self):
        return self._raw_jsondata["runtime"]["count-log-exists"]

    def wait_for_indexes_to_finish_updating(self, timeout=60):
        url = self._connection.get_dataset_indexes_url(self.id)
        response = self._connection.do_get_request(url, stream=True)
        starttime = time.monotonic()
        while True:
            indexes = entity_json.parse_json_stream(response.raw)
            for index in indexes:
                remaining = index["progress"]["remaining"]
                if remaining > 0:
                    # at least one index is still being updated
                    break
            else:
                # all indexes are done
                return

            elapsedtime = time.monotonic() - starttime
            if elapsedtime > timeout:
                raise TimeoutWhileWaitingForRunningIndexToFinishUpdatingException(
                    "Timed out while waiting for the index to finish updating! dataset:\n%s" % (
                        self.as_json(),))
            time.sleep(0.5)

    def run_dtl(self, dtl):
        """Runs the specified dtl on the dataset.

        :param dtl:
        :return: If all went well: a dict with a "sourceEntity" and a "resultEntity" value. If something went wrong a
                 dict with an "error" value (a string describing the error).
        """
        if not isinstance(dtl, str):
            dtl = json.dumps(dtl, indent=4)

        return self.run_operation("run-dtl", {"dtl": dtl})

    def delete(self):
        """Deletes this dataset from the sesam-node.
        """
        url = self._connection.get_dataset_url(self.id)
        response = self._connection.do_delete_request(url)
        validate_response_is_ok(response, allowable_response_status_codes=[200])
        self.update_raw_jsondata(response.text)

    def get_metadata(self):
        """Gets the current metadata for this dataset"""
        url = self._connection.get_dataset_metadata_url(self.id)
        response = self._connection.do_get_request(url)
        validate_response_is_ok(response, allowable_response_status_codes=[200])
        metadata = response.json()
        return metadata

    def set_metadata(self, metadata):
        """Replaces the metadata for this dataset with the specified dictionary"""
        url = self._connection.get_dataset_metadata_url(self.id)
        response = self._connection.do_put_request(url, json=metadata)
        validate_response_is_ok(response, allowable_response_status_codes=[200])

    def delete_metadata(self):
        """Deleted all metadata for this dataset"""
        url = self._connection.get_dataset_metadata_url(self.id)
        response = self._connection.do_delete_request(url)
        validate_response_is_ok(response, allowable_response_status_codes=[200])

    def run_operation(self,
                      operation,
                      operation_parameters=None,
                      allowable_response_status_codes=frozenset([200])):
        """Runs the specified operation on the dataset.
        :param operation: The operation to run.
        :param operation_parameters: A dict with operation parameters.
        :param allowable_response_status_codes: The http request status code(s) to accept (defaults to 200).
        """
        url = self._connection.get_dataset_url(self.id)
        postdata = {"operation": operation}
        if operation_parameters is not None:
            postdata.update(operation_parameters)

        response = self._connection.do_post_request(url, data=postdata)

        validate_response_is_ok(response, allowable_response_status_codes=allowable_response_status_codes)
        return response.json()
