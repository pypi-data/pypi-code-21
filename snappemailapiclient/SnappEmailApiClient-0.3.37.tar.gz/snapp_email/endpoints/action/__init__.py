from .ActionDeleteMention_18Endpoint import ActionDeleteMention_18Endpoint
from .ActionDeletePinNotification_18Endpoint import ActionDeletePinNotification_18Endpoint
from .ActionDeleteQuestion_18Endpoint import ActionDeleteQuestion_18Endpoint
from .ActionDeleteReminder_18Endpoint import ActionDeleteReminder_18Endpoint
from .ActionDelete_18Endpoint import ActionDelete_18Endpoint
from .ActionFinishWorkflow_18Endpoint import ActionFinishWorkflow_18Endpoint
from .ActionHideStream_18Endpoint import ActionHideStream_18Endpoint
from .ActionNextStep_18Endpoint import ActionNextStep_18Endpoint
from .ActionSetReminder_18Endpoint import ActionSetReminder_18Endpoint
from .ActionableResourceAvailability_20Endpoint import ActionableResourceAvailability_20Endpoint
from .ActionableResourceOverview_20Endpoint import ActionableResourceOverview_20Endpoint
from .ActionableResourceOverview_21Endpoint import ActionableResourceOverview_21Endpoint
from .ActionableResourceOverview_22Endpoint import ActionableResourceOverview_22Endpoint
from .ActionableResource_20Endpoint import ActionableResource_20Endpoint
from .ActionableResource_21Endpoint import ActionableResource_21Endpoint
from .ActionableResource_22Endpoint import ActionableResource_22Endpoint
from .ListOfActionableResourcesPage_20Endpoint import ListOfActionableResourcesPage_20Endpoint
from .ListOfActionableResourcesPage_21Endpoint import ListOfActionableResourcesPage_21Endpoint
from .ListOfActionableResourcesPage_22Endpoint import ListOfActionableResourcesPage_22Endpoint


class ActionEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def ActionDeleteMention_18(self):
        """
        :return: ActionDeleteMention_18Endpoint
        """
        return ActionDeleteMention_18Endpoint(self._api_client)
        
    @property
    def ActionDeletePinNotification_18(self):
        """
        :return: ActionDeletePinNotification_18Endpoint
        """
        return ActionDeletePinNotification_18Endpoint(self._api_client)
        
    @property
    def ActionDeleteQuestion_18(self):
        """
        :return: ActionDeleteQuestion_18Endpoint
        """
        return ActionDeleteQuestion_18Endpoint(self._api_client)
        
    @property
    def ActionDeleteReminder_18(self):
        """
        :return: ActionDeleteReminder_18Endpoint
        """
        return ActionDeleteReminder_18Endpoint(self._api_client)
        
    @property
    def ActionDelete_18(self):
        """
        :return: ActionDelete_18Endpoint
        """
        return ActionDelete_18Endpoint(self._api_client)
        
    @property
    def ActionFinishWorkflow_18(self):
        """
        :return: ActionFinishWorkflow_18Endpoint
        """
        return ActionFinishWorkflow_18Endpoint(self._api_client)
        
    @property
    def ActionHideStream_18(self):
        """
        :return: ActionHideStream_18Endpoint
        """
        return ActionHideStream_18Endpoint(self._api_client)
        
    @property
    def ActionNextStep_18(self):
        """
        :return: ActionNextStep_18Endpoint
        """
        return ActionNextStep_18Endpoint(self._api_client)
        
    @property
    def ActionSetReminder_18(self):
        """
        :return: ActionSetReminder_18Endpoint
        """
        return ActionSetReminder_18Endpoint(self._api_client)
        
    @property
    def ActionableResourceAvailability_20(self):
        """
        :return: ActionableResourceAvailability_20Endpoint
        """
        return ActionableResourceAvailability_20Endpoint(self._api_client)
        
    @property
    def ActionableResourceOverview_20(self):
        """
        :return: ActionableResourceOverview_20Endpoint
        """
        return ActionableResourceOverview_20Endpoint(self._api_client)
        
    @property
    def ActionableResourceOverview_21(self):
        """
        :return: ActionableResourceOverview_21Endpoint
        """
        return ActionableResourceOverview_21Endpoint(self._api_client)
        
    @property
    def ActionableResourceOverview_22(self):
        """
        :return: ActionableResourceOverview_22Endpoint
        """
        return ActionableResourceOverview_22Endpoint(self._api_client)
        
    @property
    def ActionableResource_20(self):
        """
        :return: ActionableResource_20Endpoint
        """
        return ActionableResource_20Endpoint(self._api_client)
        
    @property
    def ActionableResource_21(self):
        """
        :return: ActionableResource_21Endpoint
        """
        return ActionableResource_21Endpoint(self._api_client)
        
    @property
    def ActionableResource_22(self):
        """
        :return: ActionableResource_22Endpoint
        """
        return ActionableResource_22Endpoint(self._api_client)
        
    @property
    def ListOfActionableResourcesPage_20(self):
        """
        :return: ListOfActionableResourcesPage_20Endpoint
        """
        return ListOfActionableResourcesPage_20Endpoint(self._api_client)
        
    @property
    def ListOfActionableResourcesPage_21(self):
        """
        :return: ListOfActionableResourcesPage_21Endpoint
        """
        return ListOfActionableResourcesPage_21Endpoint(self._api_client)
        
    @property
    def ListOfActionableResourcesPage_22(self):
        """
        :return: ListOfActionableResourcesPage_22Endpoint
        """
        return ListOfActionableResourcesPage_22Endpoint(self._api_client)
        