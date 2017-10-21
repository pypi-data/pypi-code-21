from .GMailSyncInfo_16Endpoint import GMailSyncInfo_16Endpoint
from .MicrosoftExchangeSyncInfo_16Endpoint import MicrosoftExchangeSyncInfo_16Endpoint
from .UserSettingsGMailSync_14Endpoint import UserSettingsGMailSync_14Endpoint
from .UserSettingsGMailSync_16Endpoint import UserSettingsGMailSync_16Endpoint
from .UserSettingsLocationTracking_20Endpoint import UserSettingsLocationTracking_20Endpoint
from .UserSettingsMicrosoftExchangeSync_16Endpoint import UserSettingsMicrosoftExchangeSync_16Endpoint
from .UserSettingsNotification_20Endpoint import UserSettingsNotification_20Endpoint
from .UserSettings_14Endpoint import UserSettings_14Endpoint


class UserSettingsEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def GMailSyncInfo_16(self):
        """
        :return: GMailSyncInfo_16Endpoint
        """
        return GMailSyncInfo_16Endpoint(self._api_client)
        
    @property
    def MicrosoftExchangeSyncInfo_16(self):
        """
        :return: MicrosoftExchangeSyncInfo_16Endpoint
        """
        return MicrosoftExchangeSyncInfo_16Endpoint(self._api_client)
        
    @property
    def UserSettingsGMailSync_14(self):
        """
        :return: UserSettingsGMailSync_14Endpoint
        """
        return UserSettingsGMailSync_14Endpoint(self._api_client)
        
    @property
    def UserSettingsGMailSync_16(self):
        """
        :return: UserSettingsGMailSync_16Endpoint
        """
        return UserSettingsGMailSync_16Endpoint(self._api_client)
        
    @property
    def UserSettingsLocationTracking_20(self):
        """
        :return: UserSettingsLocationTracking_20Endpoint
        """
        return UserSettingsLocationTracking_20Endpoint(self._api_client)
        
    @property
    def UserSettingsMicrosoftExchangeSync_16(self):
        """
        :return: UserSettingsMicrosoftExchangeSync_16Endpoint
        """
        return UserSettingsMicrosoftExchangeSync_16Endpoint(self._api_client)
        
    @property
    def UserSettingsNotification_20(self):
        """
        :return: UserSettingsNotification_20Endpoint
        """
        return UserSettingsNotification_20Endpoint(self._api_client)
        
    @property
    def UserSettings_14(self):
        """
        :return: UserSettings_14Endpoint
        """
        return UserSettings_14Endpoint(self._api_client)
        