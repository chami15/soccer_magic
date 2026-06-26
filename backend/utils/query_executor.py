import psycopg2

from utils.db import Database
from utils.sql_manager import sql_manager


def executar_query(
    query_name: str,
    commit: bool = False,
    returning: bool = False,
    connection: str = "",
    params=None,
    **kwargs,
):
    """
    params    → tupla de valores para placeholders %s  (seguro contra SQL injection)
    kwargs    → variáveis {var} interpoladas no template (use só com valores internos)
    returning → faz commit e retorna as linhas do RETURNING (INSERT/UPDATE/DELETE)
    """
    query_sql = sql_manager.load_query(query_name, **kwargs)

    # uma retentativa com conexao nova: conexoes ociosas do pool podem cair
    # (ex.: timeout do pooler do Supabase) entre uma query e outra.
    for tentativa in range(2):
        try:
            with Database(sufix=connection) as conn:
                conn.execute(query_sql, params)

                if returning:
                    rows = conn.fetchall()
                    conn.commit()
                    if not rows:
                        return []
                    columns = [desc[0] for desc in conn.get_cur().description]
                    return [dict(zip(columns, row)) for row in rows]

                if commit:
                    rows_affected = conn.get_cur().rowcount
                    conn.commit()
                    return rows_affected

                rows = conn.fetchall()
                if not rows:
                    return []

                columns = [desc[0] for desc in conn.get_cur().description]
                return [dict(zip(columns, row)) for row in rows]
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            if tentativa == 1:
                raise
