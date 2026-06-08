import cv2
import pytesseract
import sqlite3
import os

# --- LOGICA DE INTEGRAÇÃO AUTOMÁTICA DO TESSERACT ---
caminhos_possiveis = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    os.path.expanduser(r'~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe')
]

tesseract_encontrado = False
for caminho in caminhos_possiveis:
    if os.path.exists(caminho):
        pytesseract.pytesseract.tesseract_cmd = caminho
        tesseract_encontrado = True
        break

if not tesseract_encontrado:
    print("ATENÇÃO: O Tesseract não foi encontrado nas pastas padrões.")
    print("Certifique-se de que instalou o instalador do GitHub até o final!")
# -----------------------------------------------------

def buscar_no_banco(codigo):
    """Busca o código limpo e decide se é Chapa ou Peça."""
    codigo = codigo.strip().upper()
    conn = sqlite3.connect('controle_producao.db')
    cursor = conn.cursor()
    
    print(f"\nBuscando por: {codigo}")
    
    if codigo.startswith('C'):
        cursor.execute("SELECT * FROM chapas WHERE codigo_chapa = ?", (codigo,))
        res = cursor.fetchone()
        if res:
            print(f"CHAPA LOCALIZADA!\n • Status: {res[2]}\n • Cadastrada em: {res[1]}")
        else:
            print("Chapa não encontrada no banco.")
            
    elif codigo.startswith('P'):
        cursor.execute('''
            SELECT p.codigo_peca, p.data_corte, p.status, p.codigo_chapa_mae 
            FROM pecas p WHERE p.codigo_peca = ?
        ''', (codigo,))
        res = cursor.fetchone()
        if res:
            print(f"PEÇA LOCALIZADA!\n • Status: {res[2]}\n • Cortada em: {res[1]}\n • Chapa Mãe: {res[3]}")
        else:
            print("Peça não encontrada no banco.")
    else:
        print("Código fora do padrão de fábrica (Não começa com C ou P).")
        
    conn.close()

def ler_imagem_da_peca(nome_arquivo):
    """Processa a imagem e manda o texto pro banco."""
    if not os.path.exists(nome_arquivo):
        print(f"Erro: O arquivo '{nome_arquivo}' não existe na pasta.")
        return

    img = cv2.imread(nome_arquivo)
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, tratada = cv2.threshold(cinza, 127, 255, cv2.THRESH_BINARY)
    
    # Lê a imagem buscando letras, números e hífens
    texto = pytesseract.image_to_string(tratada, config='--psm 6').strip()
    
    if texto:
        buscar_no_banco(texto)
    else:
        print("A imagem foi carregada, mas a IA não conseguiu ler nenhum texto.")

# Teste direto digitando o texto (tava sem camera na hr)
if __name__ == "__main__":
    # Quando quiser testar digitando, mude o código abaixo para um gerado pelo gerador.py:
    # buscar_no_banco("C01-1234567")
    buscar_no_banco("P01C01-1234567")