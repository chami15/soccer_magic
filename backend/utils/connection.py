import os
import threading

import psycopg2
from psycopg2 import pool as psycopg2_pool
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

_pools: dict[str, psycopg2_pool.ThreadedConnectionPool] = {}
_pools_lock = threading.Lock()


def _pool_config(sufix: str | None):
    if sufix:
        host = os.getenv(f"POSTGRES_HOST_{sufix}", os.getenv("POSTGRES_HOST", "localhost"))
        port = int(os.getenv(f"POSTGRES_PORT_{sufix}", os.getenv("POSTGRES_PORT", 5432)))
        database = os.getenv(f"POSTGRES_DB_{sufix}")
        user = os.getenv(f"POSTGRES_USER_{sufix}")
        password = os.getenv(f"POSTGRES_PASSWORD_{sufix}")
    else:
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = int(os.getenv("POSTGRES_PORT", 5432))
        database = os.getenv("POSTGRES_DB")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")

    minconn = int(os.getenv(f"POSTGRES_POOL_MIN_{sufix}" if sufix else "POSTGRES_POOL_MIN", 1))
    maxconn = int(os.getenv(f"POSTGRES_POOL_MAX_{sufix}" if sufix else "POSTGRES_POOL_MAX", 10))

    return {
        "host": host,
        "port": port,
        "database": database,
        "user": user,
        "password": password,
        "minconn": minconn,
        "maxconn": maxconn,
    }


def _get_pool(sufix: str | None) -> psycopg2_pool.ThreadedConnectionPool:
    key = sufix or "_default"
    if key in _pools:
        return _pools[key]

    with _pools_lock:
        if key not in _pools:
            cfg = _pool_config(sufix)
            _pools[key] = psycopg2_pool.ThreadedConnectionPool(
                cfg["minconn"],
                cfg["maxconn"],
                host=cfg["host"],
                port=cfg["port"],
                database=cfg["database"],
                user=cfg["user"],
                password=cfg["password"],
                # evita que a conexao seja derrubada por inatividade durante
                # os intervalos em que o pipeline esta so fazendo chamadas HTTP
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5,
            )
        return _pools[key]


def close_all_pools() -> None:
    """Fecha todas as conexões de todos os pools. Usar no shutdown da aplicação."""
    with _pools_lock:
        for pool in _pools.values():
            pool.closeall()
        _pools.clear()


class PostgreConn:
    def __init__(self, sufix=None):
        self.sufix = sufix
        self.pool = None
        self.conn = None
        self.cur = None
        try:
            self.pool = _get_pool(sufix)
            self.conn = self.pool.getconn()
            self.cur = self.conn.cursor()
        except Exception as e:
            print(f"Erro ao se conectar com o banco: {e}")
            self.pool = None
            self.conn = None
            self.cur = None

    def close(self):
        if self.cur:
            self.cur.close()
        if self.pool and self.conn:
            # se a conexao caiu (closed != 0), descarta em vez de devolver
            # pro pool — devolver uma conexao morta contaminaria a proxima
            # query que a reutilizasse com o mesmo erro.
            esta_quebrada = self.conn.closed != 0
            self.pool.putconn(self.conn, close=esta_quebrada)
        self.cur = None
        self.conn = None

    def commit(self):
        if self.conn:
            self.conn.commit()

    def rollback(self):
        if self.conn:
            self.conn.rollback()

    def execute(self, query, params=None):
        try:
            if self.cur:
                self.cur.execute(query, params)
        except Exception as e:
            print(f"Erro ao executar query: {e}")
            self.rollback()
            raise

    def execute_values(self, insert_query, values_list):
        try:
            if self.cur:
                execute_values(self.cur, insert_query, values_list)
        except Exception as e:
            print(f"Erro ao executar inserção: {e}")
            self.rollback()
            raise

    def fetchall(self):
        return self.cur.fetchall() if self.cur else None

    def fetchone(self):
        return self.cur.fetchone() if self.cur else None

    def fetchmany(self):
        return self.cur.fetchmany() if self.cur else None

    def get_cur(self):
        return self.cur

    def get_conn(self):
        return self.conn
