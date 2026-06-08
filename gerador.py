import sqlite3
import random
import datetime
import os

def iniciar_sistema():
    """Cria o arquivo do banco de dados e as tabelas automaticamente."""
    conn = sqlite3.connect('controle_producao.db')
    cursor = conn.cursor()
    
    # Cria tabela de Chapas Mãe (Modelo C)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chapas (
            codigo_chapa TEXT PRIMARY KEY,
            data_cadastro TEXT,
            status TEXT
        )
    ''')
    
    # Cria tabela de Peças Cortadas (Modelo PC)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pecas (
            codigo_peca TEXT PRIMARY KEY,
            codigo_chapa_mae TEXT,
            data_corte TEXT,
            status TEXT,
            FOREIGN KEY (codigo_chapa_mae) REFERENCES chapas(codigo_chapa)
        )
    ''')
    conn.commit()
    return conn, cursor

def gerar_7_numeros():
    """Gera 7 números aleatórios de 1 a 9."""
    return "".join(str(random.randint(1, 9)) for _ in range(7))

def cadastrar_chapa():
    """Gera um código sequencial C01-1234567 e salva no banco."""
    conn, cursor = iniciar_sistema()
    
    cursor.execute("SELECT COUNT(*) FROM chapas")
    proximo_id = cursor.fetchone()[0] + 1
    
    codigo_chapa = f"C{proximo_id:02d}-{gerar_7_numeros()}"
    data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("INSERT INTO chapas VALUES (?, ?, ?)", (codigo_chapa, data_atual, 'INTEIRA'))
    conn.commit()
    conn.close()
    print(f"CHAPA MÃE GERADA: {codigo_chapa}")
    return codigo_chapa

def cortar_peca(codigo_chapa_mae):
    """Gera uma peça vinculada à chapa mãe (Ex: P01C01-1234567)."""
    conn, cursor = iniciar_sistema()
    
    # Verifica se a chapa mãe existe
    cursor.execute("SELECT codigo_chapa FROM chapas WHERE codigo_chapa = ?", (codigo_chapa_mae,))
    if not cursor.fetchone():
        print(f"Erro: A chapa {codigo_chapa_mae} não existe no banco!")
        conn.close()
        return
    
    # Conta quantas peças já saíram dessa chapa para definir o P01, P02...
    cursor.execute("SELECT COUNT(*) FROM pecas WHERE codigo_chapa_mae = ?", (codigo_chapa_mae,))
    proximo_p = cursor.fetchone()[0] + 1
    
    codigo_peca = f"P{proximo_p:02d}{codigo_chapa_mae}"
    data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("INSERT INTO pecas VALUES (?, ?, ?, ?)", (codigo_peca, codigo_chapa_mae, data_atual, 'CORTADA'))
    cursor.execute("UPDATE chapas SET status = 'EM CORTE' WHERE codigo_chapa = ?", (codigo_chapa_mae,))
    
    conn.commit()
    conn.close()
    print(f"PEÇA CORTADA GERADA: {codigo_peca}")
    return codigo_peca

# Executa um teste automático ao rodar este arquivo
if __name__ == "__main__":
    print("--- GERANDO DADOS DE TESTE ---")
    nova_chapa = cadastrar_chapa()
    cortar_peca(nova_chapa)
    cortar_peca(nova_chapa)