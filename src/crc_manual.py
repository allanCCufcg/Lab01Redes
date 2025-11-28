"""
crc_manual.py
Implementação manual do CRC (divisão polinomial por XOR).
Exporta:
 - xor_bits(a,b)
 - calcular_crc_manual(dados_bits, gerador_bits)
 - check_frame_manual(frame_bits, gerador_bits) -> bool (True se válido)
 
Teste rápido se executado como script.
"""

def xor_bits(a: str, b: str) -> str:
    """XOR bit-a-bit entre strings binárias de mesmo comprimento."""
    return "".join('0' if a[i] == b[i] else '1' for i in range(len(a)))

def calcular_crc_manual(dados_bits: str, gerador_bits: str) -> str:
    """
    Calcula o CRC (resto) de dados_bits usando gerador_bits.
    Retorna string de r bits (r = len(gerador_bits)-1).
    """
    if not dados_bits:
        raise ValueError("dados_bits vazio")
    if not gerador_bits or gerador_bits[0] != '1':
        raise ValueError("gerador_bits inválido (deve começar com '1')")

    r = len(gerador_bits) - 1
    # mensagem com r zeros anexados (lista para mutação)
    mensagem = list(dados_bits + '0' * r)

    for i in range(len(dados_bits)):
        if mensagem[i] == '1':
            bloco = "".join(mensagem[i:i+len(gerador_bits)])
            resultado = xor_bits(bloco, gerador_bits)
            # atualiza a janela com o resultado do XOR:
            # o primeiro bit do resultado corresponde ao bit processado (vai virar 0)
            # substituímos os próximos bits da janela
            for j in range(1, len(resultado)):
                mensagem[i + j] = resultado[j]

    # resto são os últimos r bits
    if r == 0:
        return ""
    return "".join(mensagem[-r:])

def check_frame_manual(frame_bits: str, gerador_bits: str) -> bool:
    """
    Verifica um quadro (mensagem + crc) pela divisão por gerador.
    Retorna True se o resto for todo zeros (ou seja: válido).
    """
    r = len(gerador_bits) - 1
    # Ao dividir frame_bits diretamente, o resto deve ser 0...0 se válido.
    resto = calcular_crc_manual(frame_bits[:-r] if r>0 else frame_bits, gerador_bits) if False else None
    # Para verificar sem recomputar o CRC de um frame já com CRC:
    # Simplesmente execute a mesma rotina de divisão sobre frame_bits e cheque se resto == 0
    # Vamos implementar a divisão direta sobre frame_bits:
    mensagem = list(frame_bits)  # mutável
    n = len(frame_bits)
    g_len = len(gerador_bits)

    for i in range(n - (g_len - 1)):
        if mensagem[i] == '1':
            bloco = "".join(mensagem[i:i+g_len])
            resultado = xor_bits(bloco, gerador_bits)
            for j in range(g_len):
                mensagem[i + j] = resultado[j]

    # resto são os últimos r bits
    if r == 0:
        return True
    resto_final = "".join(mensagem[-r:])
    return set(resto_final) == {'0'}

# Teste rápido ao rodar diretamente
if __name__ == "__main__":
    # Exemplo do slide (validação)
    dados_teste = "1101011111"
    gerador_teste = "10011"
    crc = calcular_crc_manual(dados_teste, gerador_teste)
    print("Teste slide:")
    print("Dados:", dados_teste)
    print("Gerador:", gerador_teste)
    print("CRC calculado:", crc)  # deve bater com o slide
