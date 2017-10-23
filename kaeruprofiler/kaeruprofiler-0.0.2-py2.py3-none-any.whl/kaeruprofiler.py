def profile_with_key(attr_name):
    import os
    import pickle
    import time

    filename = 'repr.dump'
    if not os.path.exists(filename):
        pickle.dump({}, open(filename, 'wb'))

    def each_profile(method):
        def _deco(self, *args, **kwargs):
            loaded = pickle.load(open(filename, 'rb'))

            key = getattr(self, attr_name)

            data = loaded.get(key, {'count': 0, 'time': 0})
            start = time.time()

            r = method(self, *args, **kwargs)

            end = time.time()
            elapsed = end - start
            data['count'] += 1
            data['time'] += elapsed
            data['avr'] = data['time'] / data['count']
            loaded[key] = data
            pickle.dump(loaded, open(filename, 'wb'))
            return r
        return _deco
    return each_profile
