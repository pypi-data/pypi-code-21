from .http import request


def get_company_info():
    data = request('v2', 'info', '')
    return Company(data)


class Company:
    """Represents the company.
    
    Attributes
    ----------
    name: str
        The name of the company.
    founder: str
        The founder of the company.
    founded: int
        The year the company was founded in.
    employees: int
        The amount of people the company employs.
    vehicles: int
        The unique amount of vehicles the company has.
    launch_sites: int
        The amount of launch sites the company has.
    test_sites: int
        The amount of test sites the company has.
    ceo: str
        The CEO of the company.
    cto: str
        The CTO of the company.
    coo: str
        The COO of the company.
    cto_propulsion: str
        The CTO of Propulsion of the company.
    valuation: int
        The valuation of the company.
    summary: str
        A summary of the company.
    headquarters: dict
        Contains information about the company's headquarters.
    """
    def __init__(self, data):
        self._from_data(data)

    def _from_data(self, data):
        self.__dict__.update(data)
