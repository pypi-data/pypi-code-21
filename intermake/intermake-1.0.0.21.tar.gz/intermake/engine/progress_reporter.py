"""
Contains the `ProgressReporter`, and associated classes.

This acts as the go-between between the `Mandate` (plugin-side) and the `IProgressReceiver` (host-side), which may or may not exist in different threads.
"""
import time
from queue import Queue
from typing import Optional, List, Tuple, Sequence, Union, Callable

from mhelper.comment_helper import abstract
from mhelper.string_helper import time_to_string_short, time_to_string
from intermake.engine.constants import EStream, EDisplay


__author__ = "Martin Rusilowicz"

WORKER_FN = "Callable[ [ ProgressReporter ], Any ]"
CALLBACK_FN = "Optional[Callable[ [ IProgressReceiver ], None ]]"
SIMPLE_WORKER_CALLBACK_FN = "Optional[Callable[ [ WorkerManager ], None ]]"
TText = Optional[Union[str, bool, Callable[[int], str]]]


class TaskCancelledError( Exception ):
    """
    The `ProgressReporter` can raise this error when the plugin tries to send a progress update, if it determines the user has chosen to cancel the operation.
    Note that this is distinct from the KeyboardInterrupt issued by the CLI and handled separately.
    """
    
    
    def __init__( self ):
        super().__init__( "Task cancelled by user." )


class UpdateInfo:
    """
    Update information passed from worker (possibly in another thread) to watcher.
    
    The fields on this class are the same as those passed to the constructor. See the constructor for details.
    """
    
    
    def __init__( self,
                  uid: int,
                  depth: Tuple[int, ...],
                  text: str,
                  value: int,
                  max: int,
                  total_time: float,
                  sample_complete: int,
                  sample_time: float,
                  thread_index: int,
                  num_threads: int,
                  message: Optional[str],
                  value_string: Optional[str],
                  stream: EStream
                  ):
        """
        :param uid:               - a unique number assigned to the task. Used to distinguish concurrent tasks.
        :param depth:             - a list denoting the subtask stages. The caller gets the following updates for each subtask stage, in order:
                                        1 x       : when it is created,         e.g. depth=1,2,1      value=0,   max=10 
                                        0..n x    : when its progress changes   e.g. depth=1,2,1      value=1..9 max=10
                                        1 x       : when it is completed,       e.g. depth=1,2,1      value=10   max=10 (value and max not guaranteed to coincide - use the next update to signal subtask completion)
                                        1 x       : when its child completes    e.g. depth=1,2
        :param text:              - the title of the subtask stage
        :param value:             - the progress into the subtask stage. When `max` is `0`, `0` indicates unknown or not begun.
        :param max:               - the size of the subtask stage. 0 indicates unknown.
        :param total_time:        - how long the subtask stage has been running, in seconds
        :param sample_complete:   - number of increments to `value` in the sampling period
        :param sample_time:       - length of the sampling period, in seconds
        :param thread_index:      - number of the thread
        :param num_threads:       - number of threads
        :param message:           - a specific, informative message passed from worker to watcher.
                                    when this is not `None` all other fields are undefined.
        """
        assert isinstance( uid, int )
        assert isinstance( depth, tuple )
        assert isinstance( text, str )
        assert isinstance( value, int )
        assert isinstance( max, int )
        assert isinstance( total_time, float )
        assert isinstance( sample_complete, int )
        assert isinstance( sample_time, float )
        assert isinstance( thread_index, int )
        assert isinstance( num_threads, int )
        assert message is None or isinstance( message, str ), "Message should be a str not a «{}» («{}»).".format( type( message ), message )
        assert value_string is None or isinstance( value_string, str )
        assert isinstance( stream, EStream )
        
        self.uid = uid
        self.depth = depth
        self.text = text
        self.value = value
        self.value_string = value_string
        self.max = max
        self.total_time = total_time
        self.sample_complete = sample_complete
        self.sample_time = sample_time
        self.thread_index = thread_index
        self.num_threads = num_threads
        self.message = message
        self.stream = stream
    
    
    def format_progress( self ) -> str:
        """
        Formats the progress as an "x of y" -type message.
        """
        if self.value_string:
            return self.value_string
        
        if self.max <= 0:
            if self.value <= 0:
                #  No maximum or value
                return ""
            else:
                # No maximum but has a value
                return str( self.value )
        else:
            # Value and maximum
            return str( self.value ) + " of " + str( self.max )
    
    
    def format_time( self, display: EDisplay ) -> str:
        """
        Formats the time remaining, using the specified `display` mode.
        """
        if self.max <= 0 or self.value < 0:
            return ""
        
        ops_per_second, ops_remaining, time_per_op, time_remaining = self.estimate_time()
        
        # Return that as a string
        if display == EDisplay.TIME_REMAINING:
            # 17 minutes remaining
            if time_remaining < 1:
                return ""
            
            return time_to_string( time_remaining ) + " remaining"
        elif display == EDisplay.OPERATIONS_REMAINING:
            # 17000 operations remaining
            return str( ops_remaining ) + " operations remaining"
        elif display == EDisplay.TIME_PER_OPERATION:
            # 45 milliseconds per operation
            return time_to_string( time_per_op ) + " per operation"
        elif display == EDisplay.OPERATIONS_PER_SECOND:
            # 60 operations per second
            return str( round( ops_per_second ) ) + " operations per second"
        elif display == EDisplay.SAMPLE_RANGE:
            # Estimated using 420 completions over 5 minutes
            return "Estimated using " + str( self.sample_complete ) + " completions over " + time_to_string( self.sample_time )
        elif display == EDisplay.TOTAL_RANGE:
            # Total of 170 completions over 9 minutes
            return "Total of " + str( self.value ) + " completions over " + time_to_string( self.total_time )
        elif display == EDisplay.OPERATIONS_COMPLETED:
            # 170 of 256 operations completed
            return str( self.value ) + " of " + str( self.max ) + " operations completed"
        elif display == EDisplay.TIME_TAKEN:
            # Time taken: 4 days
            return "Time taken: " + time_to_string( self.total_time )
        elif display == EDisplay.TIME_REMAINING_SHORT:
            if time_remaining < 1:
                return ""
            
            return time_to_string_short( time_remaining )
        else:
            return "Unknown switch on " + repr( display )
    
    
    def estimate_time( self ) -> Tuple[float, float, float, float]:
        """
        Estimates time the remaining, giving the answer as a tuple of 4 floats.
        :return: ops_per_second, ops_remaining, time_per_op, time_remaining 
        """
        
        if self.sample_complete:
            time_per_op = self.sample_time / self.sample_complete
        else:
            time_per_op = 0
        if self.sample_time:
            ops_per_second = self.sample_complete / self.sample_time
        else:
            ops_per_second = 0
        
        # Given our time_per_op how long to complete the rest?
        ops_remaining = self.max - self.value
        time_remaining = time_per_op * ops_remaining
        return ops_per_second, ops_remaining, time_per_op, time_remaining


class IProgressReceiver:
    """
    Interface for classes able to process progress updates issued by a `ProgressReporter` object (which is encapsulated in the `Mandate`).
    """
    
    
    @abstract
    def question( self, message: str, options: Sequence[object] ) -> Optional[object]:
        """
        The receiver should ask the user the question and return the response.
        :param message: Question text 
        :param options: List of options. If empty or `None` this can be considered as a `True`, `False` question. 
        :return:        Selected option from list. 
        """
        raise NotImplementedError( "abstract" )
    
    
    @abstract
    def was_cancelled( self ) -> bool:
        """
        The receiver should determine if the user wishes to cancel the task.
        :return: `True` if the user wishes to cancel the task, else `False` to continue. 
        """
        raise NotImplementedError( "abstract" )
    
    
    @abstract
    def progress_update( self, info: UpdateInfo ) -> None:
        """
        The receiver should provide a progress feedback to the user.
        :param info: Information on the progress update, see the `UpdateInfo` class for details. 
        :return: Nothing is returned from this function 
        """
        raise NotImplementedError( "abstract" )


class ProgressReporter:
    """
    Acts as the go-between between the `Mandate` (plugin-side) and the `IProgressReceiver` (host-side).
    
    For help on methods see `Mandate` for general comments on the method, or see `IProgressReceiver` for host-specific help (where relevant).
    """
    __uid_counter = 0
    
    
    def __init__( self, receiver: IProgressReceiver, title: str = None, thread_index = 0, num_threads = 1, update_interval = 0.2 ):  # MAIN
        """
        CONSTRUCTOR

        Performs the action "f" behind a progress dialogue
        :param receiver: Worker thread
        :param title: Title of wait window
        """
        
        if title is None:
            title = "Please wait"
        
        self._receiver = receiver
        self._thread_index = thread_index
        self._num_threads = num_threads
        self._message_records = []
        
        ProgressReporter.__uid_counter += 1
        self.uid = ProgressReporter.__uid_counter
        
        # Start the update timer
        self._timer = time.time()
        
        self._update_interval = update_interval
        self._monitor_duration = 300
        self._monitor_duration_slice = 60
        self._change_display_interval = 5
        self._last_update = None
        
        # Create the title card
        self._title = title
        self._current_action = None
        self._titlecard_action = ActionHandler( self, self._title, 0, None )
        self._titlecard_action.__enter__()
        self._current_action = self._titlecard_action
    
    
    def question( self, message: str, options: Sequence[object] ):
        """
        See class comments.
        """
        return self._receiver.question( message, options )
    
    
    def thread_index( self ) -> int:
        """
        See class comments.
        """
        return self._thread_index
    
    
    def num_threads( self ) -> int:
        """
        See class comments.
        """
        return self._num_threads
    
    
    def close( self ):  # MAIN
        self._titlecard_action.__exit__()
    
    
    def update( self, force = False ):  # WORKER
        """
        THREAD: WORKER
        """
        
        now = time.time()
        
        if not force \
                and (self._last_update == self._current_action) \
                and ((now - self._timer) < self._update_interval):
            return
        
        self._last_update = self._current_action
        
        if self._receiver.was_cancelled():
            raise TaskCancelledError()
        
        self._receiver.progress_update( self._current_action._create_update_info( None, EStream.PROGRESS ) )
        self._timer = now
    
    
    def action( self, title: str, count: int, text: TText ) -> "ActionHandler":  # WORKER
        """
        See `Mandate.action`.
        """
        
        # Make sure the previous item receives its last update
        self.update( force = True )
        
        return ActionHandler( self, title, count, text )
    
    
    def still_alive( self ):  # WORKER
        """
        See class comments.
        """
        self._current_action.still_alive()
    
    
    def print( self, message, stream: EStream ):
        """
        See class comments.
        """
        message = str( message )  # Always coerce to str because we shouldn't send arbitrary objects over threads
        self._message_records.append( message )
        self._receiver.progress_update( self._current_action._create_update_info( message, stream ) )


class ActionHandler:
    """
    Represents an activity the coder can wrap in
    
        ```
        with MCMD.action("doing something") as action:
            action.increment()
        ```
    
    To automatically inform the host (the user) of progress.
    """
    
    
    def __init__( self, owner, title: str, maximum: Optional[int], text: TText ):  # ANY
        """
        CONSTRUCTOR
        See `Mandate.action`.
        """
        assert maximum is None or type( maximum ) is int
        
        self._owner = owner  # type:ProgressReporter
        self._value = 0
        self._value_string = None
        self._title = title
        self._maximum = maximum or 0
        self._next = None  # type:ActionHandler
        self._previous = None  # type:ActionHandler
        self._op_start_time = time.time()
        self._op_start_ops = 0
        self._time_monitor = Queue()
        self._minute_timer = time.time()
        self._tensec_timer = time.time()
        self._time_display = 0
        self._total_timer = time.time()
        self.depth = None  # type:List[int]
        self.num_children = 0
        self.get_text = None
        self.__set_text( text )
    
    
    def __enter__( self ):  # WORKER
        """
        ENTER
        """
        self._previous = self._owner._current_action
        
        if self._previous:
            self._previous._next = self
            self.depth = self._previous.depth + [self._previous.num_children]
            self._previous.num_children += 1
        else:
            self.depth = [0]
        
        self._owner._current_action = self
        self._owner._timer = 0  # force an update when we change the title text
        self._owner.update()
        
        return self
    
    
    def __exit__( self, exc_type = None, exc_val = None, exc_tb = None ):  # WORKER
        """
        EXIT
        """
        self.set_text( "DONE" )
        self._owner.update( True )
        
        if self._previous:
            self._owner._current_action = self._previous
    
    
    def __set_text( self, text: TText ):
        if text is None:
            self.get_text = None
        elif text is True:
            self.get_text = str
        elif isinstance( text, str ):
            closure = text
            self.get_text = lambda x: closure.format( x )
        else:
            self.get_text = text
    
    
    def set_text( self, value: str ):
        """
        Sets the "interesting" field.
        See `Mandate.action`.
        """
        self.__set_text( value )
        self.__update()
    
    
    def set_value( self, value: int ):  # WORKER
        """
        Sets the progress of this action.
        """
        self._value = value
        self.__update()
    
    
    def __update( self ):
        if self.get_text is not None:
            self._value_string = self.get_text( self._value )
        
        self._owner.update()
    
    
    def still_alive( self ):  # WORKER
        """
        Keeps the UI alive without changing the progress bar value.
        This should be called to inform the user that the system is not frozen and progress is being made, even if we can't calculate how much.
        """
        self.__update()
    
    
    def increment( self, value = 1, text: TText = None ):  # WORKER
        """
        Increments the value of this action. See `set_value` and `set_text`.
        """
        self._value += value
        
        if text is not None:
            self.__set_text( text )
        
        self.__update()
    
    
    def _create_update_info( self, message: Optional[str], stream: EStream ) -> UpdateInfo:
        """
        Internally used to create the update object sent to the host.
        """
        # Every 1 minute record where we are at
        now = time.time()
        
        if (now - self._minute_timer) >= self._owner._monitor_duration_slice:
            self._time_monitor.put( (now, self._value) )
            self._minute_timer = now
        
        # Get the current slice of time
        
        while True:
            time_taken = now - self._op_start_time
            
            if time_taken < self._owner._monitor_duration or self._time_monitor.empty():
                break
            
            # If the time slice goes over five minutes then shift forward one minute using our _time_monitor
            item = self._time_monitor.get()
            self._op_start_time = item[0]
            self._op_start_ops = item[1]
        
        # In the last 5 minutes, how many operations completed?
        ops_complete = self._value - self._op_start_ops
        
        total_time = now - self._total_timer
        
        return UpdateInfo( uid = self._owner.uid,
                           depth = tuple( self.depth ),
                           text = self._title,
                           value = self._value,
                           max = self._maximum,
                           total_time = total_time,
                           sample_time = time_taken,
                           sample_complete = ops_complete,
                           thread_index = self._owner.thread_index(),
                           num_threads = self._owner.num_threads(),
                           message = message,
                           value_string = self._value_string,
                           stream = stream,
                           )
