import warnings


class MyWarning(Warning):
    pass


def func_with_warning():
    warnings.warn("We warn here!", MyWarning)
    print("Continue after raising warning...")


if __name__=="__main__":
    print("Testing warnings...")

    with warnings.catch_warnings():
        # warnings.filterwarnings('error')
        warnings.simplefilter("error")

        try:
            func_with_warning()
        except MyWarning:
            print("it seems we can catch warning!..")
        else:
            print("We can't catch warnings :(")