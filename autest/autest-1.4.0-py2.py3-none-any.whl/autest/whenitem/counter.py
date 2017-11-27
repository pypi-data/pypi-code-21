from autest.api import AddWhenFunction
import hosts.output as host


def Counter(count_to):
    initialState = {"counter" : 0}

    def up_to_count():
        initialState["counter"] += 1
        host.WriteDebug(["counter", "when"],
                        "updating count to {0}".format(initialState["counter"]))
        return initialState["counter"] >= count_to

    return up_to_count


AddWhenFunction(Counter, generator=True)
