import clarus.services

def fixingdates(output=None, **params):
    return clarus.services.api_request('Dates', 'FixingDates', output=output, **params)

def fxforwarddate(output=None, **params):
    return clarus.services.api_request('Dates', 'FxForwardDate', output=output, **params)

def fxoptiondate(output=None, **params):
    return clarus.services.api_request('Dates', 'FxOptionDate', output=output, **params)

def irdspotdate(output=None, **params):
    return clarus.services.api_request('Dates', 'IrdSpotDate', output=output, **params)

def maintenanceperiods(output=None, **params):
    return clarus.services.api_request('Dates', 'MaintenancePeriods', output=output, **params)

def schedule(output=None, **params):
    return clarus.services.api_request('Dates', 'Schedule', output=output, **params)

