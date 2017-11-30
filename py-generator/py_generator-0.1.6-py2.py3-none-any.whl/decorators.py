def receives_params(recipe_type):
    def receiver(func):
        def prompt_for_recipe(*args, **kwargs):
            args_dict = {}

            args_dict['recipe'] = recipe_type

            if recipe_type == 'component':
                component_name = raw_input("Please specify a name for the component: ")
                args_dict['component_name'] = component_name
            elif recipe_type == 'filter':
                filter_name = raw_input("Please specify a name for the filter: ")
                args_dict['filter_name'] = filter_name
            elif recipe_type == 'route':
                route_name = raw_input("Please specify a name for the route: ")
                component_name = raw_input("Please specify a valid component name: ")
                slug = raw_input("Please specify a slug for the route: ")

                args_dict['route_name'] = route_name.lower()
                args_dict['component_name'] = component_name.capitalize() or route_name.capitalize()
                args_dict['slug'] = slug

            return func(required_params=args_dict)
        return prompt_for_recipe
    return receiver
