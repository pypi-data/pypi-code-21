"""Implements a connection pool for use in this package."""
import queue
import weakref

class PooledConnection(object):
    """Wraps a DBAPI 2.0 connection for use with connection pools.
    
    This class calls DBAPI 2.0 methods on its underlying connection.
    It only guarantees that it can handle the DBAPI-compliant subset
    of any underlying cursor's functionality.
    """
    
    def __init__(self, pool, conn):
        """Bundles a connection with a specific pool.
        
        :param pool: The source connection pool.
        
        :param conn: The underlying connection.
        """
        self._pool = pool
        self._conn = conn
        
        self._cursor_refs = []
    
    def close(self):
        """Puts the connection back in the pool."""
        if self._conn is not None:
            conn = self._conn
            self._conn = None
            
            for cur_ref in self._cursor_refs:
                cur = cur_ref()
                if cur is not None:
                    try:
                        cur.close()
                    except self._pool._dbapi.Error:
                        pass
            
            self._pool._putconn(conn)
    
    def commit(self):
        """Commits changes to the underlying connection."""
        self._conn.commit()
    
    def rollback(self):
        """Rolls back the underlying connection."""
        self._conn.rollback()
    
    def cursor(self):
        """Allocates a cursor from the underlying connection.
        
        Also store a weak-reference to this cursor so it can be
        closed when the connection is 'closed'.
        """
        cursor = self._conn.cursor()
        self._cursor_refs.append(weakref.ref(cursor))
        return cursor
    
    def __enter__(self):
        """Supplies the associated connection to block context."""
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        """Puts the connection back in the pool when a block exits."""
        if exc_type is None or (not issubclass(exc_type, self._pool._dbapi.Error)):
            self.close()
        else:
            self._pool._decrement_conn_count()
    
    def __del__(self):
        """Puts the connection back in the pool when this object is deleted."""
        # Make sure this "closes".
        self.close()
        # There is no superclass destructor, but it would be called here.

class ConnectionPool(object):
    """A pool of DBAPI 2.0 connections."""
    
    def __init__(self, dbapi_module, pool_size, conn_limit,
            *connect_args, **connect_kwargs):
        """Initializes a pool, connections will be generate  as-needed."""
        self._pool_size = pool_size
        self._conn_limit = conn_limit
        self._num_conns = 0
        
        self._dbapi = dbapi_module
        
        self._connect = self._dbapi.connect
        self._conn_args = connect_args
        self._conn_kwargs = connect_kwargs
        
        self._pool = queue.Queue(self._pool_size)
    
    def _create_connection(self):
        """Creates a connection and puts in in the pool."""
        self._pool.put(
            self._connect(*self._conn_args, **self._conn_kwargs))
        self._num_conns += 1
    
    def _getconn(self, block=True, timeout=None):
        """Returns an unwrapped connection object from the pool.
        
        With `block` set to False or `timeout` set, this method
        will raise `queue.Empty` when the pool cannot find a
        connection quickly enough."""
        if self._pool.empty() and self._num_conns < self._conn_limit:
            self._create_connection()
        
        return self._pool.get(block, timeout)
    
    def get(self, block=True, timeout=None):
        """Returns a wrapped connection object from the pool.
        
        As `ConnectionPool._getconn`, may raise `queue.Empty`."""
        return PooledConnection(self, self._getconn(block, timeout))
    
    def _putconn(self, conn, block=True, timeout=None):
        """Returns a connection to the connection pool.
        
        Connection may not actually return to the pool,
        such as if it is closed or the pool is full."""
        try:
            # Perform a rollback just in case and put the connection back.
            conn.rollback()
            self._pool.put(conn, block, timeout)
        except self._dbapi.Error:
            # This occuring during a rollback means the connection is closed.
            # Because of this we're just going to drop it.
            self._num_conns -= 1
        except queue.Full:
            # There are enough idle connections that we don't need this one.
            # We're going to close and drop it.
            conn.close()
            self._num_conns -= 1
    
    def put(self, wrapped_conn, block=True, timeout=None):
        """Returns a wrapped connection to the pool."""
        # This just calls close on the wrapped connection.
        # That should handle it if that's what the argument actually was.
        wrapped_conn.close()
    
    def _decrement_conn_count(self):
        self._num_conns -= 1
