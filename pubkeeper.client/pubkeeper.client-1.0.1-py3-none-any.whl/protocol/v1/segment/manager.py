"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.protocol.v1.brewer.brewer import ProtocolBrewer as Brewer
from pubkeeper.protocol.v1.patron.patron import ProtocolPatron as Patron
from pubkeeper.protocol.v1.segment.translator import BrewTranslator
from pubkeeper.protocol.v1.segment.info import SegmentInfo
from pubkeeper.utils.logging import get_logger


class _SegmentManager(object):
    """ Manages all segments

    Provides functionality to create and destroy segments

    A segment is originally requested by server providing brewer and
    patron details on how to create a matching segment, client internally
    creates a patron and brewer respectively able to consume data from original
    brewer and brew to original patron.
    """
    def __init__(self):
        self.logger = get_logger('pubkeeper.segment.SegmentManager')
        self._segments = dict()

    @property
    def segments(self):
        return self._segments

    def create(self, handler, segment_id,
               patron_details, brewer_details):
        """ Creates requested segment

        Args:
            handler (ClientProtocolHandler) - ClientProtocolHandler instance
            segment_id (uuid) - segment UUID
            patron_details (dict) - contains settings used to create
                tmp_patron which patronizes previous brewer.
                    patron_id    -> created temp patron id
                    brewer_id    -> brewer_id to patronize
                    topic        -> topic for brewer_id to patronize
                    brew details -> brew to patronize
            brewer_details (dict) - contains settings used to create
                tmp_brew which receives from tmp_patron created and
                brews to next patron in bridge.
                    brewer_id -> created temp brewer id
                    brew_name -> temp brew name to brew on
                    topic     -> temp topic to brew on
        """
        if handler is None or segment_id is None \
                or brewer_details is None or patron_details is None:
            raise ValueError(
                "create_segment: Need to Provide a segment id, "
                "brewer_details, patron_details, handler")

        if segment_id in self._segments:
            self.logger.warning('Segment: {} already exists, ignoring creation'.
                                format(segment_id))

        self.logger.info('Creating segment: {}'.format(segment_id))

        # setup temp brewer to receive from below patron
        brewer = Brewer(brewer_details["topic"],
                        brewer_id=brewer_details["brewer_id"],
                        crypto=False)
        translator = BrewTranslator(brewer)
        # setup patron receiving from already going brewer
        patron = Patron(patron_details["topic"],
                        callback=translator.callback,
                        patron_id=patron_details["patron_id"],
                        crypto=False)

        brewer_brew = None
        patron_brew = None
        brewer_brew_out = {}
        patron_brew_out = {}

        for brew in handler._brews:
            if brew.name == brewer_details['brew_name']:
                brewer_brew = brew
                brewer.brews = [brewer_brew]
                brewer_brew_out['name'] = brewer_brew.name

                details = brewer_brew.create_brewer(brewer)
                if details:
                    if not isinstance(details, dict):  # pragma no cover
                        raise RuntimeError("Create Patron returned a non dict")
                    else:
                        brewer_brew_out.update(details)

            if brew.name == patron_details['brew']['name']:
                patron_brew = brew
                patron.brews = [patron_brew]
                patron_brew_out['name'] = patron_brew.name

                details = patron_brew.create_patron(patron)
                if details:
                    if not isinstance(details, dict):  # pragma no cover
                        raise RuntimeError("Create Patron returned a non dict")
                    else:
                        patron_brew_out.update(details)

        self._segments[segment_id] = SegmentInfo(
            brewer_details["brewer_id"], brewer, brewer_brew,
            patron, patron_brew
        )

        patron.new_brewers([
            {
                "topic": patron_details["topic"],
                "brewer_id": patron_details["brewer_id"],
                "brew": patron_details["brew"],
                "brewer_config": None
            }
        ])

        return brewer_brew_out, patron_brew_out

    def connect_brewer(self, segment_id, patron_id, patron_brew):
        """ Connects a brewer with its patron brew

        Args:
            segment_id (uuid) - segment UUID
            patron_id (uuid) - patron id
            patron_brew (dict) - patron brew
        """
        if segment_id not in self._segments:
            msg = 'Segment: {} does not exist, ignoring brewer connect ' \
                  'request'.format(segment_id)
            self.logger.warning(msg)
            raise ValueError(msg)

        segment_info = self._segments[segment_id]
        segment_info.target_patron_id = patron_id
        segment_info.brewer.new_patrons([
            {
                "patron_id": patron_id,
                "brew": patron_brew
            }
        ])

    def destroy(self, segment_id):
        """ Destroy an existing segment

        Args:
            segment_id (uuid) - segment UUID
        """
        if segment_id not in self._segments:
            self.logger.warning('Segment: {} does not exist, ignoring destroy'.
                                format(segment_id))
            return

        self.logger.info('Destroying segment: {}'.format(segment_id))

        # cleanup local info
        segment_info = self._segments[segment_id]

        # Stop brewing and patronizing
        segment_info.brewer.remove_patron(segment_info.target_patron_id)
        segment_info.patron.remove_brewer(segment_info.previous_brewer_id)

        # execute brew un-registration
        segment_info.brewer_brew.destroy_brewer(segment_info.brewer)
        segment_info.patron_brew.destroy_patron(segment_info.patron)

        # remove reference to this segment
        del(self._segments[segment_id])

    def reset(self):
        self.logger.info("Removing all segments")
        for segment_id in list(self._segments.keys()):
            self.destroy(segment_id)
        self._segments.clear()


SegmentManager = _SegmentManager()
