"""
A schema using HAL JSON linking conventions.

"""
from microcosm_resourcesync.following import FollowMode
from microcosm_resourcesync.schemas.base import Link, Schema


class HALSchema(Schema):
    """
    A schema that implements HAL JSON linking.

    """
    @property
    def embedded(self):
        return self.get("items", [])

    def links(self, follow_mode):
        return [
            Link(relation, uri)
            for relation, uri in self.iter_links()
            if self.should_follow(relation, uri, follow_mode)
        ]

    @property
    def parents(self):
        return [
            uri
            for relation, uri in self.iter_links()
            if relation.startswith("parent:")
        ]

    def should_follow(self, relation, uri, follow_mode):
        """
        Compute whether a link should be followed.

        We use the convention that a link prefixed with "child:" is a non-parent link.

        """
        if follow_mode == FollowMode.NONE:
            return False

        if relation == "self":
            # don't follow self links
            return False

        if follow_mode == FollowMode.ALL:
            return True

        if follow_mode == FollowMode.CHILD and relation.startswith("child:"):
            return True

        if follow_mode in (FollowMode.CHILD, FollowMode.PAGE) and relation in ("next", "prev"):
            return True

        return False

    @property
    def type(self):
        """
        We assume that the URI is of the form: `https://example.com/path/to/<type>/<id>`

        """
        return self.uri.split("/")[-2]

    @property
    def uri(self):
        """
        We assume that the resource has a valid HAL self link.

        """
        return self["_links"]["self"]["href"]

    def iter_links(self):
        for relation, links in self["_links"].items():
            if isinstance(links, list):
                for link in links:
                    yield relation, link["href"]
            else:
                link = links["href"]
                yield relation, link
