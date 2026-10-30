
import requests

from .api import consultar_sidra
from .tratamento import tratar_dados


def main():
    print("\n========================================")
    print("      IBGE SIDRA - PRODUCAO INDUSTRIAL")
    print("========================================")

    try:
        dados = consultar_sidra()
        resultados = tratar_dados(dados)

        if not resultados:
            print("Nenhum dado encontrado.")
            return

        print("\nBrasil | Indice de producao (2022 = 100)\n")

        print(f"{'PERIODO':<20} {'INDICE':>10} {'VS. BASE':>12}")
        print("-" * 44)

        for item in resultados:
            print(
                f"{item['periodo']:<20}"
                f"{item['indice']:>10.2f}"
                f"{item['diferenca_base']:>+11.2f}%"
            )

        print("-" * 44)

        ultimo = resultados[-1]

        print("\nRESUMO")
        print(f"Ultimo periodo: {ultimo['periodo']}")
        print(f"Indice atual: {ultimo['indice']:.2f}")

        if ultimo["indice"] > 100:
            print("Producao acima do nivel-base de 2022.")

        elif ultimo["indice"] < 100:
            print("Producao abaixo do nivel-base de 2022.")
            
        else:
            print("Producao igual ao nivel-base de 2022.")

    except requests.RequestException as erro:
        print(f"Erro na consulta: {erro}")

    except (ValueError, KeyError, TypeError) as erro:
        print(f"Erro no processamento: {erro}")


if __name__ == "__main__":
    main()
