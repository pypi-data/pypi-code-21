import sys
import lbppy


class Resource():
    def __init__(self, url, results):
        self.results = results


    @classmethod
    def find(cls, url):
        query_obj = lbppy.Query()
        cls.results = query_obj.query(url)
        return cls.create(cls, url, cls.results)
    def create(cls, url, results):
        type = ""
        for result in cls.results["results"]["bindings"]:
            if (result["p"]["value"] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"):
                type = result["o"]["value"].split("/").pop()
        type = type.capitalize()

        klass = getattr(sys.modules['lbppy'], type)

        return klass(url, results)


    def values(self, predicate):
        predicates = []
        for result in self.results["results"]["bindings"]:
            if (result["p"]["value"] == predicate):
                predicates.append(lbppy.ResourceIdentifier(result["o"]["value"]))

        if len(predicates) > 1:
            return predicates
        elif len(predicates) == 1:
            return predicates[0]
        else:
            return "no results found"

    def title(self):
        return self.values("http://purl.org/dc/elements/1.1/title").to_s()
    def description(self):
        return self.values("http://purl.org/dc/elements/1.1/description")
    def has_parts(self):
        return self.values("http://purl.org/dc/terms/hasPart")
    def is_part_of(self):
        return self.values("http://purl.org/dc/terms/isPartOf")

    def type(self):
        return self.values("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    def next(self):
        return self.values("http://scta.info/property/next")
    def previous(self):
        return self.values("http://scta.info/property/previous")
    def inbox(self):
        return self.values("http://www.w3.org/ns/ldp#inbox")
