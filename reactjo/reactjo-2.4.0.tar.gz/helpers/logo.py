string = """
╦═╗╔═╗╔═╗╔═╗╔╦╗╦╔═╗
╠╦╝║╣ ╠═╣║   ║ ║║ ║
╩╚═╚═╝╩ ╩╚═╝ ╩╚╝╚═╝
"""
def logo():
    print("\u001b[32m" + string + "\u001b[0m")
# Usage
# Pass the question as a string, without "(y/n)"
# (optional) pass a default of either "y" or "n"
# if no default is passed, then it's required,
# and process repeats until a valid answer is given
# e.g. boolean_input("Do you like cats", 'n') defaults to 'n'
