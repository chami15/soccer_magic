"""
Teste manual e isolado: insere 1 linha em dim_selecao (Brasil) usando
o pipeline raw-SQL (utils/executar_query) para validar a conexao com
o Postgres do Supabase antes de integrar ao pipeline completo.

Rodar localmente (fora do sandbox remoto, onde a porta do Postgres
nao e bloqueada):

    cd backend
    python3 test_insert_selecao.py
"""

from utils.query_executor import executar_query

if __name__ == "__main__":
    rows = executar_query(
        "selecao:create_table",
        commit=True,
    )
    print("create_table ok")

    inserted = executar_query(
        "selecao:insert_teste",
        returning=True,
        params=(4748, "Brazil", "America do Sul", "G", None),
    )
    print("inserido:", inserted)

    check = executar_query(
        "selecao:select_teste",
        params=(4748,),
    )
    print("select:", check)
