from . import constants as const
import logging
log = logging.getLogger()
import requests

class Workspace(object):
    def __init__(self, pbi, wks_id = None, wks_name = "", isReadOnly = False):
        '''
        initializes the Workspace class. requires powerbi object.
        If workspace id is passed as None(default), it assumes default (My Workspace)
        '''
        self._pbi = pbi
        self.wks_id = wks_id
        self.wks_name = wks_name
        self.isReadOnly = isReadOnly
    def __str__(self):
        s = "Workspace ID: %s Name: %s" % (self.wks_id, self.wks_name) \
                                    if self.wks_id is not None \
                                    else "Workspace ID: Default Name: My Workspace"
        return s

    def __repr__(self):
        return str(self)

    def get_reports(self):
        pass
    def get_datasets(self):

        if self.wks_id is None:
            datasets = self._pbi.request(const.DATASET_LIST_DEFAULT)
        else:
            datasets = self._pbi.request(const.DATASET_LIST.format(**vars(self)))

        return [Dataset(self,  ds_id = ds["id"], ds_name = ds["name"], details = ds) \
                                                                    for ds in datasets]

    def get_dataset_by_id(self, ds_id):
        ret = [d for d in self.get_datasets() if d.ds_id == ds_id]
        return ret[0] if len(ret) > 0 else None

class Dataset(object):
    def __init__(self, wks, ds_id, ds_name = None, details = None):
        '''
        Constructs a dataset. If only the ID has been passed, retrieve the dataset
        '''

        self._pbi = wks._pbi
        self._wks = wks
        self.wks_id = wks.wks_id
        self.ds_id = ds_id
        if  details is None or ds_name is None:
            ds = wks.get_dataset_by_id(ds_id)
            self.ds_name = ds.ds_name
            self.details = ds.details
        else:
            self.ds_name = ds_name
            self.details = details

    def __str__(self):
        return "Dataset ID: %s Name: %s" % (self.ds_id, self.ds_name)

    def __repr__(self):
        log.debug(vars(self))
        return "Dataset ID: %s Name: %s" % (self.ds_id, self.ds_name)

    def get_tables(self):
        if "addRowsAPIEnabled" not in self.details:
            raise RuntimeError("cannot get the addRowsAPIEnabled property")
        if not self.details["addRowsAPIEnabled"]:
            log.warning("Non-push datasets do not support table API")
            return []

        if self.wks_id is None:
            tables = self._pbi.request(const.TABLES_LIST_DEFAULT.format(**vars(self)))
        else:
            tables = self._pbi.request(const.TABLES_LIST.format(**vars(self)))

        return [Table(self, t["name"]) for t in tables]

class Table(object):
    def __init__(self, ds, tbl_name):
        self._pbi = ds._wks._pbi
        self._ds = ds
        self._wks = ds._wks

        self.ds_id = ds.ds_id
        self.wks_id = ds._wks.wks_id
        self.tbl_name = tbl_name
        self._is_def_workspace = self._wks.wks_id is None
    def _str_(self):
        return "Table: %s" % (self.tbl_name)

    def __repr__(self):
        return "Table: %s" % (self.tbl_name)

    def delete_rows(self):
        headers = {"Authorization": "Bearer " + self._pbi._aad_token}

        if self._is_def_workspace:
            req = const.TABLE_DELETE_ROWS_DEFAULT.format(**vars(self))
        else:
            req = const.TABLE_DELETE_ROWS.format(**vars(self))

        response = requests.delete(req, headers=headers)