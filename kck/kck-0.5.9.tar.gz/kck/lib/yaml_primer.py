import os
import datetime

from jsonpath_ng import jsonpath, parse

from .config import kck_config_lookup
from .kck_primer import KCKPrimer, QUERY_TYPE_DICTS, QUERY_TYPE_ROWS
from .yaml_reader import YAMLReader

class KCKYamlPrimer(KCKPrimer, YAMLReader):

    refresh_after_updates = []
    refresh_after_primes = []


    def __init__(self, yaml_filepath):

        self.filepath = yaml_filepath

        self._proc_primer_yaml()


    @classmethod
    def register_primers(cls, cache_obj):
        """register all yaml-based primers in the primers dir"""

        def fnfilter(filepath):
            # print("fp: {}, fpl: {}".format(filepath, filepath[-3:]))
            if filepath[-4:] == ".yml":
                return True
            return False

        def proc_primer_yaml(filepath):
            cache_obj.register_primer(
                os.path.basename(filepath)[:-4],
                KCKYamlPrimer(filepath)
            )

        cls.proc_files_in_dirpath(
            cls.make_relpath_absolute(kck_config_lookup("kck", "primers_dirpath")),
            fnfilter,
            proc_primer_yaml
        )

    def register_hooks(self):

        # register after_primes refreshes



        super(KCKYamlPrimer, self).register_hooks()

        cache_obj = self.get_cache()

        # add hooks for refresh-after-primes

        refresh_str_format = "{}{}".format(self.name, self.keysep)+"{}"

        def refresh_primer_val(key=None, hints=None, param_key=None):
            print("refresh_primer_val(key={}, hints={}, param_key={})".format(key, hints, param_key))
            if bool(hints["success"]):
                #
                # - key is the key that just got refreshed, triggering the hook
                # - param_key is the key that was listed in refresh/after_primes
                #

                # --- build the keystr to send to the cache_obj refresh() method

                # get the param dict from the refresh_str_format
                primer_obj = cache_obj.primer_obj(refresh_str_format.format(""))

                # get the param dict that describes dependent key in terms of current key
                param_dict = self.dependency_key_to_param_dict(param_key, key)

                refresh_key = refresh_str_format.format(self.param_dict_to_key(param_dict))

                self.get_cache().refresh(
                    key=refresh_key,
                    hints=hints,
                    queued=True
                )

        for key_tmpl in self.refresh_after_primes:

            # param_dict = self.dependency_key_to_param_dict(key_tmpl, key)

            # get the primer obj for the key
            target_primer_obj = cache_obj.primer_obj(key_tmpl)

            # add refresh_primer_val() as a post-prime hook
            depkey = self.dependency_key()
            target_primer_obj.add_hook("post_prime", key_tmpl, refresh_primer_val)

        for key_tmpl in self.refresh_after_updates:
            u = cache_obj.updater_obj(key_tmpl)
            u.add_hook("post_update", key_tmpl, refresh_primer_val)

    def _proc_primer_yaml(self):

        p = self.read_yaml(self.filepath)

        # the key is the same as the yaml file (minus the .yml)
        self.keys = [os.path.basename(self.filepath)[:-4]]

        self.database = p["database"]

        self.parameters = p["parameters"] if "parameters" in p else []

        self.expire = datetime.timedelta(seconds=p["expire_seconds"]) if "expire_seconds" in p else None

        self.query_template = p["query"]["template"]

        self.query_type = QUERY_TYPE_DICTS if "type" in p["query"] and p["query"]["type"] == "dicts" else QUERY_TYPE_ROWS

        if "process_result" in p["query"]:
            if "jsonpath_first" in p["query"]["process_result"]:
                jpparser = parse(p["query"]["process_result"]["jsonpath_first"])
                self.result_filter = lambda x: jpparser.find(x)[0].value if x is not None and bool(x) else None

        if "refresh" in p:
            try:
                self.refresh_after_primes = p["refresh"]["after_primes"]
            except KeyError:
                pass

            try:
                self.refresh_after_updates = p["refresh"]["after_updates"]
            except KeyError:
                pass

            try:
                self.domain_key = p["refresh"]["domain_key"]
            except KeyError:
                pass

