# encoding: utf-8

from abc import ABCMeta, abstractmethod


class BaseValidator(metaclass=ABCMeta):
    """Base validator

.. uml::
    @startuml
    abstract class BaseValidator <<abstract>>{
        -_protocol
        -_message : ValidatorMessages
        -_db_engine : Engine
        __methods__
        {abstract} validate(*credentials):ValidatorMessages
        __setter/getter__
        {abstract} protocol() : string
    }
    ABCMeta <|-- BaseValidator
    ValidatorMessages *-- BaseValidator
    @enduml

    """
    # Validation responses
    VALIDATION_OK = 'ACCESS'
    VALIDATION_DENIED = 'DENIED'
    VALIDATION_NOT_FOUND = 'NOT FOUND'
    VALIDATION_ERROR = 'ERROR'
    VALIDATION_FIRST = 'FIRST_OK'

    @abstractmethod
    def protocol(self):
        """Holds the protocol string for reporting and notification purposes
        :returns: str of protocol name

        """
        pass

    @abstractmethod
    def validate(self, key1=None, key2=None):
        """Validation function, intended to be overridden

        :param bytearray key1: Used for first authentification
        :param bytearray key2: Used for second authentification

        """
        pass
