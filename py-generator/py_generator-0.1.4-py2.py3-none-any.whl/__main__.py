import sys

from functions import (
    create_component,
    create_filter,
    register_route,
)


def main(args=None):

    # def prompt_for_recipe(recipe_type, to_exec):
    #     if recipe_type == 'component':
    #         to_exec()
    #     elif recipe_type == 'filter':
    #         to_exec()
    #     elif recipe_type == 'route':
    #         to_exec()

    def show_help(*args):
        print "Help content"

    def validate(param):
        available_recipes = {
            'component': create_component(),
            'filter': create_filter(),
            'route': register_route(),
        }

        available_recipes.get(param, show_help())

    if args is None:
        if len(sys.argv) == 1:
            sys.exit("Error: Required 'recipe' param")
        else:
            validate(sys.argv[1])
            

if __name__ == "__main__":
    main()