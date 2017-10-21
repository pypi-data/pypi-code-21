import sys
from douban_rating.query import query
from simple_table import SimpleTable


def print_ratings(ratings):
    table = SimpleTable()
    table.set_headers(['Title', 'Rating'])
    table.add_rows([[rating.title, rating.rating] for rating in ratings])

    print(table)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: douban-rating -book book-name')

        sys.exit(1)

    query_type = sys.argv[1]

    if query_type not in ['-book', '-movie']:
        print('Invalid type')

        sys.exit(1)

    title = sys.argv[2]
    ratings = query(query_type.replace('-', ''), title)

    print_ratings(ratings)
