"""自定义字典."""


class Dict:
    """字典."""

    def __init__(self, name, path):
        """."""
        self.name_ = name
        self.path_ = path
        self.content_ = set()
        self.kvs = {}

    def load_dict(self):
        """."""
        pass


class NationalDict(Dict):
    """."""

    def __init__(self, name, path):
        """."""
        Dict.__init__(self, name, path)

    def load_dict(self):
        """."""
        with open(self.path_, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                self.content_.add(line)


class AddressDict(Dict):
    """."""

    def __init__(self, name, path):
        """."""
        Dict.__init__(self, name, path)

    def load_dict(self):
        """."""
        with open(self.path_, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                tokens = line.split("\t")
                if len(tokens) != 2:
                    continue
                self.kvs[tokens[0]] = tokens[1]
