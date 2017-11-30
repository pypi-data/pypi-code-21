class DegradeCommand(object):
    def __init__(self, resources):
        self.__resources = resources

    def __run(self, resource):
        if resource._opted_in:
            resource.state = 0
            print(resource.path)

        for child in resource.children:
            self.__run(child)

    def run(self):
        for resource in self.__resources:
            self.__run(resource)
