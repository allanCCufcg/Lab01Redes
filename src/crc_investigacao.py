"""
crc_investigacao.py - Análise de detecção de erros com CRC
Implementação da Parte 4 do projeto:
 - Converte nome em bits ASCII para formar a mensagem base
 - Aplica CRC-16/MAXIM (baseado no dígito final da matrícula)
 - Realiza testes com bursts de erro variados
 - Documenta casos onde o CRC falha em detectar erros
"""

import os
import random
import sys
sys.path.append('/mnt/user-data/uploads')
from utils import text_to_bits, bits_to_bytes, inserir_erro_burst, salvar_csv
from crc_manual import calcular_crc_manual, check_frame_manual

try:
    from crc import Calculator, Crc16
except ImportError:
    print("Aviso: Biblioteca 'crc' não encontrada. Usando apenas implementação manual.")
    Calculator = None

# Configurações do experimento
NOME = "Lucas Andrade Souza"  # Meu nome completo para gerar a mensagem
MATRICULA_FINAL = 7
# CRC-16/MAXIM corresponde ao dígito 7
GERADOR_BITS = "10011000000010001"  # Polinômio: x^16 + x^15 + x^13 + x^7 + x^4 + 1

# Convertendo o nome para sequência de bits
mensagem_bits_base = text_to_bits(NOME)
r = len(GERADOR_BITS) - 1

print(f"Nome: {NOME}")
print(f"Tamanho da mensagem: {len(mensagem_bits_base)} bits ({len(mensagem_bits_base)//8} bytes)")
print(f"Gerador CRC-16/MAXIM: {GERADOR_BITS}")
print(f"Grau r: {r}")
print()

# Calculando o CRC da mensagem original
crc_bits = calcular_crc_manual(mensagem_bits_base, GERADOR_BITS)
quadro_tx = mensagem_bits_base + crc_bits  # Quadro completo para transmissão

print(f"CRC calculado: {crc_bits}")
print(f"Quadro completo (mensagem + CRC): {len(quadro_tx)} bits")
print()

# Preparando estrutura para salvar resultados
os.makedirs("results", exist_ok=True)

resultados = []
erros_nao_detectados = []

# Seed fixo para reproduzir os resultados se necessário
random.seed(42)

for teste in range(1, 11):
    # Estratégia: começar com bursts pequenos e aumentar gradualmente
    # Isso aumenta as chances de encontrar falhas de detecção
    if teste <= 5:
        tamanho_burst = random.randint(2, 8)
    else:
        tamanho_burst = random.randint(8, 16)
    
    quadro_corrompido_bits, pos = inserir_erro_burst(quadro_tx, tamanho_burst)
    
    # Verifica se o erro foi detectado usando divisão polinomial
    detectado_manual = not check_frame_manual(quadro_corrompido_bits, GERADOR_BITS)
    
    resultado = {
        "teste": teste,
        "pos": pos,
        "burst_bits": tamanho_burst,
        "manual_detectou": detectado_manual,
        "padrão_erro": quadro_tx[pos:pos+tamanho_burst] + " -> " + quadro_corrompido_bits[pos:pos+tamanho_burst]
    }
    
    resultados.append(resultado)
    
    if not detectado_manual:
        erros_nao_detectados.append(resultado)
    
    if detectado_manual:
        print(f"Teste {teste}: erro detectado (burst de {tamanho_burst} bits)")
    else:
        print(f"Teste {teste}: FALHA - erro NÃO detectado (burst de {tamanho_burst} bits)")

# Salvando resultados em CSV
salvar_csv("results/investigacao_tabela.csv", resultados)

# Gerando relatório detalhado
num_manual_fail = sum(1 for r in resultados if not r["manual_detectou"])

with open("results/investigacao_relatorio.txt", "w", encoding="utf-8") as f:
    f.write("Parte 4: Análise Investigativa da Detecção de Erros\n")
    f.write("=" * 60 + "\n\n")
    
    f.write("4.1 - Configuração do Cenário\n")
    f.write("-" * 30 + "\n")
    f.write(f"MENSAGEM: {NOME}\n")
    if len(mensagem_bits_base) > 100:
        f.write(f"MENSAGEM_BASE (bits ASCII): {mensagem_bits_base[:50]}...{mensagem_bits_base[-50:]}\n")
    else:
        f.write(f"MENSAGEM_BASE (bits ASCII): {mensagem_bits_base}\n")
    f.write(f"Tamanho da mensagem: {len(mensagem_bits_base)} bits\n")
    f.write(f"Matrícula final: {MATRICULA_FINAL}\n")
    f.write(f"Gerador usado: CRC-16/MAXIM\n")
    f.write(f"Gerador (bits): {GERADOR_BITS}\n")
    f.write(f"CRC calculado: {crc_bits}\n\n")
    
    f.write("4.2 - Resultados dos 10 Testes\n")
    f.write("-" * 30 + "\n\n")
    
    f.write("| Teste | Posição | Tamanho Burst | Detecção | Padrão de Erro |\n")
    f.write("|-------|---------|---------------|----------|----------------|\n")
    
    for r in resultados:
        status = "SIM" if r["manual_detectou"] else "NÃO"
        f.write(f"| {r['teste']:^5} | {r['pos']:^7} | {r['burst_bits']:^13} | {status:^8} | {r['padrão_erro']} |\n")
    
    f.write("\n\nResumo:\n")
    f.write(f"Total de erros detectados: {10 - num_manual_fail} / 10\n")
    f.write(f"Total de erros NÃO detectados: {num_manual_fail} / 10\n\n")
    
    if erros_nao_detectados:
        f.write("Erros não detectados (Pontos Cegos):\n")
        f.write("-" * 30 + "\n")
        for erro in erros_nao_detectados:
            f.write(f"Teste {erro['teste']}: Burst de {erro['burst_bits']} bits na posição {erro['pos']}\n")
            f.write(f"  Padrão: {erro['padrão_erro']}\n\n")
    
    f.write("\nAnálise e Reflexões:\n")
    f.write("-" * 30 + "\n")
    f.write("1. O CRC-16/MAXIM tem capacidade de detectar:\n")
    f.write("   - Todos os erros de bit único\n")
    f.write("   - Todos os erros de burst até 16 bits\n")
    f.write("   - Todos os erros com número ímpar de bits\n\n")
    
    if num_manual_fail > 0:
        f.write("2. Foram encontrados erros não detectados, demonstrando as limitações do CRC:\n")
        f.write("   - Alguns padrões específicos de erro podem resultar em um resto zero\n")
        f.write("   - Isso ocorre quando o erro é divisível pelo polinômio gerador\n\n")
    else:
        f.write("2. Todos os erros foram detectados nestes testes, mas isso não significa\n")
        f.write("   que o CRC é perfeito. Com mais testes ou bursts maiores, eventualmente\n")
        f.write("   encontraríamos padrões não detectados.\n\n")
    
    f.write("3. Limitações conhecidas do CRC:\n")
    f.write("   - Não pode detectar 100% dos erros para bursts > r bits\n")
    f.write("   - A probabilidade de não detecção é aproximadamente 2^(-r) para erros aleatórios\n")
    f.write("   - Para CRC-16, isso significa ~0.0015% de chance de falha\n")

print("\nInvestigação concluída!")
print(f"Erros não detectados: {num_manual_fail} de 10 testes")
print("Arquivos salvos em: results/")

# Se não encontramos nenhuma falha, vamos tentar com bursts maiores
if num_manual_fail == 0:
    print("\nTentando encontrar um erro não detectado com testes adicionais...")
    for extra in range(50):  # Mais tentativas para demonstrar a limitação
        tamanho_burst = random.randint(16, 32)  # Bursts além da capacidade garantida
        quadro_corrompido_bits, pos = inserir_erro_burst(quadro_tx, tamanho_burst)
        if not check_frame_manual(quadro_corrompido_bits, GERADOR_BITS):
            print(f"ENCONTRADO! Erro não detectado: burst de {tamanho_burst} bits na posição {pos}")
            with open("results/investigacao_relatorio.txt", "a", encoding="utf-8") as f:
                f.write(f"\n\nTeste adicional: Encontrado erro não detectado!\n")
                f.write(f"Burst de {tamanho_burst} bits na posição {pos}\n")
            break