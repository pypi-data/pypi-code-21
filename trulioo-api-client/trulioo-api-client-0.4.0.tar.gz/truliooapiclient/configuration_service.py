class ConfigurationService:
    def __init__(self, client):
        self.client = client

    def GetConsents(self, configurationName, countryCode, headers=None,
                    query_params=None, content_type="application/json"):
        """
        This method retrieves the consents required for data sources currently configured in your account configuration. The response for this method contains a collection of strings that Verify method's ConsentForDataSources field expects to perform a verification using those data sources. A failure to provide an element from the string collection will lead to a 1005 service error.
        It is method for GET /configuration/v1/consents/{configurationName}/{countryCode}
        """
        uri = self.client.base_url + "/configuration/v1/consents/" + configurationName + "/" + countryCode
        return self.client.get(uri, None, headers, query_params, content_type)

    def GetCountryCodes(self, configurationName, headers=None, query_params=None, content_type="application/json"):
        """
        This method retrieves all the countries that are available to perform a verification.
        It is method for GET /configuration/v1/countrycodes/{configurationName}
        """
        uri = self.client.base_url + "/configuration/v1/countrycodes/" + configurationName
        return self.client.get(uri, None, headers, query_params, content_type)

    def GetCountrySubdivisions(self, countryCode, headers=None, query_params=None, content_type="application/json"):
        """
        Gets the provinces states or other subdivisions for a country, mostly matches ISO 3166-2
        It is method for GET /configuration/v1/countrysubdivisions/{countryCode}
        """
        uri = self.client.base_url + "/configuration/v1/countrysubdivisions/" + countryCode
        return self.client.get(uri, None, headers, query_params, content_type)

    def GetDocumentTypes(self, countryCode, headers=None, query_params=None, content_type="application/json"):
        """
        Gets the document types available for a country.
        It is method for GET /configuration/v1/documentTypes/{countryCode}
        """
        uri = self.client.base_url + "/configuration/v1/documentTypes/" + countryCode
        return self.client.get(uri, None, headers, query_params, content_type)

    def GetFields(self, configurationName, countryCode, headers=None,
                  query_params=None, content_type="application/json"):
        """
        Generates json schema for the API, the schema is dynamic based on the country and configuration you are using. http://json-schema.org/documentation.html
        It is method for GET /configuration/v1/fields/{configurationName}/{countryCode}
        """
        uri = self.client.base_url + "/configuration/v1/fields/" + configurationName + "/" + countryCode
        return self.client.get(uri, None, headers, query_params, content_type)

    def GetTestEntities(self, configurationName, countryCode, headers=None,
                        query_params=None, content_type="application/json"):
        """
        Gets the test entities configured for your product and country.
        It is method for GET /configuration/v1/testentities/{configurationName}/{countryCode}
        """
        uri = self.client.base_url + "/configuration/v1/testentities/" + configurationName + "/" + countryCode
        return self.client.get(uri, None, headers, query_params, content_type)
