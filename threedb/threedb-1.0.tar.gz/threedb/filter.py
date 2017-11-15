
class SetFilter:

    def apply_filter(self, items, strict=None, filter=None):
        if not filter:
            return items

        filtered = []
        tags = set(filter or [])
        for item in items:
            data_tags = set([item.index]) | set(item.tags)

            if strict:
                if not bool(tags - data_tags):
                    filtered.append(item)
                    continue
                continue

            if (data_tags & tags):
                filtered.append(item)

        return filtered
