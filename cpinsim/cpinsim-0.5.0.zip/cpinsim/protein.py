# -*- coding: utf-8 -*-

from bitarray import bitarray

class Protein:
    """ Representing a protein instance in the simulated cell.
        Contains the state of the protein in it, a pointer to the protein-type
        and the neccesary methods for protein interaction.
    """

    def __init__(self, name, protein_pointer):
        """ Initialize a protein instance with its name, the information to the protein type
            and a state without any other proteins bound.
        """
        self.name = name
        self.index = protein_pointer.index
        self.interactions = protein_pointer.interactions
        self.map_interactor_domains = protein_pointer.map_interactor_domains
        self.domains = protein_pointer.domains

        self.state = bitarray(len(self.index))
        self.state.setall(False)

        self.number_of_free_domains = len(self.domains)


    def get_possible_interactors(self):
        """ Return a list of the possible interactors of this protein.
        """
        return list(self.map_interactor_domains.keys())


    def get_domains_to_interactor(self, interactor):
        """ Return the domains at which the given $interactor can interact with
            this protein.
        """
        return self.map_interactor_domains[interactor]


    def is_interacting(self, protein, domain):
        """ Test if this protein instance is already interacting with $protein
            at $domain.
        """
        if not (protein, domain) in self.index:
            return False

        i = self.index[(protein, domain)]
        return self.state[i]


    def is_association_possible(self, protein, domain):
        """ Test if this protein can associate with $protein at $domain.
        """
        if not (protein, domain) in self.index:
            return False

        s = self.state
        i = self.index[(protein, domain)]
        # each clause contains two bitarrays: p=positive and n=negative
        for p, n in self.interactions[i]:
            # all bits from positive clauses must be set and no bit from a negative is allowed
            if ((p&s) == p) and ((n&(~s)) == n):
                return True
        return False


    def associate(self, protein, domain):
        """ Perfom an association beteween this protein and $protein at $domain.
            In the updated state the bit of index(protein,domain) is set to 1.
        """
        i = self.index[(protein, domain)]
        assert not self.state[i], "For a association the proteins should not be interacting before."
        self.state[i] = True
        self.number_of_free_domains -= 1
        return


    def dissociate(self, protein, domain):
        """ Perfom an dissociation beteween of the interaction this protein and
            $protein at $domain. In the updated state the bit of
            index(protein,domain) is set to 0.
        """
        i = self.index[(protein, domain)]
        assert self.state[i], "For a dissociation the proteins must be interacting first."
        self.state[i] = False
        self.number_of_free_domains += 1
        return

