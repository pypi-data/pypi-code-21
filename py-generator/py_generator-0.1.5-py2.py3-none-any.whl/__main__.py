import sys

from functions import (
    create_component,
    create_filter,
    register_route,
)


def main(args=None):
  
    def show_help(*args):
        print "Help content"

    def validate(param):
        available_recipes = {
            'component': create_component,
            'filter': create_filter,
            'route': register_route,
        }

        available_recipes.get(param, show_help)()

    if len(sys.argv) == 1:
        sys.exit("Error: Required 'recipe' param")
    else:
        validate(sys.argv[1])
        sys.exit()
      

if __name__ == "__main__":
    main()