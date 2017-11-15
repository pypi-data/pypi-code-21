import xml.etree.ElementTree as ET
from chemkin import *
import numpy as np

def parseXML(file):
    """
    Parses the XML file containing reactions information. Returns reaction coefficients and reaction rates.
    
    INPUTS
    ========
    file: string, required
          path of the XML file
          
    RETURNS
    ========
    species_lst: list of species to fix order
    reactions_dict: dictionary containing all relevant information for calculating reaction rates
    """
    
    tree = ET.parse(file)
    root = tree.getroot()

    # initialize variables
    reactions_dict = {'reactants': {}, 'products': {}, 'rates': []}
    coeffs_dict = []
    species_lst = []
    reversible_lst = []

    for species in root.find('phase').find('speciesArray').text.split():
        species_lst.append(species)
        reactions_dict['reactants'][species] = []
        reactions_dict['products'][species] = []

    for child in root.find('reactionData').findall('reaction'):

        # Record whether reaction is reversible
        reversible_lst.append(child.get('reversible'))

        # Parse reactants and products
        species = list(reactions_dict['products'].keys())
        for reactant in child.find('reactants').text.split():
            key, value = reactant.split(':')
            try:
                reactions_dict['reactants'][key].append(float(value))
            except:
                raise ValueError('Unknown species. Please check if your XML file specifies all species.')
            species.remove(key)
        for reactant in species:
            try:
                reactions_dict['reactants'][reactant].append(0.0)
            except:
                raise ValueError('Unknown species. Please check if your XML file specifies all species.')

        species = list(reactions_dict['products'].keys())
        for product in child.find('products').text.split():
            key, value = product.split(':')
            reactions_dict['products'][key].append(float(value))
            species.remove(key)
        for product in species:
            reactions_dict['products'][product].append(0.0)

        # Parse reaction coefficients
        coeffs = child.find('rateCoeff')
        if coeffs.find('Arrhenius'):
            new_dict = {}
            new_dict['type'] = 'Arrhenius'
            try:
                new_dict['A'] = float(coeffs.find('Arrhenius').find('A').text)
                new_dict['E'] = float(coeffs.find('Arrhenius').find('E').text)
            except:
                raise ValueError('Missing coefficients. Please check your XML file.')
            reactions_dict['rates'].append(new_dict)
            
        if coeffs.find('modifiedArrhenius'):
            new_dict = {}
            new_dict['type'] = 'modifiedArrhenius'
            try:
                new_dict['A'] = float(coeffs.find('modifiedArrhenius').find('A').text)
                new_dict['E'] = float(coeffs.find('modifiedArrhenius').find('E').text)
                new_dict['b'] = float(coeffs.find('modifiedArrhenius').find('b').text)
            except:
                raise ValueError('Missing coefficients. Please check your XML file.')
            reactions_dict['rates'].append(new_dict)

        if coeffs.find('Constant'):
            new_dict = {}
            new_dict['type'] = 'Constant'
            try:
                new_dict['k'] = float(coeffs.find('Constant').find('k').text)
            except:
                raise ValueError('Missing coefficients. Please check your XML file.')
            reactions_dict['rates'].append(new_dict)

    return species_lst, reactions_dict, reversible_lst