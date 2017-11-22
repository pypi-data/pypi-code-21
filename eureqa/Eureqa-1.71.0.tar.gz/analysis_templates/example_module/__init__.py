
import sys, os

## Add the Eureqa API and the test runner to sys.path
## Modify these lines as needed.
sys.path.append(os.path.abspath("../.."))
sys.path.append(os.path.abspath(".."))

from eureqa import *
from eureqa.analysis_templates import *
from eureqa.utils.modulefiles import open_module_file

## This function is required for the analysis template.
## Modify it to create any analyses that you need.
def create_analysis(eureqa, template_execution):
    template_execution.update_progress('Starting running analysis template.')
    analysis = template_execution.get_analysis()
    analysis.name = 'Test analysis template execution 1'

    ## Open the "sample.csv" file contained within this module.
    ## When running on the remote server, this fetches the file.
    with open_module_file('sample.csv') as f:
        data_source = eureqa.create_data_source('Analysis_card__data_source', f)
        
    input_variables = set(data_source.get_variables())-{'Weight'}
    settings = eureqa.search_templates.numeric('Test analysis templates 1', 'Weight',
                                               input_variables, datasource=data_source)
    template_execution.update_progress('Creating search.')
    search = data_source.create_search(settings)
    template_execution.update_progress('Starting search')
    search.submit(1000)
    while len(search.get_solutions()) < 2 and search.is_running:
        pass
    template_execution.update_progress('Found 2 models. Stopping search.')
    search.stop()
    template_execution.update_progress('Creating cards.')

    card_title = template_execution.parameters['example_text_param'].value
    for solution in search.get_solutions():
        analysis.create_model_card(solution, card_title)

    template_execution.update_progress('Done!')


## This function is optional.
## If provided, the template will be a parameterized template;
## in order to run your template, Eureqa users will be prompted to provide these values.
def template_parameters():
    return Parameters(
            [TextParameter('example_text_param','Input Text'),
             TopLevelModelParameter('example_model_param','Select a Model', None),
             DataSourceParameter('example_datasource_param', 'Select a DataSource',
                                 {VariableParameter('variable_param_1', 'Variable')})])

## This section is not required for an analysis template,
## but can be a convenience for developers.
## It causes the module to be runnable; and when run, to
## behave as if you had invoked run_analysis_template.py to
## run the template.
## Note -- to run this, the directory containing
## 'run_analysis_template.py' must be in PYTHONPATH.
if __name__ == "__main__":
    from eureqa.analysis_templates.runner.client import main

    ## By default, take any arguments from the command line.
    args = list(sys.argv)
    ## Alternatively, if you want to construct the command line from scratch:
    #args = ["run_analysis_template.py"]

    ## Construct a Parameters object representing the template's parameters.
    ## These can be difficult to construct at the command line;
    ## constructing them in Python can be easier.
    import json
    parameter_values = ParametersValues(
            [TextParameterValue(None, 'example_text_param','Text entered by the user'),
             TopLevelModelParameterValue(None, 'example_model_param', "a + 2", None, None, None),
             DataSourceParameterValue(None, 'example_datasource_param', 'value of datasource',
                {VariableParameterValue(None, 'variable_param_1', 'value of variable')})])
    args += ["--parameter-values", json.dumps(parameter_values._to_json())]

    ## The one required argument to run_analysis_template.py
    ## is the path to ourselves.
    ## Python knows that, so add it automatically.
    args += [os.path.abspath(os.path.dirname(__file__))]
    
    main(args)
