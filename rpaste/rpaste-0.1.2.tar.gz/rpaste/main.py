from .rpaste import rpaste


def main():
    import argparse
    import sys
    import requests
    import pyperclip
    import os.path

    parser = argparse.ArgumentParser(prog='rpaste')
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('--push', nargs="*", metavar="FILES",
                       help='Push paste to rpaste.com')

    group.add_argument('--languages', action="store_true",
                       help='List languages available for syntax highlighting')

    group.add_argument('--pull', nargs=1,
                       help='Pull paste from rpaste.com')

    parser.add_argument('--password', nargs=1,
                        help='Set password for the paste')

    parser.add_argument('--clip', action='store_true',
                        help='Use clipboard to push and pull paste')

    parser.add_argument('--detailed', action='store_true',
                        help="Print all information about the paste in pull")

    args = parser.parse_args()

    if args.push is not None:
        files = args.push
        if not files:
            try:
                # Get input from the console
                paste = rpaste()
                if args.password:
                    paste.set_password(args.password)
                if args.clip:
                    paste.set_content(pyperclip.paste())
                    paste.push_paste("Clipboard")
                else:
                    inputcontent = ""
                    for line in sys.stdin:
                        inputcontent += line
                    paste.set_content(inputcontent)
                    paste.push_paste("Input")
            except Exception as e:
                print("ERROR : ", str(e))
                exit(1)
        else:
            if len(files) > 10:
                print("Can only process 10 files at a time")
                exit(2)

            for filename in files:
                if not os.path.isfile(filename):
                    print("File {} not found.".format(filename))
                else:
                    paste = rpaste()
                    if args.password:
                        paste.set_password(args.password)
                    try:
                        content = open(filename, "r").read()
                        paste.set_content(open(filename, "r").read())
                        paste.push_paste(filename)
                    except IOError:
                        print("Can't read {}".format(filename))
                    except Exception as e:
                        print("Error : ", str(e))
    elif args.pull:
        try:
            paste = rpaste()
            paste.set_url_slug(args.pull[0])
            if args.password:
                paste.set_password(args.password)

            paste.pull_paste()
            if args.clip:
                # Copy paste content to clipboard
                pyperclip.copy(paste.get_content())
                print("paste copied to clipboard")
            else:
                if args.detailed:
                    paste.print_info()
                else:
                    print(paste.get_content())
        except Exception as e:
            print("Error : ", str(e))
            exit(1)

    elif args.languages:
        print("Available languages: ")
        r = requests.get('https://rpaste.com/api/languages/list')

        languages = r.json()
        for language, slug in sorted(languages['languages']):
            print(language, " - ", slug)

    return 0
