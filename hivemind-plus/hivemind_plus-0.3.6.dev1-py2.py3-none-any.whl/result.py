from hivemindplus.validation import validate


class Results:
    def __init__(
        self,
        connection_string,
        instance_table,
        iteration_table,
        output_function,
        agreement_function,
        agg_agreement_function,
        target_agreement,
        feedback_function,
        max_iterations
    ):
        self.connection_string = connection_string
        self.instance_table = instance_table
        self.iteration_table = iteration_table
        self.output_function = output_function
        self.agreement_enabled = agreement_function is not None or agg_agreement_function is not None
        self.agreement_function = agreement_function
        self.agg_agreement_function = agg_agreement_function
        self.target_agreement = target_agreement
        self.feedback_function = feedback_function
        self.max_iterations = max_iterations


class ConfigBuilder:
    def __init__(self):
        self._connection_string = None
        self._instance_table = None
        self._iteration_table = None
        self._output_function = None
        self._agreement_function = None
        self._agg_agreement_function = None
        self._target_agreement = None
        self._feedback_function = None
        self._max_iterations = 0

    def with_connection_string(self, connection_string):
        """
        A pypyodbc SQL connection string that is used to execute the query

        E.g. 'DRIVER={SQL Server};SERVER=localhost;UID=sa;PWD=password'
        """
        self._connection_string = connection_string
        return self

    def with_instance_table(self, instance_table):
        """
        (Optional) The fully qualified name of the table to store instance-level agreed upon results.
        This will be created automatically if it does not already exist.

        Defaults to HivemindPlus.dbo.Task_<TaskId>_InstanceResults
        """
        self._instance_table = instance_table
        return self

    def with_iteration_table(self, iteration_table):
        """
        (Optional) The fully qualified name of the table to store iteration-level agreed upon results.
        This will be created automatically if it does not already exist.

        Defaults to HivemindPlus.dbo.Task_<TaskId>_IterationResults
        """
        self._iteration_table = iteration_table
        return self

    def with_output_function(self, output_function):
        """
        (Optional) Function that will be invoked with every agreed upon result. This is called for every result
        that has not already been stored in the instance result table specified.
        """
        self._output_function = output_function
        return self

    def with_agreement_function(self, agreement_function, target_agreement=0.51):
        """
        Sets the function to be used when checking iterations for agreement

        (a, b) -> agree

        Function must take two iteration parameters and return a boolean
        to decide if they agree or not. If they agree then one will be
        written to the instance result table. If they do not agree and
        the instance has not hit the max iterations, then the instance
        will be reiterated.
        """
        self._agreement_function = agreement_function
        self._target_agreement = target_agreement
        return self

    def with_agg_agreement_function(self, agg_agreement_function):
        """
        Sets the function to be used when checking iterations for agreement

        (results, instance_id) -> agreed result

        Function must take an iteration results param with additional instance_id param
        and return an agreed upon result or throw AgreementNotReachedException.
        If they agree then the result will be written to the instance result table.
        If they do not agree and the instance has not hit the max iterations,
        then the instance will be reiterated.
        """
        self._agg_agreement_function = agg_agreement_function
        return self

    def with_feedback_function(self, feedback_function):
        """
        Sets the function to be used for any custom feedback logic after the instance has been persistes 
        
        (agreed_result, iteration_results)
        
        :param feedback_function: A function that takes in the agreed result as well as all the iteration results
        """
        self._feedback_function = feedback_function
        return self

    def with_max_iterations(self, max_iterations):
        """"
        Determines the upper limit of reiteration attempts.

        Defaults to 0
        """
        self._max_iterations = max_iterations
        return self

    def build(self):
        validate(self, [['_connection_string']])

        return Results(
            self._connection_string,
            self._instance_table,
            self._iteration_table,
            self._output_function,
            self._agreement_function,
            self._agg_agreement_function,
            self._target_agreement,
            self._feedback_function,
            self._max_iterations
        )
