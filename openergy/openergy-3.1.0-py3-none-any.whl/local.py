import os
import json
import logging
import hashlib
import textwrap

import pandas as pd

from slugify import slugify

from .outil import mkdir

from openergy import get_client, get_series_info

try:
    from otimeframes import SingleKeyHDFSeriesIO
except ImportError:
    SingleKeyHDFSeriesIO = None
    from .series_io import IncompleteLocalSeriesIO

logger = logging.getLogger(__name__)

META_FIELDS = (  # except name
        "freq",
        "native_clock",
        "timezone",
        "default_resample_rule",
    )


class LocalDatabase:
    def __init__(self, base_path, storage_format="single-key-hdf"):
        # checks
        assert os.path.isdir(base_path), "base path does not exist: %s" % base_path
        assert storage_format in ("single-key-hdf",), "unknown storage format: %s" % storage_format

        # store variables
        self.base_path = base_path
        self.storage_format = storage_format

    def get_local_series(self, project_name, generator_model, generator_name, name):
        """
        Parameters
        ----------
        project_name
        generator_model: importer, cleaner or analysis
        generator_name
        name

        Returns
        -------

        """
        return LocalSeries(self, project_name, generator_model, generator_name, name)

    def iter_local_series(self, project_name, generator_model=None, generator_name=None):
        # slugify
        slug_project_name = slugify(project_name)
        slug_generator_model = None if generator_model is None else slugify(generator_model)
        slug_generator_name = None if generator_name is None else slugify(generator_name)

        # find project
        project_path = os.path.join(self.base_path, slug_project_name)
        if not os.path.isdir(project_path):
            return

        # iter generator models
        for _slug_generator_model in os.listdir(project_path):
            # create path
            generator_model_path = os.path.join(project_path, _slug_generator_model)

            # only keep directories (osx may add hidden files automatically)
            if not os.path.isdir(generator_model_path):
                continue

            # only keep relevant
            if (slug_generator_model is not None) and (slug_generator_model != _slug_generator_model):
                continue

            # iter generator names
            for _slug_generator_name in os.listdir(generator_model_path):
                # create path
                generator_name_path = os.path.join(generator_model_path, _slug_generator_name)

                # only keep directories (osx may add hidden files automatically)
                if not os.path.isdir(generator_name_path):
                    continue

                # only keep relevant
                if (slug_generator_name is not None) and (slug_generator_name != _slug_generator_name):
                    continue

                # iter meta info
                for file_name in os.listdir(generator_name_path):
                    file_path = os.path.join(generator_name_path, file_name)

                    # don't work on directories
                    if os.path.isdir(file_path):
                        continue

                    _base, extension = os.path.splitext(file_name)
                    if extension != ".json":
                        continue

                    with open(file_path) as f:
                        meta = json.load(f)

                    yield self.get_local_series(
                        slug_project_name,
                        _slug_generator_model,
                        _slug_generator_name,
                        meta["name"]
                    )

    def download_all_series(self, project_name, generator_model=None, generator_name=None):
        """
        Parameters
        ----------
        project_name
        generator_model: importer, cleaner or analysis
        generator_name

        Returns
        -------

        """
        # get client
        client = get_client()

        # prepare request
        params = dict(project_name=project_name)
        if generator_model is not None:
            params["generator_model"] = generator_model
        if generator_name is not None:
            params["generator_name"] = generator_name

        # iter all series meta
        for series_meta in client.list_iter_all(
                "odata/series",
                params=params
        ):
            # extract info
            generator_model = series_meta['generator']['model']
            generator_name = series_meta['generator']['name']
            series_name = series_meta['name']

            # prepare local series
            local_se = self.get_local_series(
                project_name,
                generator_model,
                generator_name,
                series_name
            )

            # download
            logger.info("Downloading: %s, %s, %s, %s" % (project_name, generator_model, generator_name, series_name))
            local_se.download()

        logger.info("All series where successfully downloaded.")


class LocalSeries:
    def __init__(self, local_db, project_name, generator_model, generator_name, name):
        assert isinstance(local_db, LocalDatabase), "local_db must be a LocalDatabase object"
        self.local_db = local_db
        self.project_name = project_name
        self.generator_model = generator_model
        self.generator_name = generator_name
        self.name = name

        self.id = None  # only for database series

    def prepare_directory_tree(self):
        current_path = self.local_db.base_path
        for dir_name in (self.project_name, self.generator_model, self.generator_name):
            dir_name = slugify(dir_name)
            current_path = os.path.join(current_path, dir_name)
            if not os.path.exists(current_path):
                mkdir(current_path)

    def delete(self):
        # remove data
        if os.path.exists(self.data_path):
            os.remove(self.data_path)
        # remove meta
        if os.path.exists(self.meta_path):
            os.remove(self.meta_path)
        # cleanup directory tree
        dirs_l = [slugify(self.project_name), slugify(self.generator_model), slugify(self.generator_name)]
        while len(dirs_l) > 0:
            current_path = os.path.join(self.local_db.base_path, *dirs_l)
            if len(os.listdir(current_path)) > 0:
                break
            os.rmdir(current_path)
            dirs_l.pop()

    def clear(self):
        if self.has_data:
            os.remove(self.data_path)

    @property
    def base_path(self):
        return os.path.join(
            self.local_db.base_path,
            slugify(self.project_name),
            slugify(self.generator_model),
            slugify(self.generator_name),
            slugify(self.name)
        )

    @property
    def storage_name(self):
        # we use hash for unique match with name (prefix with se to comply with python variables naming, in case hash
        # starts with number
        return "se" + hashlib.sha1(self.base_path.encode("utf-8")).hexdigest()

    @property
    def data(self):
        se = self.get_se_io().select()
        se.name = self.name  # todo: manage tags
        return se

    @property
    def meta_path(self):
        return self.base_path + ".json"

    @property
    def has_meta(self):
        return os.path.exists(self.meta_path)

    @property
    def data_path(self):
        return self.base_path + ".hdf"

    @property
    def has_data(self):
        return os.path.exists(self.data_path)

    def get_meta(self):
        assert os.path.isfile(self.meta_path), "no meta file, can't retrieve meta info"
        with open(self.meta_path) as f:
            return json.load(f)

    def set_meta(
            self,
            freq,
            native_clock="tzt",
            timezone=None,
            default_resample_rule="mean"):
        assert not os.path.exists(self.meta_path), "can't use set meta if meta already exists. use update_meta"
        self.prepare_directory_tree()
        with open(self.meta_path, "w") as f:
            json.dump(dict(
                name=self.name,
                freq=freq,
                native_clock=native_clock,
                timezone=timezone,
                default_resample_rule=default_resample_rule
            ), f, indent=4)

    def update_meta(self, **kwargs):
        to_set = {}
        for k, v in kwargs.items():
            assert k in META_FIELDS, "unknown meta field: '%s'" % k
            if v is not None:
                to_set[k] = v
        meta = self.get_meta()
        for k, v in to_set.items():
            meta[k] = v
        self.set_meta(
            meta["freq"],
            native_clock=meta["native_clock"],
            timezone=meta["timezone"],
            default_resample_rule=meta["default_resample_rule"]
        )

    def get_se_io(self, human_readable_name=True):
        if SingleKeyHDFSeriesIO is not None:  # use otimeframes series_io
            meta = self.get_meta()
            return SingleKeyHDFSeriesIO(
                self.name if human_readable_name else self.storage_name,
                self.data_path,
                freq=meta["freq"],
                native_clock=meta["native_clock"],
                timezone=meta["timezone"],
                tags=[],
                default_resample_rule=meta["default_resample_rule"],
                default_max_acceptable_delay="6H",  # todo !! (must update opmodels and oplatform first)
                storage_name=self.storage_name if human_readable_name else None
            )

        # use incomplete local series io
        return IncompleteLocalSeriesIO(
            self.name if human_readable_name else self.storage_name,
            self.data_path
        )

    def download(self):
        """
        will be reset

        Returns
        -------
        """
        client = get_client()

        # get series info
        uuid = (self.project_name, self.generator_model, self.generator_name, self.name) if self.id is None else self.id
        info = get_series_info(uuid)
        if self.id is None:
            self.id = info["id"]

        # erase existing data
        erased = False
        for path in (self.data_path, self.meta_path):
            if os.path.exists(path):
                erased = True
                os.remove(path)
        if erased:
            logger.warning(
                "series %s was already in database, existing data was erased (%s)" % (self.name, self.base_path))

        # prepare directory tree if needed
        self.prepare_directory_tree()

        # write meta
        self.set_meta(**dict([(k, info[k]) for k in META_FIELDS]))

        # select data
        rep = client.detail_route("odata/series", info["id"], "GET", "select", return_json=False)

        # transform to pandas series
        se = pd.read_json(rep, orient="split", typ="series")

        # put storage name
        se.name = self.storage_name

        # write data
        se_io = self.get_se_io(human_readable_name=False)
        se_io.append(se)

    def __str__(self):
        if os.path.exists(self.meta_path):
            meta = self.get_meta()
            meta_content_xml = "<meta>\n"
            for k, v in sorted(meta.items()):
                meta_content_xml += textwrap.indent("<%s>%s</%s>\n" % (k, v, k), "\t")
            meta_content_xml += "</meta>\n"

            se_io = self.get_se_io()
            data_content_xml = """<data>
    <start>%s</start>
    <end>%s</end>
</data>
""" % (se_io.start(), se_io.end())
        else:
            meta_content_xml = "<meta></meta>\n"
            data_content_xml = "<data></data>\n"

        return """<local_series>
    <name>{name}</name>
{meta}{data}</local_series>""".format(
            name=self.name,
            meta=textwrap.indent(meta_content_xml, "\t"),
            data=textwrap.indent(data_content_xml, "\t")
        )
