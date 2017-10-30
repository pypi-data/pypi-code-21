def read_artists(filename):
    with open(filename, 'r') as file:
        return file.read().splitlines()


def reverse_artists(filename):
    artists = read_artists(filename)

    with open(filename, 'w') as file:
        for artist in reversed(artists):
            file.write(artist + '\n')
