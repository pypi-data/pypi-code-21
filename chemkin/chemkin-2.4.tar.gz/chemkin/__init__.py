import os

# Define paths to key data assets based on relative position to this module.
# XML files folder.
_PATH_XML_FILES = os.path.join(os.path.dirname(__file__), 'xml-files/')
# NASA coefficients db.
PATH_NASA_COEFF_DB = os.path.join(os.path.dirname(__file__),
                                   'thermodynamics/NASA_coef.sqlite')


def pckg_xml_path (file_name):
    """Creates full path to XML file located in xml-files directory."""
    if file_name[-4:] != '.xml':
        file_name += '.xml'
    return _PATH_XML_FILES + file_name
