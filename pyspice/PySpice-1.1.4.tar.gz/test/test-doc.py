####################################################################################################

from PySpice.Spice.Netlist import ElementParameterMetaClass

####################################################################################################

for classes in ElementParameterMetaClass.__classes__.values():
    for element_class in classes:
        print('-'*50)
        print(element_class.__name__)
        if element_class.number_of_pins():
            print(element_class.number_of_pins())
            # [str(x) for x in element_class.pins]
        # for parameter in element_class.positional_parameters.values():
        #     print(parameter.position, parameter.attribute_name, parameter, parameter.key_parameter)
        for parameter in element_class.parameters_from_args:
            print(parameter.position, parameter.attribute_name, parameter)
        for parameter in element_class.positional_parameters.values():
            if parameter.key_parameter:
                print(parameter.attribute_name, parameter)
        for parameter in element_class.optional_parameters.values():
            print(parameter.attribute_name, parameter)
