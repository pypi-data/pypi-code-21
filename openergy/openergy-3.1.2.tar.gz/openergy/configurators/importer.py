from ..client import get_client


class ImporterConfigurator:
    def __init__(self, importer_uid):
        """
        Parameters
        ----------
        importer_uid: importer_id or (project_id, importer_name)
        client: optional
        """
        self.client = get_client()

        if isinstance(importer_uid, str):
            self.importer_id = importer_uid
            self.project_id = None
            self.importer_name = None
        else:
            self.importer_id = None
            self.project_id = importer_uid[0]
            self.importer_name = importer_uid[1]

    def create_importer(self, get_if_exists=True):
        assert (None not in (self.project_id, self.importer_name)), "project_id and importer_name must not be None"
        importers_l = self.client.list(
            "odata/importers/",
            dict(project=self.project_id, name=self.importer_name))["data"]

        if len(importers_l) > 1:
            raise AssertionError("len(importers_l) > 1, shouldn't happen")
        elif len(importers_l) == 1:
            # already exists
            if get_if_exists:
                raise AssertionError("Importer already exists.")
            self.importer_id = importers_l[0]["id"]
        else:
            # TODO: understand why create_importer with other_params fails...
            importer = self.client.create(
                "odata/importers/",
                dict(project=self.project_id, name=self.importer_name)
            )
            self.importer_id = importer["id"]

    def update_importer(self, data):
        assert self.project_id is not None, "project_id must not be None (use create or get_or_create)"
        self.client.partial_update("odata/importers", self.importer_id, data=data)

    # def configure_from_directory(self, dir_path):
    #     """
    #     directory must contain:
    #         - params.json
    #         - script.py (optional): will create (or erase) script argument in params dictionary
    #     """
    #     params = load(os.path.join(dir_path, "params.json"))
    #     script_path = os.path.join(dir_path, "script.py")
    #     if os.path.isfile(script_path):
    #         with open(script_path) as f:
    #             params["script"] = f.read()
    #
    #     self.create_importer(params["name"], params["project"], other_params=params)

