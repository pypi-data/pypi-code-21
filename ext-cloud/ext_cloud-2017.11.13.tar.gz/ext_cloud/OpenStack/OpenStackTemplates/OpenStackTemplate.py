from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls
from ext_cloud.BaseCloud.BaseTemplates.BaseTemplates import BaseTemplatescls


class OpenStackTemplatecls(OpenStackBaseCloudcls, BaseTemplatescls):

    def state(self):
        pass

    def validate_template(self):
        pass

    def create_stack(self):
        pass

    def delete_stack(self):
        pass

    def update_stack(self):
        pass
