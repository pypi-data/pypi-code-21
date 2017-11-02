from inspect import stack


class Condition:
    def __init__(self, value):
        self.value = value
        self._result = True
        self.failures = []
        self.success = []

    def result(self):
        return self._result

    def equal(self, target):
        if not self.value == target:
            self.failures.append((stack()[0].function, target))
            self._result = False
        self.success.append((stack()[0].function, target))
        return self

    def gt(self, target):
        if not self.value > target:
            self.failures.append((stack()[0].function, target))
            self._result = False
        self.success.append((stack()[0].function, target))
        return self

    def lt(self, target):
        if not self.value > target:
            self.failures.append((stack()[0].function, target))
            self._result = False
        self.success.append((stack()[0].function, target))
        return self

    def differ(self, target):
        if not self.value != target:
            self.failures.append((stack()[0].function, target))
            self._result = False
        self.success.append((stack()[0].function, target))
        return self

    def be(self, target):
        if self.value is not target:
            self.failures.append((stack()[0].function, target))
            self._result = False
        self.success.append((stack()[0].function, target))
        return self

    def contain(self, item):
        if item not in self.value:
            self.failures.append((stack()[0].function, item))
            self._result = False
        self.success.append((stack()[0].function, item))
        return self

    def hold(self, num):
        if not len(self.value) == num:
            self.failures.append((stack()[0].function, num))
            self._result = False
        self.success.append((stack()[0].function, num))
        return self

    def have(self, attribute):
        if not hasattr(self.value, attribute):
            self.failures.append((stack()[0].function, attribute))
            self._result = False
        self.success.append((stack()[0].function, attribute))
        return self

    def instance_of(self, _class):
        if not isinstance(self.value, _class):
            self.failures.append((stack()[0].function, _class.__name__))
            self._result = False
        self.success.append((stack()[0].function, _class.__name__))
        return self

    def expect(self, func, result):
        if not func(self.value) == result:
            self.failures.append((stack()[0].function, (func.__name__, result)))
            self._result = False
        self.success.append((stack()[0].function, (func.__name__, result)))
        return self


if __name__ == '__main__':
    condition = Condition(1).be(2).equal(
        2.0 - 2).differ('a').instance_of(str).expect(lambda x: x, 1)
    print(condition.result(), condition.success, condition.failures, sep='\n')
    condition = Condition([1, 2, 3]).contain(1).have('append').hold(3).instance_of(list)
    print(condition.result(), condition.success, condition.failures, sep='\n')
