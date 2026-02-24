import requests
import pandas as pd

BASE_URL = "https://apidadosabertos.saude.gov.br/daf/estoque-medicamentos-bnafar-horus"


def normalizar_codigo_municipio(codigo: int | str) -> str:
    """
    Remove o último dígito do código IBGE do município.
    Ex: 230445 -> 23044
    """
    codigo = str(codigo)
    return codigo[:-1]


def buscar_bnafar(
    codigo_uf: int | str,
    codigo_municipio: int | str,
    codigo_catmat: str,
    anomes_posicao_estoque: str,
    limit: int = 1000
) -> pd.DataFrame:
    """
    Consulta a API BNAFAR (Hórus) e retorna DataFrame com o estoque.
    """

    params = {
        "codigo_uf": codigo_uf,
        "codigo_municipio": normalizar_codigo_municipio(codigo_municipio),
        "codigo_catmat": codigo_catmat,
        "anomes_posicao_estoque": anomes_posicao_estoque,
        "limit": limit,
        "offset": 0
    }

    all_data = []

    while True:
        resp = requests.get(BASE_URL, params=params)
        resp.raise_for_status()

        data = resp.json().get("parametros", [])

        if not data:
            break

        all_data.extend(data)

        if len(data) < limit:
            break

        params["offset"] += limit

    if not all_data:
        return pd.DataFrame()

    return pd.DataFrame(all_data)
