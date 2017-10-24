#* Imports
import sys
import pycook.elisp as el
import pycook.cook as pc
import operator
import functools

#* Functions
def main(argv = None):
    if argv is None:
        argv = sys.argv
    try:
        rc_file = el.expand_file_name("~/.cookrc.py")
        if el.file_exists_p(rc_file):
            mod = imp.load_source("book_config", rc_file)
            books = mod.config["global"]
            functools.reduce(operator.concat ,
                             [pc.recipe_names(el.expand_file_name(book)) for book in books])
        (book, dd) = script_get_book()
        os.chdir(dd)
        pc.main(argv, book)
    except subprocess.CalledProcessError as e:
        print(e)
        sys.exit(e.returncode)
    except RuntimeError as e:
        print(e)
        sys.exit(1)
