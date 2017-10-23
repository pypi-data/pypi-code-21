def profile_with_key(attr_name):
    import os
    import pickle
    import time
    filename = 'repr.dump'

    def each_profile(method):
        def _deco(self, *args, **kwargs):
            if not os.path.exists(filename):
                pickle.dump({}, open(filename, 'wb'))

            loaded = pickle.load(open(filename, 'rb'))

            splitted = attr_name.split('.')
            current_attr = self
            for sp in splitted:
                current_attr = getattr(current_attr, sp)

            data = loaded.get(current_attr, {'count': 0, 'time': 0})
            start = time.time()

            r = method(self, *args, **kwargs)

            end = time.time()
            elapsed = end - start
            data['count'] += 1
            data['time'] += elapsed
            data['avr'] = data['time'] / data['count']
            loaded[current_attr] = data
            pickle.dump(loaded, open(filename, 'wb'))
            return r
        return _deco
    return each_profile
