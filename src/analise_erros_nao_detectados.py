"""
analise_erros_nao_detectados.py
Programa para encontrar e analisar padrões de erro que não são detectados pelo CRC
"""

import sys
sys.path.append('/mnt/user-data/uploads')
from utils import text_to_bits, inserir_erro_burst
from crc_manual import calcular_crc_manual, check_frame_manual
import random

# Configurações
NOME = "Lucas Andrade Souza"
GERADOR_BITS = "10011000000010001"  # CRC-16/MAXIM

# Preparar mensagem
mensagem_bits = text_to_bits(NOME)
crc_bits = calcular_crc_manual(mensagem_bits, GERADOR_BITS)
quadro_original = mensagem_bits + crc_bits

print("=== Análise Detalhada de Erros Não Detectados ===\n")
print(f"Nome: {NOME}")
print(f"Tamanho do quadro: {len(quadro_original)} bits")
print(f"CRC: {crc_bits}")
print(f"Gerador: {GERADOR_BITS} (CRC-16/MAXIM)")
print()

# Encontrar múltiplos erros não detectados
erros_nao_detectados = []
testes_totais = 0

print("Procurando erros não detectados...\n")

# Testar diferentes tamanhos de burst
for tamanho_burst in range(17, 33):  # Bursts de 17 a 32 bits
    encontrados_neste_tamanho = 0
    
    for _ in range(100):  # 100 tentativas por tamanho
        testes_totais += 1
        
        # Gerar posição aleatória
        pos = random.randint(0, len(quadro_original) - tamanho_burst)
        
        # Inserir erro
        quadro_com_erro, _ = inserir_erro_burst(quadro_original, tamanho_burst, pos)
        
        # Verificar se foi detectado
        if not check_frame_manual(quadro_com_erro, GERADOR_BITS):
            encontrados_neste_tamanho += 1
            
            # Calcular o padrão de erro
            padrao_erro = ""
            for i in range(tamanho_burst):
                if quadro_original[pos + i] != quadro_com_erro[pos + i]:
                    padrao_erro += "1"
                else:
                    padrao_erro += "0"
            
            erro_info = {
                "posicao": pos,
                "tamanho": tamanho_burst,
                "padrao": padrao_erro,
                "original": quadro_original[pos:pos+tamanho_burst],
                "corrompido": quadro_com_erro[pos:pos+tamanho_burst]
            }
            
            erros_nao_detectados.append(erro_info)
            
            # Limitar para não gerar muitos exemplos
            if len(erros_nao_detectados) >= 10:
                break
    
    if encontrados_neste_tamanho > 0:
        print(f"Burst de {tamanho_burst} bits: {encontrados_neste_tamanho} erros não detectados encontrados")
    
    if len(erros_nao_detectados) >= 10:
        break

print(f"\nTotal de testes realizados: {testes_totais}")
print(f"Total de erros não detectados encontrados: {len(erros_nao_detectados)}")

# Salvar análise detalhada
with open("results/analise_erros_detalhada.txt", "w", encoding="utf-8") as f:
    f.write("ANÁLISE DETALHADA DOS ERROS NÃO DETECTADOS\n")
    f.write("=" * 60 + "\n\n")
    
    f.write(f"Configuração:\n")
    f.write(f"- Mensagem: {NOME}\n")
    f.write(f"- Gerador: CRC-16/MAXIM ({GERADOR_BITS})\n")
    f.write(f"- Tamanho do quadro: {len(quadro_original)} bits\n")
    f.write(f"- Testes realizados: {testes_totais}\n")
    f.write(f"- Erros não detectados: {len(erros_nao_detectados)}\n\n")
    
    f.write("EXEMPLOS DE ERROS NÃO DETECTADOS:\n")
    f.write("-" * 60 + "\n\n")
    
    for i, erro in enumerate(erros_nao_detectados[:5], 1):  # Mostrar apenas 5 exemplos
        f.write(f"Exemplo {i}:\n")
        f.write(f"  Posição: {erro['posicao']}\n")
        f.write(f"  Tamanho do burst: {erro['tamanho']} bits\n")
        f.write(f"  Bits originais:   {erro['original']}\n")
        f.write(f"  Bits corrompidos: {erro['corrompido']}\n")
        f.write(f"  Padrão de erro:   {erro['padrao']}\n\n")
    
    f.write("\nANÁLISE:\n")
    f.write("-" * 60 + "\n")
    f.write("1. Como esperado, erros com burst > 16 bits (grau do polinômio) podem\n")
    f.write("   escapar da detecção.\n\n")
    
    f.write("2. A probabilidade de não detecção para bursts > r é aproximadamente 2^(-r),\n")
    f.write("   ou seja, cerca de 1 em 65.536 para CRC-16.\n\n")
    
    f.write("3. Os erros não detectados ocorrem quando o padrão de erro é divisível\n")
    f.write("   pelo polinômio gerador, resultando em resto zero.\n\n")
    
    f.write("4. Isso demonstra a importância de escolher o polinômio gerador adequado\n")
    f.write("   e entender as limitações do CRC para o tipo de erro esperado.\n")

print("\nAnálise detalhada salva em: results/analise_erros_detalhada.txt")

# Demonstração específica do erro encontrado anteriormente
print("\n=== Demonstração do Erro Não Detectado ===")
print(f"Burst de 22 bits na posição 139:")

# Recriar o erro específico
quadro_erro, _ = inserir_erro_burst(quadro_original, 22, 139)
detectado = check_frame_manual(quadro_erro, GERADOR_BITS)

print(f"Original:   {quadro_original[139:161]}")
print(f"Corrompido: {quadro_erro[139:161]}")
print(f"Detectado: {'NÃO' if not detectado else 'SIM'}")