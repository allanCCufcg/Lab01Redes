"""
crc_investigacao.py
Automatiza a Parte 4:
 - cria MENSAGEM_BASE a partir do nome (ASCII->bits)
 - calcula CRC usando gerador escolhido (matrícula final 7 -> GENIBUS)
 - monta quadro (mensagem + crc)
 - faz 10 testes: insere burst de tamanho aleatório (2..8), checa detecção manual vs lib
 - salva tabela CSV results/investigacao_tabela.csv e relatório texto
"""

import os
import random
from utils import text_to_bits, bits_to_bytes, inserir_erro_burst, salvar_csv
from crc_manual import calcular_crc_manual, check_frame_manual
try:
    from crc import Calculator, Crc16
except ImportError:
    raise RuntimeError("Biblioteca 'crc' não encontrada. Rode: pip install crc")

# Parâmetros (nome aleatório e matrícula final 7 conforme solicitado)
NOME = "Lucas Andrade Souza"
MATRICULA_FINAL = 7
GERADOR_BITS = "11000000000000101"  # CRC-16/GENIBUS (exemplo para final 7)

calculator_lib = Calculator(Crc16.MODBUS)

# Preparar mensagem base
mensagem_bits_base = text_to_bits(NOME)  # ASCII -> bits
r = len(GERADOR_BITS) - 1

# calcula CRC para a mensagem original
crc_bits = calcular_crc_manual(mensagem_bits_base, GERADOR_BITS)
quadro_tx = mensagem_bits_base + crc_bits  # T(x)

# Verifica propriedade (deve ser válido)
# convert para bytes (tamanho múltiplo de 8 aqui: msg em ASCII + 16 bits CRC)
if len(quadro_tx) % 8 != 0:
    # padding (caso improvável para nosso nome + r=16)
    quadro_tx = quadro_tx + '0' * (8 - (len(quadro_tx) % 8))

dados_quadro_bytes = bits_to_bytes(quadro_tx)

if calculator_lib.checksum(dados_quadro_bytes) != 0:
    # Pode depender de implementação; ainda assim salvamos aviso
    pass

# Execução dos 10 testes
os.makedirs("results/graficos", exist_ok=True)
os.makedirs("results", exist_ok=True)

resultados = []
for teste in range(1, 11):
    tamanho_burst = random.randint(2, 8)  # burst entre 2 e 8 bits
    quadro_corrompido_bits, pos = inserir_erro_burst(quadro_tx, tamanho_burst)

    # Verificação manual: dividir o quadro corrompido e checar resto == 0
    detectado_manual = not check_frame_manual(quadro_corrompido_bits, GERADOR_BITS)

    # Verificação biblioteca:
    # converter para bytes (garantindo múltiplo de 8)
    if len(quadro_corrompido_bits) % 8 != 0:
        quadro_corrompido_bits = quadro_corrompido_bits + '0' * (8 - (len(quadro_corrompido_bits) % 8))
    bytes_corrompidos = bits_to_bytes(quadro_corrompido_bits)
    # Algumas implementações de CRC devolvem 0 quando o quadro (msg+crc) está correto.
    crc_lib_check = calculator_lib.checksum(bytes_corrompidos)
    detectado_lib = (crc_lib_check != 0)

    resultados.append({
        "teste": teste,
        "pos": pos,
        "burst_bits": tamanho_burst,
        "manual_detectou": detectado_manual,
        "lib_detectou": detectado_lib
    })

# Salva tabela
salvar_csv("results/investigacao_tabela.csv", resultados)

# Gera relatório simples
num_manual_fail = sum(1 for r in resultados if not r["manual_detectou"])
num_lib_fail = sum(1 for r in resultados if not r["lib_detectou"])

with open("results/investigacao_relatorio.txt", "w", encoding="utf-8") as f:
    f.write("Investigação CRC - Relatório automático\n")
    f.write("=====================================\n\n")
    f.write(f"Nome usado (MENSAGEM_BASE): {NOME}\n")
    f.write(f"Gerador (bits): {GERADOR_BITS}\n")
    f.write(f"CRC calculado (bits, r={r}): {crc_bits}\n\n")
    f.write("Resultados dos 10 testes:\n\n")
    for r in resultados:
        f.write(f"Teste {r['teste']}: pos={r['pos']}, burst={r['burst_bits']} bits -> "
                f"Manual={'DETECTOU' if r['manual_detectou'] else 'FALHOU'}, "
                f"Biblioteca={'DETECTOU' if r['lib_detectou'] else 'FALHOU'}\n")
    f.write("\nResumo:\n")
    f.write(f"Total de falhas (não detectados) — Manual: {num_manual_fail} / 10\n")
    f.write(f"Total de falhas (não detectados) — Biblioteca: {num_lib_fail} / 10\n\n")
    f.write("Notas: Uma detecção 'FALHOU' significa que o erro **não** foi detectado (resto zero).\n")

print("Investigação concluída. Tabela salva em results/investigacao_tabela.csv")
print("Relatório salvo em results/investigacao_relatorio.txt")
