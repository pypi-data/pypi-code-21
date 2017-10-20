import os
import requests
import time
import tempfile

import utils


class Client:
    def __init__(self, client_id, client_secret):
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__cached_auth = None
        #: The API host location
        self.host = "api.audionamix.com"
        self.audiofile_host = "audiofile.audionamix.com"

    @property
    def __auth(self):
        if self.__cached_auth != None:
            # TODO: check if token is still valid or request a new one
            return self.__cached_auth

        r = requests.post("https://audionamix.auth0.com/oauth/token", data={
          "client_id": self.__client_id,
          "client_secret": self.__client_secret,
          "audience": "https://*.audionamix.com/",
          "grant_type": "client_credentials"
        })
        r.raise_for_status()

        access_token = r.json()["access_token"]
        token_type = r.json()["token_type"]

        self.__cached_auth = {"Authorization": token_type + " " + access_token}
        return self.__cached_auth

    @property
    def __userid(self):
        return self.__client_id + "@clients"

    def __call_progress_handler(self, value, kwargs):
        if "progress_handler" in kwargs.keys():
            kwargs["progress_handler"](value)

    def upload_source_file(self, source_path, **kwargs):
        """
        Upload the source file to the Audionamix storage
        Args:
            source_path: the local path to the source file
            progress_handler: optional, progress_handler(int) used to report the
              upload progress
        Return:
            the url to the upload file
        """
        source_url = utils.make_url("https",
                                    self.audiofile_host,
                                    "/" + self.__userid + "/")
        source_url += os.path.basename(source_path)
        self.__call_progress_handler(0, kwargs)

        with open(source_path, 'rb') as source_file:
            r = requests.put(source_url,
                             data=source_file,
                             headers=self.__auth)
            r.raise_for_status()
        self.__call_progress_handler(100, kwargs)

        return source_url

    def download(self, url, **kwargs):
        """
        Download the source file from url
        Args:
            url: the location of the file to download
            progress_handler: optional, progress_handler(int) used to report the
              download progress
        """
        handle, dst_path = tempfile.mkstemp(suffix=".wav")
        os.close(handle)

        r = requests.get(url,
                         headers=self.__auth,
                         stream=True)
        r.raise_for_status()
        total_size = int(r.headers['Content-Length'])
        current_size = 0
        with open(dst_path, 'wb') as dst_file:
            for chunk in r:
                dst_file.write(chunk)
                current_size += len(chunk)
                self.__call_progress_handler(
                    float(current_size) / total_size * 100,
                    kwargs
                )

        return dst_path


    def __run_algorithm(self, endpoint, data, kwargs):
        r = requests.post(endpoint, data, headers=self.__auth)
        r.raise_for_status()
        tracking_url = r.json()["url"]

        while True:
            time.sleep(1)
            status = requests.get(tracking_url,
                                  headers=self.__auth)
            status.raise_for_status()
            self.__call_progress_handler(status.json()["progress"], kwargs)

            if status.json()["status"] == "Failed":
                raise Exception("Tracking error: " + status.json()["error"])

            if status.json()["status"] == "Success":
                return status.json()["result"]


    def track_pitch(self, source_url, **kwargs):
        """
        Tracks the pitch from the given source file
        Args:
            source_url: the url to the desired source file
            progress_handler: optional, progress_handler(int) used to report the
              algorithm progress
        Return:
            The JSON array of array representing the tracked pitch of the voice
        """
        return self.__run_algorithm(
            utils.make_url("https", self.host, "/api/v2/bigdipper/"),
            {"source": source_url},
            kwargs)

    def track_consonants(self, source_url, **kwargs):
        """
        Tracks the Consonants from the given source file
        Args:
            source_url: the url to the desired source file
            progress_handler: optional, progress_handler(int) used to report the
              algorithm progress
        Return:
            The JSON arrayrepresenting timestamps of consonants
        """
        return self.__run_algorithm(
            utils.make_url("https", self.host, "/api/v2/consonant/"),
            {"source": source_url},
            kwargs)

    def extract_vocals(self, source_url, consonants, pitch, **kwargs):
        """
        extract the vocals out of the given source file
        Args:
            source_url: the url to the desired source file
            consonants: the result of pre analyzed consonants
            pitch: the result of big dipper analysis
            progress_handler: optional, progress_handler(int) used to report the
              algorithm progress
        Return:
            The url to the extracted vocals
        """
        return self.__run_algorithm(
            utils.make_url("https", self.host, "/api/v2/vex/"),
            {
                "source": source_url,
                "pitch": pitch,
                "consonants": consonants
            },
            kwargs)

    def remove_drums(self, source_url, **kwargs):
        """
        remove the drums from the source file
        Args:
            source_url: the url to the desired source file
            progress_handler: optional, progress_handler(int) used to report the
              algorithm progress
        Return:
            The url to the mix with removed drums
        """
        return self.__run_algorithm(
            utils.make_url("https", self.host, "/api/v2/drumex/"),
            {
                "source": source_url
            },
            kwargs)
