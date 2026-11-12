"""Acrescenta 1000 registros (10.000 linhas) em workflows/conta_povoada.json.

Uso (a partir da raiz do repositório):
    python hydranomic/notebooks/scripts/gerar_conta_povoada.py

Cria 25 novas unidades consumidoras (14080 a 14104) com 40 meses cada
(2023-01 a 2026-04), com sazonalidade e ruído. Os registros existentes
(unidade 14079) são preservados. Cada registro ocupa 10 linhas no arquivo.
"""
import json
import math
import random
from pathlib import Path

ARQUIVO = Path(__file__).resolve().parents[2] / "workflows" / "conta_povoada.json"
N_UNIDADES = 25
MESES = [(a, m) for a in (2023, 2024, 2025) for m in range(1, 13)] + [(2026, m) for m in range(1, 5)]
CATEGORIAS = ["COMERCIAL", "RESIDENCIAL", "INDUSTRIAL", "PUBLICA"]
TARIFA_BASE = 51.5  # R$/m3 (agua + esgoto + tratamento)


def gerar_registros(semente=42):
    rnd = random.Random(semente)
    registros = []
    for i in range(N_UNIDADES):
        unidade = 14080 + i
        categoria = CATEGORIAS[i % len(CATEGORIAS)]
        base = rnd.randint(80, 400)
        for idx, (ano, mes) in enumerate(MESES):
            sazonal = 1 + 0.15 * math.sin((mes - 2) / 12 * 2 * math.pi)
            tendencia = 1 + 0.004 * idx
            ruido = rnd.uniform(0.92, 1.08)
            consumo = max(5, round(base * sazonal * tendencia * ruido))
            tarifa = TARIFA_BASE * (1 + 0.035 * (ano - 2023))
            total = round(consumo * tarifa, 2)
            agua = round(total * 0.405, 2)
            esgoto = round(total * 0.303, 2)
            tratamento = round(total - agua - esgoto, 2)
            registros.append({
                "id": f"{ano}-{mes:02d}",
                "unidade_consumidora": unidade,
                "categoria": categoria,
                "valor_total": total,
                "valor_agua": agua,
                "valor_esgoto": esgoto,
                "valor_tratamento": tratamento,
                "consumo_m3": consumo,
            })
    return registros


def formatar(r):
    return (
        "  {\n"
        f'    "id": "{r["id"]}",\n'
        f'    "unidade_consumidora": {r["unidade_consumidora"]},\n'
        f'    "categoria": "{r["categoria"]}",\n'
        f'    "valor_total": {r["valor_total"]:.2f},\n'
        f'    "valor_agua": {r["valor_agua"]:.2f},\n'
        f'    "valor_esgoto": {r["valor_esgoto"]:.2f},\n'
        f'    "valor_tratamento": {r["valor_tratamento"]:.2f},\n'
        f'    "consumo_m3": {r["consumo_m3"]}\n'
        "  }"
    )


def main():
    existentes = json.loads(ARQUIVO.read_text(encoding="utf-8"))
    ids_existentes = {(r["unidade_consumidora"], r["id"]) for r in existentes}
    novos = [r for r in gerar_registros() if (r["unidade_consumidora"], r["id"]) not in ids_existentes]
    todos = existentes + novos
    texto = "[\n" + ",\n".join(formatar(r) for r in todos) + "\n]\n"
    ARQUIVO.write_text(texto, encoding="utf-8")
    print(f"{len(novos)} registros adicionados ({len(novos) * 10} linhas). Total: {len(todos)} registros.")


if __name__ == "__main__":
    main()

