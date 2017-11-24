from pathlib import Path


def recursive_walker(top: Path, function):
    to_walk = [Path(top)]

    while to_walk:
        current_dir = to_walk.pop()
        for f in current_dir.iterdir():
            if f.is_dir():
                to_walk.append(f)
                function(top, f)
            elif f.is_file():
                function(top, f)
            else:
                print("Skipping %s" % f)
