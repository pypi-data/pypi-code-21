import configparser
import logging


class Configuration:
    def __init__(self, config_file_path):
        self.config = dict()
        self._config_parser = configparser.ConfigParser()

        try:
            config_file = open(config_file_path, "r")
            self._config_parser.read_file(config_file)
        except (OSError, IOError) as e:
            err_msg = "Error reading configuration from file " + \
                      config_file_path
            raise ValueError(err_msg, e)

        try:
            logging.info("Reading configuration...")
            self.__read_language_configuration()
            self.__read_twitter_configuration()
            self.__read_mongodb_configuration()
            logging.info("Configuration read correctly.")
        except Exception as e:
            err_msg = "Error reading configuration parameters from file " + \
                      config_file_path
            raise ValueError(err_msg, e)

    def __read_language_configuration(self):
        logging.debug("Reading language configuration...")

        lang_conf = self.config["language"] = {}

        lang_conf["locale"] = self._config_parser.get(
            "language", "locale")

        logging.debug("Language configuration read correctly.")

    def __read_twitter_configuration(self):
        logging.debug("Reading Twitter configuration...")

        twitter_conf = self.config["twitter"] = {}

        twitter_conf["consumer_key"] = self._config_parser.get(
            "twitter", "consumer_key")
        twitter_conf["consumer_secret"] = self._config_parser.get(
            "twitter", "consumer_secret")
        twitter_conf["access_token_key"] = self._config_parser.get(
            "twitter", "access_token_key")
        twitter_conf["access_token_secret"] = self._config_parser.get(
            "twitter", "access_token_secret")

        logging.debug("Twitter configuration read correctly.")

    def __read_mongodb_configuration(self):
        logging.debug("Reading MongoDB configuration...")

        mongo_conf = self.config["mongodb"] = {}

        mongo_conf["uri"] = self._config_parser.get("mongodb", "uri")
        mongo_conf["database"] = self._config_parser.get("mongodb", "database")
        mongo_conf["user"] = self._config_parser.get("mongodb", "user")
        mongo_conf["password"] = self._config_parser.get("mongodb", "password")
        mongo_conf["mechanism"] = self._config_parser.get("mongodb",
                                                          "mechanism")

        logging.debug("MongoDB configuration read correctly.")
