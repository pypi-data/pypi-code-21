def get_subclasses(parent_class):
    subclasses = set()

    def find_subclasses(cls):
        for subclass in cls.__subclassess__():
            if subclass not in subclasses:
                subclasses.add(subclass)
                find_subclasses(subclass)

    find_subclasses(parent_class)
    return subclasses
