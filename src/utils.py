"""
utils.py
Funções utilitárias:
 - text_to_bits(text)
 - bits_to_bytes(bits)    (assume len(bits) % 8 == 0)
 - bytes_to_bits(b)
 - inserir_erro_burst(bits, tamanho_erro, pos=None)
 - salvar_csv(path, lista_dicts)
"""

import csv
import random

def text_to_bits(text: str, encoding='utf-8') -> str:
    """Converte string em sequência de bits (8 bits por caractere)."""
    return "".join(format(b, '08b') for b in text.encode(encoding))

def bytes_to_bits(b: bytes) -> str:
    return "".join(format(byte, '08b') for byte in b)

def bits_to_bytes(bits: str) -> bytes:
    """Converte string bits (múltiplo de 8) em bytes."""
    if len(bits) % 8 != 0:
        raise ValueError("bits length must be a multiple of 8")
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

def inserir_erro_burst(bits: str, tamanho_erro: int, pos: int = None):
    """
    Insere um burst (inverte tamanho_erro bits) em posição pos (aleatória se None).
    Retorna (bits_corrompidos, pos).
    """
    if tamanho_erro <= 0 or tamanho_erro > len(bits):
        raise ValueError("tamanho_erro inválido")
    if pos is None:
        pos = random.randint(0, len(bits) - tamanho_erro)
    b = list(bits)
    for i in range(tamanho_erro):
        b[pos + i] = '1' if b[pos + i] == '0' else '0'
    return "".join(b), pos

def salvar_csv(path: str, lista_dicts):
    """Salva lista de dicionários em CSV (header das chaves do primeiro dict)."""
    if not lista_dicts:
        raise ValueError("lista_dicts vazia")
    keys = list(lista_dicts[0].keys())
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(lista_dicts)
