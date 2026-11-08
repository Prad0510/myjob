import os
import threading
from contextlib import contextmanager
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from dotenv import load_dotenv

from src.utils.logger import get_logger

load_dotenv()
logger = get_logger("database")

_pool: ThreadedConnectionPool | None = None
_pool_lock = threading.Lock()


def _create_pool() -> ThreadedConnectionPool:
    host = os.getenv("DATABASE_HOST", "localhost")
    port = int(os.getenv("DATABASE_PORT", 5432))
    database = os.getenv("DATABASE_NAME", "myjob")
    user = os.getenv("DATABASE_USER", "postgres")
    password = os.getenv("DATABASE_PASSWORD", "")

    min_conn = int(os.getenv("DB_POOL_MIN", 1))
    max_conn = int(os.getenv("DB_POOL_MAX", 10))

    logger.info(
        f"Initializing database connection pool: host={host}:{port}, "
        f"db={database}, user={user}, min={min_conn}, max={max_conn}"
    )

    return ThreadedConnectionPool(
        minconn=min_conn,
        maxconn=max_conn,
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
    )


def get_pool() -> ThreadedConnectionPool:
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = _create_pool()
    return _pool


class PooledConnectionWrapper:
    """
    Wraps a raw connection checked out from ThreadedConnectionPool.
    Calling close() returns the connection to the pool rather than closing the physical socket.
    """

    def __init__(self, raw_conn, pool: ThreadedConnectionPool):
        self._raw_conn = raw_conn
        self._pool = pool
        self._returned = False

    def close(self):
        if not self._returned:
            self._returned = True
            try:
                # Reset any uncommitted transaction state before returning
                if not self._raw_conn.closed:
                    self._raw_conn.rollback()
                self._pool.putconn(self._raw_conn)
            except Exception as e:
                logger.warning(f"Error returning connection to pool: {e}")

    def __enter__(self):
        return self._raw_conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            try:
                self._raw_conn.rollback()
            except Exception:
                pass
        self.close()

    def __getattr__(self, name):
        return getattr(self._raw_conn, name)


def get_connection():
    """
    Get a pooled connection wrapped so that conn.close() returns it to the pool.
    Fully backwards-compatible with existing code.
    """
    pool = get_pool()
    raw_conn = pool.getconn()
    return PooledConnectionWrapper(raw_conn, pool)


@contextmanager
def get_db_connection():
    """
    Context manager yielding a pooled connection and returning it upon exit.
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_db_cursor(commit: bool = False):
    """
    Context manager yielding a cursor from a pooled connection.
    Automatically commits on normal exit if commit=True.
    Rolls back on exception and returns connection to pool.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        finally:
            cursor.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def close_pool():
    """
    Close all connections in the pool during application shutdown.
    """
    global _pool
    with _pool_lock:
        if _pool is not None and not _pool.closed:
            _pool.closeall()
            _pool = None
            logger.info("Database connection pool closed.")
