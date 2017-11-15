"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.brew.brew_state import BrewState
from pubkeeper.utils.logging import get_logger


class Brew(object):
    def __init__(self):
        self._logger = get_logger(self.__class__.__name__)
        if self.__class__ is Brew:
            raise TypeError("Brew may not be instantiated directly")

        if not hasattr(self, 'name'):
            raise NotImplementedError('Need to define a name for this brew')

        # accepts a function/method to call whenever a brew state is reported
        self.brew_state_listener = None

    @classmethod
    def get_settings(cls):
        """get_settings

        A request to the brew asking for a dict of settings, the resulting
        settings will likely come as part of the context

        Returns:
            a dictionary returning all the brews settings
        """
        pass  # pragma: no cover

    def configure(self, context):
        """configure

        Configures a given brew

        Args:
            context: context settings
        """
        pass  # pragma: no cover

    def start(self):
        """start

        If needed, can init any brew-specific management or tools
        """
        pass  # pragma: no cover

    def stop(self):
        """stop

        If needed, can shutdown any brew-specific management or tools
        """
        pass  # pragma: no cover

    def create_brewer(self, brewer):
        """creates brewer for given topic

        If needed, create resource for brewing the specific topic

        Args:
            brewer (Brewer) - brewer instance
        Returns:
            (dict) - Any return value must be a dictionary of elements to
                     be included with the brewer_registration packet
        """
        pass  # pragma: no cover

    def destroy_brewer(self, brewer):
        """destroys brewer

        If needed, destroy resource created for brewing

        Args:
            brewer (Brewer) - brewer instance
        """
        pass  # pragma: no cover

    def create_patron(self, patron):
        """creates patron

        If needed, create resource for patronizing the specific topic

        Args:
            patron (Patron) - patron instance
        """
        pass  # pragma: no cover

    def destroy_patron(self, patron):
        """destroys patron

        If needed, destroy resource created for patronizing

        Args:
            patron (Patron) - patron instance
        """
        pass  # pragma: no cover

    def start_brewer(self, brewer_id, topic, patron_id, patron):
        """starts brewer

        Start brewing data.  The patrion_id, and patron data, will
        contain specific data about the client patronizing this brewed
        data.

        This is a place where would make sense to have some logic to determine
        if a brewer has patrons associated with it and optimize 'brew' calls to
        have it not send when no one is listening (no patrons)

        Args:
            brewer_id (uuid) - UUID of the brewing entity
            topic (string) - Topic being brewed
            patron_id (uuid) - UUID of the patronizing entity
            patron (dict) - Options from the connecting patron
        """
        pass  # pragma: no cover

    def stop_brewer(self, brewer_id, topic, patron_id):
        """stops brewer

        Stop brewing for the speicif patron on the given topic.
        This action, may or may not actually stop the brew from
        brewing, it may just prevent sending to this specific
        patron.

        Args:
            brewer_id (uuid) - UUID of the brewing entity
            topic (string) - Topic being brewed
            patron_id (uuid) - UUID of the patronizing entity
        """
        pass  # pragma: no cover

    def start_patron(self, patron_id, topic, brewer_id,
                     brewer_config, brewer_brew, callback):
        """starts patron

        Start patronizing the specific brewer for the given topic,
        create resources if needed, and give the parsed data to the
        specified callback

        Args:
            patron_id (uuid) - UUID of the patron entity
            topic (string) - Topic being patronized
            brewer_id (uuid) - UUID of the brewing entity
            brewer_config (dict) - Configuration of the brewer
            brewer_brew (dict) - Configuration of the brewers brew
            callback (callable) - Application end callback
        """
        pass  # pragma: no cover

    def stop_patron(self, patron_id, topic, brewer_id):
        """stops patron

        Stop patronizing the specific brewer for the given topic,
        destroy resources if needed

        Args:
            patron_id (uuid) - UUID of the patron entity
            topic (string) - Topic being patronized
            brewer_id (uuid) - UUID of the brewing entity
        """
        pass  # pragma: no cover

    def brew(self, brewer_id, topic, data, patrons):
        """brews data

        Actually send the data over the comm resource, you
        are provided the topic, the data

        Args:
            brewer_id (string) - brewer identifier
            topic (string) - Topic being brewed
            data (mixed) - Data to be transmitted
        """
        raise NotImplementedError()  # pragma: no cover

    def state_notify(self, state):
        """notifies a brew state

        Args:
            state (BrewState) - state brew is in
        """
        if not isinstance(state, BrewState):
            raise ValueError("Invalid Brew State specified")
        if self.brew_state_listener:
            self.brew_state_listener(self, state)
