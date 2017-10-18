from logging import getLogger

import time
from elasticsearch import helpers

from es_wrapper.configuration.parameters import ES_LOGGER_TEMPLATE_NAME
from es_wrapper.general.log import LoggerInfo, init_all_system_logs
from es_wrapper.general.strings import string_generator
from es_wrapper.tools.es_adapter import ESAdapter, es_save_wrapper, es_get_wrapper
from es_wrapper.configuration.mappings import LOGGER_INDEX_MAPPING
from es_wrapper.configuration.setup import save_template_in_es


class EsReindex(ESAdapter):

    INDEX_CREATION_TRIES = 3

    def __init__(self, es_url, source_index, index_template, mapping):
        ESAdapter.__init__(self, es_url)
        self.source_index = source_index
        self.mapping = mapping
        self.temp_index = None
        self.index_template = index_template
        self.logger = getLogger(LoggerInfo.name)

    def reindex(self):
        """
        This method re-indexes all indexes related to the source index
        """
        index_list = self._get_index_list()
        self.logger.debug("Starting reindexing process for %s indexes: %s" % (len(index_list), index_list))

        for index in index_list:
            if not self._reindex_single_index(index):
                self.logger.error("Reindexing stopped at: %s, index list is %s" % (index, index_list))

    @es_get_wrapper
    def _get_index_list(self):
        """
        This method gets a list of all valid indexes related to our sources index
        :return:
        """
        index_list = []
        es_response = self.es.indices.get(self.source_index)
        for index, mapping in es_response.items():
            index_list.append(index)

        return index_list

    @es_save_wrapper
    def _reindex_index_to_temp_index(self, source_idx, destination_idx):
        """
        This method takes and index and remaps it to a different index name
        :param str source_idx: source ES index
        :param str destination_idx: destination ES index

        :return:
        """
        self.logger.debug("Reindexing start for index: %s to index: %s" % (source_idx, destination_idx))
        es_response = helpers.reindex(self.es, source_idx, destination_idx)
        status = self.parse_reindex_response(es_response)
        if not status:
            self.logger.error("Couldn't reindex index: %s to index: %s" % (source_idx, destination_idx))
            return False
        else:
            self.logger.debug("Reindexing finished for index: %s to index: %s" % (source_idx, destination_idx))
            return True

    def _save_mapping(self, index):
        """
        This method wraps mapping saving
        :return bool:
        """
        # Saving mapping to index
        mapping_dict = {self.index_template: self.mapping}
        if not save_template_in_es(self.es_url, mapping_dict):
            self.logger.error("Couldn't save mapping template for %s. Data stored in temp index %s"
                              % (self.index_template, index))
            return False
        else:
            return True

    def _reindex_single_index(self, index):
        """
        This method re-indexes an index to a temporary index, deletes the existing one and saves it again
        """
        tries = self.INDEX_CREATION_TRIES
        # Maximum number of retries
        while tries > 0:

            # First we save the new mappings
            if not self._save_mapping(index):
                return False

            # Create a random index for the temp one
            self.temp_index = "_".join((index, string_generator(size=6).lower()))
            tries -= 1
            # Make sure the temp index has no
            if self.verify_existing_index(self.temp_index):
                self.logger.debug("Reindexing started for index: %s to temp index: %s"
                                  % (index, self.temp_index))

                # Create a new temporary index
                if not self._reindex_index_to_temp_index(index, self.temp_index):
                    return False

                # Delete original
                self.logger.debug("Deleting index: %s" % index)
                if not self.delete_index(index):
                    self.logger.error("Couldn't delete index: %s" % index)
                    return False

                # Mandatory sleep to let ES refresh
                time.sleep(2)

                if not self._reindex_index_to_temp_index(self.temp_index, index):
                    return False

                self.logger.debug("Finished reindexing: %s" % index)

                # Delete temp index
                self.logger.debug("Deleting temp index: %s" % self.temp_index)
                if not self.delete_index(self.temp_index):
                    self.logger.error("Couldn't delete index: %s" % self.temp_index)
                    return False

                return True

        self.logger.error("Couldn't temporary index for %s" % index)
        return False

    def load_from_temp_index(self, index, temp_index):
        """
        This method lets us load specifically an index from a temp one if a process got stuck in the middle
        :param str index:
        :param str temp_index:
        :return bool
        """
        self.temp_index = temp_index
        return self._reindex_single_index(index)


#
# REINDEX_ES_SERVER_URL = "127.0.0.1:9200"
# init_all_system_logs("reindex", debug_mode=True, log_to_file=False, log_to_kafka=False)
# es_server = REINDEX_ES_SERVER_URL
# es_reindex = EsReindex(es_url=es_server,
#                        source_index="logger-2015-12*",
#                        index_template=ES_LOGGER_TEMPLATE_NAME,
#                        mapping=LOGGER_INDEX_MAPPING)
# try:
#     es_reindex.reindex()
# except Exception as exc:
#     print getLogger(LoggerInfo.name).error(exc)
# # es_reindex.load_from_temp_index("fefv_profiles", "profiles")
#
