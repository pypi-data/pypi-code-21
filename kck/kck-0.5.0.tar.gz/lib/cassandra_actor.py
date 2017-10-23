import datetime
import dateutil
from cassandra.cluster import Cluster, NoHostAvailable
from cassandra.connection import ConnectionException
from dateutil.parser import parser

from kck.lib.exceptions import KCKKeyNotRegistered, KCKKeyNotSetException
from kck.lib.kck_database import KCKDatabase
from kck.lib.kck_primer import KCKPrimer
from kck.lib.kck_updater import KCKUpdater
from kck.lib.yaml_primer import KCKYamlPrimer
from kck.lib.yaml_updater import KCKYamlUpdater
import json
from .config import kck_config_lookup


class CassandraActor(object):
    prim_cache_name = None
    sec_cache_name = None
    update_queue_name = None
    refresh_queue_name = None
    refresh_counter_name = None
    cluster = None
    session = None
    cache_obj = None
    data_obj = None
    updaters = None
    primers = None
    keysep = "/"

    def init(self, inhibit_framework_registration=False, cache_obj=None, data_obj=None):
        try:
            self.session = self.cluster.connect(kck_config_lookup("cassandra", "keyspace"))
        except (ConnectionException, NoHostAvailable):
            self.cluster.shutdown()
            self._cache_create_keyspace(kck_config_lookup("cassandra", "keyspace"))
            self.cluster = Cluster(kck_config_lookup("cassandra", "hosts"))
            self.session = self.cluster.connect(kck_config_lookup("cassandra", "keyspace"))
        self._cache_create_table(self.prim_cache_name)
        self._cache_create_table(self.sec_cache_name)
        self._queued_updates_create_table(self.update_queue_name)
        self._queued_refreshes_create_tables(self.refresh_queue_name)

        self.cache_obj = cache_obj
        self.data_obj = data_obj

        if not inhibit_framework_registration:
            self._register_updaters()
            self._register_primers()

        self._register_hooks()

    def primitive_init(self):
        self.prim_cache_name = kck_config_lookup("cassandra", "tables", "primary_cache")
        self.sec_cache_name = kck_config_lookup("cassandra", "tables", "secondary_cache")
        self.update_queue_name = kck_config_lookup("cassandra", "tables", "queued_updates")
        self.refresh_queue_name = kck_config_lookup("cassandra", "tables", "queued_refreshes")
        self.refresh_counter_name = kck_config_lookup("cassandra", "tables", "queued_refreshes_counter")
        self.cluster = Cluster(kck_config_lookup("cassandra", "hosts"))

        self.updaters = {}
        self.primers = {}

    def primer_obj(self, key):
        try:
            return self.cache_obj.primers[key.split(self.keysep)[0]]
        except KeyError:
            raise KCKKeyNotRegistered(key)

    def updater_obj(self, key):
        return self.data_obj.updaters[key.split(self.keysep)[0]]

    def do_processes(self):

        type_map = dict(
            sql=self._sql_process,
            key=self._key_process
        )

        for key, actor_obj in self.cache_obj.primers.items():
            try:
                processes = actor_obj.processes
            except AttributeError:
                continue

            for process_name, process_dict in processes.items():
                print("process for key: {}, name: {}".format(key, process_name))
                if process_dict["type"] in type_map:
                    type_map[process_dict["type"]](
                        process_name=process_name,
                        process_dict=process_dict,
                        actor_obj=actor_obj
                    )

    def queued_refresh_data(self, query=None):
        # # get queue names from config
        # refresh_queue_name = kck_config_lookup(
        #     "cassandra", "tables", "queued_refreshes"
        # )
        # refresh_counter_name = kck_config_lookup(
        #     "cassandra", "tables", "queued_refreshes_counter"
        # )

        # async refresh queue query
        q_hints = "select kck_key, kck_hints from {}".format(self.refresh_queue_name)
        pq_hints = self.session.prepare(q_hints)
        fut_hints = self.session.execute_async(pq_hints)

        # async refresh counters query
        q_counts = "select kck_key, refresh_request_counter from {}".format(
            self.refresh_counter_name
        )
        pq_counts = self.session.prepare(q_counts)
        fut_counts = self.session.execute_async(pq_counts)

        queue_dict = {}
        for key_hints_tuple in fut_hints.result():
            key, hints = key_hints_tuple
            queue_dict[key] = {"hints": hints}

        for key_count_tuple in fut_counts.result():
            key, cnt = key_count_tuple
            if key not in queue_dict:
                queue_dict[key] = dict(count=cnt)
            else:
                queue_dict[key]["count"] = cnt

        return queue_dict

    def queue_refresh_count(self, key):
        q = "select refresh_request_counter from {} where kck_key= ?".format(self.refresh_counter_name)
        pq = self.session.prepare(q)
        future = self.session.execute_async(pq)
        ret = future.result()[0]
        return ret

    def perform_queued_refreshes(self, query=None):

        refresh_data = self.queued_refresh_data(query)

        for key, refresh_request_entry in refresh_data.items():
            hints = None
            if "hints" in refresh_request_entry and \
                    refresh_request_entry["hints"] is not None:
                hints = refresh_request_entry["hints"]
            self.cache_obj.refresh(key, hints)

    def raw_queue_update(self, key, data):
        q = "insert into {} (kck_key, kck_data) values (?, ?)".format(self.update_queue_name)
        pq = self.session.prepare(q)
        future = self.session.execute_async(pq, (key, data))
        return future.result()

    def raw_cache_put(self, key, tbl, val, version=None, check_last_version=None, expire=None, modified=None):
        """sets the value associated with <key> in the table <tbl>.
           if callback_func is defined, the query is executed asynchronously
           and the future resulting from the call to execute_async method"""

        new_version = version if version is not None else self.gen_new_version()

        ttl_clause = "" if expire is None else "using ttl {} ".format(expire.seconds)
        current_timestamp = datetime.datetime.utcnow() if modified == None else modified

        # --- if <check_last_version> is None, then don't do the version check
        if check_last_version is None:

            upsert_query = "update {} {}set kck_value = ?, version = ?, modified = ? where kck_key = ?".format(tbl, ttl_clause)
            prepared_query = self.session.prepare(upsert_query)
            future = self.session.execute_async(prepared_query, (val, new_version, current_timestamp, key))
            return future.result()

        # --- update only if version = <check_last_version>
        upsert_query = "update {} {}set kck_value = ?, version = ?, modified = ? where kck_key = ? if version = ?".format(tbl, ttl_clause)
        prepared_query = self.session.prepare(upsert_query)

        future = self.session.execute_async(prepared_query, (val, new_version, current_timestamp, key, check_last_version))

        return future.result()

    def raw_cache_delete(self, key, tbl):
        delete_query_str = "delete from {} where kck_key = ?".format(tbl)

        prepared_query = self.session.prepare(delete_query_str)

        future = self.session.execute_async(prepared_query, (key,))
        return future.result()

    def raw_cache_get(self, key, tbl):
        """looks up the value associated with <key> in the table <tbl>.
           if callback_func is defined, the query is executed asynchronously
           and the future resulting from the call to execute_async method"""
        prepared_query = self.session.prepare(
            "select kck_value, version, modified from {} where kck_key = ?".format(
                tbl
            )
        )
        future = self.session.execute_async(prepared_query, (key,))

        ret =  future.result()
        return ret

    def raw_queue_refresh(self, key, hints=None):

        # increment refresh counter
        q_inc = "update {} set refresh_request_counter = refresh_request_counter + 1 where kck_key = ?".format(self.refresh_counter_name, key)
        pq_inc = self.session.prepare(q_inc)
        future_inc = self.session.execute_async(pq_inc, (key,))

        # if there's no hints, incrementing the refresh counter is good enough
        if hints is None:
            ret =  future_inc.result()
            return ret

        # update the refresh table with hints
        q_hints = "update {} set kck_hints=kck_hints".format(self.refresh_queue_name) + \
                  ' + ' + '{' + "'" + self._to_encoded_json(hints) + "'" + '}' + \
                  " where kck_key = ?"
        pq_hints = self.session.prepare(q_hints)
        if hints is not None:
            if "modified" in hints:
                hints["modified"] = str(hints["modified"])
        future_hints = self.session.execute_async(pq_hints, (key,))

        # return
        ret = future_hints.result()
        return ret

    def _to_encoded_json(self, d):
        def serialize_datetime(obj):
            if isinstance(obj, (datetime.datetime, datetime.date)):
                return obj.isoformat()
            raise TypeError("Type %s not serializable" % type(obj))
        return json.dumps(d, default=serialize_datetime)


    def _key_process(self, process_name, process_dict, actor_obj):

        if "hooks" in process_dict:

            hooks = process_dict["hooks"]

            if "pre" in hooks and hooks["pre"] is not None:
                for pre_hook in hooks["pre"]:
                    pre_hook(self)

            if "value" in hooks and hooks["value"] is not None:
                for value_hook in hooks["value"]:
                    if "key_attribute" in process_dict:
                        key_ptr = getattr(actor_obj, process_dict["key_attribute"])
                        if callable(key_ptr):
                            key = key_ptr()
                        else:
                            key = key_ptr

                    if key is not None:
                        try:
                            value_hook(actor_obj, self.cache_obj.get(key)["value"])
                        except KCKKeyNotSetException:
                            pass

    def _sql_process(self, process_name, process_dict, actor_obj):

        if "hooks" in process_dict:

            hooks = process_dict["hooks"]

            if "pre" in hooks and hooks["pre"] is not None:
                for pre_hook in hooks["pre"]:
                    pre_hook(self)

            if "row" in hooks and hooks["row"] is not None:
                rowset = KCKDatabase.query(
                    process_dict["database"],
                    process_dict["query"]
                )
                for row in rowset:
                    for row_hook in hooks["row"]:
                        row_hook(self, row)

            if "post" in hooks and hooks["post"] is not None:
                for post_hook in hooks["post"]:
                    post_hook(self)

    def _register_primers(self):
        """registers yaml and class-based primers"""
        KCKPrimer.register_primers(self.cache_obj)
        KCKYamlPrimer.register_primers(self.cache_obj)

    def _register_updaters(self):
        """registers yaml and class-based updaters"""
        KCKYamlUpdater.register_updaters(self.data_obj)
        KCKUpdater.register_updaters(self.data_obj)

    def _register_hooks(self):

        # register primer dependencies
        for _, p in self.primers.items():
            p.register_hooks()

        # register updater dependencies
        for _, u in self.updaters.items():
            u.register_hooks()

    def _cache_create_table(self, tbl):
        ks = kck_config_lookup("cassandra", "keyspace")
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS {}.{} (
              kck_key text PRIMARY KEY,
              kck_value blob,
              version int,
              modified timestamp,
            )
        """.format(ks, tbl))

    def _queued_updates_create_table(self, tbl):
        ks = kck_config_lookup("cassandra", "keyspace")
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS {}.{} (
              kck_key text PRIMARY KEY,
              kck_data blob,
              version int
            )
        """.format(ks, tbl))

    # counter explanation: https: // stackoverflow.com / questions / 23145817 / update - a - cassandra - integer - column - using - cql
    def _queued_refreshes_create_tables(self, tbl):
        ks = kck_config_lookup("cassandra", "keyspace")

        self.session.execute("""
            CREATE TABLE IF NOT EXISTS {}.{} (
              kck_key text PRIMARY KEY,
              kck_hints set<text>,
              version int
            )
        """.format(ks, tbl))

        self.session.execute("""
            CREATE TABLE IF NOT EXISTS {}.{} (
              kck_key text PRIMARY KEY,
              refresh_request_counter counter
            )
        """.format(ks, tbl + "_counter"))

    @staticmethod
    def _cache_create_keyspace(keyspace_name):
        cluster = Cluster(kck_config_lookup("cassandra", "hosts"))
        create_keyspace_session = cluster.connect()
        create_keyspace_session.execute("""
            CREATE KEYSPACE IF NOT EXISTS {}
            WITH REPLICATION = {{
               'class' : 'SimpleStrategy',
               'replication_factor' : 1
            }}
        """.format(keyspace_name))
        create_keyspace_session.shutdown()
        cluster.shutdown()

