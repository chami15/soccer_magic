"""
Testes unitários — pipeline/transformers/selecao.py
"""
from pipeline.transformers.selecao import transform_selecao


def _team(
    team_id: int = 1,
    name: str = "Brasil",
    country: str | None = "Brazil",
    group_name: str | None = "A",
    ranking_fifa: int | None = 1,
) -> dict:
    return {
        "id": team_id,
        "name": name,
        "country": country,
        "group_name": group_name,
        "ranking_fifa": ranking_fifa,
    }


def test_campos_basicos():
    r = transform_selecao(_team(team_id=5, name="Brasil", group_name="G", ranking_fifa=1))
    assert r["id"] == 5
    assert r["nome"] == "Brasil"
    assert r["grupo"] == "G"
    assert r["ranking_fifa"] == 1


def test_continente_none_quando_pais_nao_mapeado():
    # CONTINENTE_POR_PAIS está vazio — continente sempre None por enquanto
    r = transform_selecao(_team(country="Brazil"))
    assert r["continente"] is None


def test_continente_none_quando_pais_none():
    r = transform_selecao(_team(country=None))
    assert r["continente"] is None


def test_grupo_none():
    r = transform_selecao(_team(group_name=None))
    assert r["grupo"] is None


def test_ranking_fifa_none():
    r = transform_selecao(_team(ranking_fifa=None))
    assert r["ranking_fifa"] is None


def test_todos_opcionais_none():
    team = {"id": 99, "name": "Teste FC"}
    r = transform_selecao(team)
    assert r["id"] == 99
    assert r["nome"] == "Teste FC"
    assert r["continente"] is None
    assert r["grupo"] is None
    assert r["ranking_fifa"] is None
