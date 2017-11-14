"""Managing users and group membership in the container."""

from stuffer.core import Action


class AddToGroup(Action):
    """Add a user to a group.

    Parameters
    ----------
    user
        Name of user.
    group
        Name of group.
    """

    def __init__(self, user, group):
        super().__init__()
        self.user = user
        self.group = group

    def command(self):
        return "adduser {} {}".format(self.user, self.group)

