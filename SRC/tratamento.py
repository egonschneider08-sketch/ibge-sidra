
def tratar_dados(dados):
    resultados = []

    for item in dados[1:]:
        periodo = item.get("D3N")
        valor = item.get("V")

        try:
            valor = float(valor)
        except (ValueError, TypeError):
            continue

        diferenca_base = valor - 100

        resultados.append({
            "periodo": periodo,
            "indice": round(valor, 2),
            "diferenca_base": round(diferenca_base, 2)
        })

    return resultados
