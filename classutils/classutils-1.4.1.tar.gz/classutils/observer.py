# -*- coding: utf-8 -*-
# Description: Implements an Observable class that can be added
#              simply to another class.
#              https://en.wikipedia.org/wiki/Observer_pattern
# Author: Hywel Thomas


class ObserverError(Exception):
    pass


class Observable(object):

    def __initialise_if_required(self):

        try:
            self.observers

        except AttributeError:
            # First observer, initialise the list
            self.observers = []

    def register_observer(self,
                          observer):

        self.__initialise_if_required()

        try:
            observer.notify

        except AttributeError:
            raise ObserverError(u'{observer} does not have a notify method.'.format(observer=observer))

        self.observers.append(observer)

    def unregister_observer(self,
                            observer):
        self.__initialise_if_required()
        self.observers.remove(observer)

    def notify_observers(self,
                         *args,
                         **kwargs):
        self.__initialise_if_required()

        for observer in self.observers:
            observer.notify(notifier=self,
                            *args,
                            **kwargs)


class ObserverMixIn(Observable):
    pass
