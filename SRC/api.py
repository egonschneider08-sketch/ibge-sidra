
import requests


def consultar_sidra(categoria="129336", variavel="12606", meses=6):
    """Consulta a tabela 8888 da PIM-PF por setor, indicador e período."""

    if not (str(categoria).isdigit() and str(variavel).isdigit()):
        raise ValueError("Categoria e variável devem ser códigos numéricos do IBGE")

    if not isinstance(meses, int) or not 1 <= meses <= 120:
        raise ValueError("meses deve estar entre 1 e 120")

    url = (
        "https://apisidra.ibge.gov.br/values/"
        f"t/8888/n1/all/v/{variavel}/"
        f"p/last%20{meses}/c544/{categoria}"
    )
    
    resposta = requests.get(url, timeout=30)
    resposta.raise_for_status()
    return resposta.json()


def consultar_metadados(tabela):
    url = (
        "https://servicodados.ibge.gov.br/"
        f"api/v3/agregados/{tabela}/metadados"
    )

    resposta = requests.get(url, timeout=30)
    resposta.raise_for_status()

    return resposta.json()
