"""
crc_comparacao.py
Script para comparar desempenho (tempo e pico de memória) entre
 - implementação manual (crc_manual.calcular_crc_manual)
 - biblioteca crc (crc.Calculator)
Gera dois gráficos salvos em results/graficos/
"""

import os
import time
import tracemalloc
import matplotlib.pyplot as plt
import json

from crc_manual import calcular_crc_manual
from utils import bits_to_bytes
from crc import Crc16
# Tenta importar a lib crc
try:
    from crc import Calculator, Crc16
except Exception as e:
    raise RuntimeError("Biblioteca 'crc' não encontrada. Rode: pip install crc") from e

# Configuração
GERADOR_BITS = "11000000000000101"  # CRC-16/GENIBUS (uso do exemplo)
calculator_lib = Calculator(Crc16.GENIBUS)

TAMANHOS_BYTES = [1500, 3000, 6000, 16000]
RESULTS = []

os.makedirs("results/graficos", exist_ok=True)

for tamanho in TAMANHOS_BYTES:
    print(f"Processando tamanho {tamanho} bytes...")
    # gerar bytes aleatórios
    dados_bytes = os.urandom(tamanho)
    dados_bits = "".join(format(b, "08b") for b in dados_bytes)

    # Mensuração - Manual
    tracemalloc.start()
    t0 = time.perf_counter()
    crc_manual = calcular_crc_manual(dados_bits, GERADOR_BITS)
    t1 = time.perf_counter()
    _, pico_manual = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Mensuração - Biblioteca
    tracemalloc.start()
    t2 = time.perf_counter()
    crc_lib = calculator_lib.checksum(dados_bytes)
    t3 = time.perf_counter()
    _, pico_lib = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    resultado = {
        "tamanho": tamanho,
        "tempo_manual_s": t1 - t0,
        "tempo_lib_s": t3 - t2,
        "pico_mem_manual_kib": pico_manual / 1024.0,
        "pico_mem_lib_kib": pico_lib / 1024.0
    }
    RESULTS.append(resultado)

# Salva JSON/CSV simples
with open("results/comparacao_resultados.json", "w", encoding="utf-8") as f:
    json.dump(RESULTS, f, indent=2)

# Plots
x = [r["tamanho"] for r in RESULTS]
tman = [r["tempo_manual_s"] for r in RESULTS]
tlib = [r["tempo_lib_s"] for r in RESULTS]

plt.figure(figsize=(8,5))
plt.plot(x, tman, marker='o', label="Manual")
plt.plot(x, tlib, marker='o', label="Biblioteca")
plt.xlabel("Tamanho (bytes)")
plt.ylabel("Tempo (s)")
plt.title("Tempo de execução: Manual vs Biblioteca")
plt.legend()
plt.grid(True)
plt.savefig("results/graficos/tempo_execucao.png", dpi=150)
plt.close()

mman = [r["pico_mem_manual_kib"] for r in RESULTS]
mlib = [r["pico_mem_lib_kib"] for r in RESULTS]

plt.figure(figsize=(8,5))
plt.plot(x, mman, marker='o', label="Manual")
plt.plot(x, mlib, marker='o', label="Biblioteca")
plt.xlabel("Tamanho (bytes)")
plt.ylabel("Pico de Memória (KiB)")
plt.title("Pico de memória: Manual vs Biblioteca")
plt.legend()
plt.grid(True)
plt.savefig("results/graficos/memoria_execucao.png", dpi=150)
plt.close()

print("Comparação concluída. Resultados salvos em results/ e gráficos em results/graficos/")
print("Resumo:", RESULTS)
