import requests
import unicodedata

BASE_UF_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"

def normalize(texto: str) -> str:
    """
    Normaliza texto removendo acentos e deixando minúsculo.
    """
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(ch for ch in texto if not unicodedata.combining(ch))

# -------- Estados --------

def fetch_all_states() -> list[dict]:
    """
    Busca todos os estados ordenados por nome.
    """
    url = f"{BASE_UF_URL}?orderBy=nome"
    resp = requests.get(url)
    return resp.json() if resp.status_code == 200 else []

def find_states_by_input(entrada: str) -> list[dict]:
    """
    Procura estados por código, sigla ou nome parcial.
    """
    entrada_norm = normalize(entrada)
    estados = fetch_all_states()
    resultados = []

    for est in estados:
        sigla_norm = normalize(est["sigla"])
        nome_norm = normalize(est["nome"])
        id_norm = str(est["id"])

        if entrada_norm == id_norm:
            return [est]
        if sigla_norm == entrada_norm:
            return [est]
        if entrada_norm in nome_norm:
            resultados.append(est)

    return resultados

# -------- Municípios --------

def fetch_municipios_by_state_id(uf_id: int) -> list[dict]:
    """
    Busca todos os municípios de um estado dado o ID IBGE.
    """
    url = f"{BASE_UF_URL}/{uf_id}/municipios"
    resp = requests.get(url)
    return resp.json() if resp.status_code == 200 else []

def find_municipios(uf_id: int, entrada: str) -> list[dict]:
    """
    Procura municípios pelo nome parcial ou código.
    """
    entrada_norm = normalize(entrada)
    municipios = fetch_municipios_by_state_id(uf_id)
    resultados = []

    for muni in municipios:
        nome_norm = normalize(muni["nome"])
        id_norm = str(muni["id"])
        if entrada_norm == id_norm:
            return [muni]
        if entrada_norm in nome_norm:
            resultados.append(muni)

    return resultados
