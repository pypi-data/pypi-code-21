import warnings

from trunity_3_client import TermsClient
from bs4 import BeautifulSoup


MISSING_TERMS_DEFINITION_TEXT = 'DEFINITION NOT FOUND'


class MissingDefinitionWarning(Warning):
    pass


class Glossary(object):

    def __init__(self, site_id, session):
        self._site_id = site_id
        self._client = TermsClient(session)

        self._no_definition_terms = []

        # we track uploaded term ids to make "update content term"
        # (this is a weird behavior of Trunity 3 Terms API):
        self._uploaded_term_ids = set()

        # This is the dict for keeping uploaded term definitions as keys and
        # uploaded term ids as values. We need this for do not upload the
        # term twice:
        self._uploaded_content_terms = {}

    @property
    def uploaded_term_ids(self) -> set:
        """
        Return uploaded term ids for each html.
        """
        return self._uploaded_term_ids

    @property
    def no_definition_terms(self):
        return self._no_definition_terms

    @no_definition_terms.deleter
    def no_definition_terms(self):
        self._no_definition_terms = []

    def _upload_term(self, term: str, definition: str) -> str:
        """
        Upload term to T3 and return term id.
        If already uploaded, just return uploaded terms id.
        """

        def upload_content_term(term: str, definition: str):
            print("Glossary term - {}: {}".format(term, definition))

            term_id = self._client.list.post(
                site_id=self._site_id,
                term_title=term,
                term_text=definition,
            )
            return self._client.tmp_content_term.post(term_id)

        if term not in self._uploaded_content_terms:
            content_term_id = upload_content_term(term, definition)
            self._uploaded_content_terms[term] = content_term_id
            return content_term_id

        else:
            return self._uploaded_content_terms[term]

    def _save_no_definition_term(self, term):
        self._no_definition_terms.append(term)
        warnings.warn("Tag without definition!", MissingDefinitionWarning)

    @staticmethod
    def _fix_definition(definition):
        return "<p>{}</p>".format(definition).strip()

    def _get_term(self, term_tag):
        term = term_tag['data-word']
        definition_tag = term_tag.find(
            "span",
            attrs={"data-type": "glossaryDefinition"}
        )

        # sometimes we have glossary terms without definitions.
        # this prevent the program from crushing:
        if definition_tag:
            definition = definition_tag.text
            if not definition.strip():
                definition = MISSING_TERMS_DEFINITION_TEXT
                self._save_no_definition_term(term)

        else:
            definition = MISSING_TERMS_DEFINITION_TEXT
            self._save_no_definition_term(term)

        return term.strip(), self._fix_definition(definition)

    @staticmethod
    def _build_t3_term_tag(soup, term_id, term):
        new_tag = soup.new_tag("term")
        new_tag.string = term
        new_tag["content-term-id"] = str(term_id)
        return new_tag

    def fix_tags(self, html: str) -> str:
        """
        - find all occurrences of term in html
        - upload term and definition to Trunity 3
        - fix html according to T3 format

        :param html article source html from Trunity 2:
        :return: str
        """
        soup = BeautifulSoup(html,  "html.parser")

        uploaded_term_ids = set()

        for term_tag in soup.find_all("span", class_='trunity_glossary'):
            term, definition = self._get_term(term_tag)
            term_id = self._upload_term(term, definition)
            uploaded_term_ids.add(term_id)
            t3_tag = self._build_t3_term_tag(soup, term_id, term)
            term_tag.replace_with(t3_tag)

        self._uploaded_term_ids = uploaded_term_ids

        return soup.decode()
