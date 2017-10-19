# -*- coding: utf-8 -*-

from .base_manager import BaseManager
from .models import Node, Edge, Citation, Evidence, Author
from ..utils import hash_citation


class LookupManager(BaseManager):
    """Groups functions for looking up entries by hashes"""

    def get_node_by_hash(self, node_hash):
        """Looks up a node by the hash of a PyBEL node tuple

        :param str node_hash: The hash of a PyBEL node tuple from :func:`pybel.utils.hash_node`
        :rtype: Node
        """
        return self.session.query(Node).filter(Node.sha512 == node_hash).one_or_none()

    def get_edge_by_hash(self, edge_hash):
        """Looks up an edge by the hash of a PyBEL edge data dictionary

        :param str edge_hash: The hash of a PyBEL edge data dictionary from :func:`pybel.utils.hash_edge`
        :rtype: Edge
        """
        return self.session.query(Edge).filter(Edge.sha512 == edge_hash).one_or_none()

    def get_citation_by_reference(self, type, reference):
        """Gets a citation object by its type and reference

        :param str type: The reference type
        :param str reference: The identifier in the source (e.g., PubMed identifier)
        :rtype: Optional[Citation]
        """
        citation_hash = hash_citation(type, reference)
        return self.get_citation_by_hash(citation_hash)

    def get_citation_by_hash(self, citation_hash):
        """Gets a citation object by its hash

        :param str citation_hash: The hash of the citation
        :rtype: Optional[Citation]
        """
        return self.session.query(Citation).filter(Citation.sha512 == citation_hash).one_or_none()

    def get_author_by_name(self, name):
        """Gets an author by name if they exist in the database

        :param str name: An author's name
        :rtype: Optional[Author]
        """
        return self.session.query(Author).filter(Author.name == name).one_or_none()

    def get_evidence_by_hash(self, evidence_hash):
        """Looks up evidence by its hash

        :param str evidence_hash:
        :rtype: Optional[Evidence]
        """
        return self.session.query(Evidence).filter(Evidence.sha512 == evidence_hash).one_or_none()
