import argparse
from .reader import dictionary_sample


def main():
    parser = argparse.ArgumentParser(description="Code name generator")

    parser.add_argument('num', nargs='?', type=int, default=1)
    parser.add_argument('-c', '--capitalize', action='store_true', default=False)
    parser.add_argument('-t', '--title', action='store_true', default=False)
    parser.add_argument('-s', '--slugify', action='store_true', default=False)

    parser.add_argument(
        '--prefix',
        help='Prefix dictionary',
        default='adjectives')

    parser.add_argument(
        '--suffix',
        help='Suffix dictionary',
        default='mobi_notable_scientists_and_hackers')

    args = parser.parse_args()

    prefix = dictionary_sample(args.prefix, args.num)
    suffix = dictionary_sample(args.suffix, args.num)

    for n in range(args.num):
        codename = prefix[n] + " " + suffix[n]

        if args.capitalize:
            codename = codename.capitalize()
        elif args.title:
            codename = codename.title()
        elif args.slugify:
            codename = codename.replace(' ', '_')
        else:
            codename = codename.lower()

        # TODO: support output formats: plain, csv, json, xml
        print(codename)

main()
