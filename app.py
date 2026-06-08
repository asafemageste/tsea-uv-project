from flask import Flask, render_template, jsonify, request
import sqlite3
import random
import datetime
import os
import cv2
import pytesseract
import base64

app = Flask(__name__)

# --- CONFIGURAÇÃO DO TESSERACT ---
caminhos_possiveis = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    os.path.expanduser(r'~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe')
]
for caminho in caminhos_possiveis:
    if os.path.exists(caminho):
        pytesseract.pytesseract.tesseract_cmd = caminho
        break

DB_NAME = 'controle_producao.db'

def iniciar_banco():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (email TEXT PRIMARY KEY, senha TEXT, role TEXT)")
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('adminuv@gmail.com', 'lineallium123', 'admin')")
    cursor.execute("CREATE TABLE IF NOT EXISTS chapas (codigo_chapa TEXT PRIMARY KEY, data_cadastro TEXT, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS pecas (codigo_peca TEXT PRIMARY KEY, codigo_chapa_mae TEXT, data_corte TEXT, status TEXT, FOREIGN KEY (codigo_chapa_mae) REFERENCES chapas(codigo_chapa))")
    conn.commit()
    conn.close()

iniciar_banco()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM usuarios WHERE email = ? AND senha = ?", (data.get('email'), data.get('senha')))
    user = cursor.fetchone()
    conn.close()
    if user: return jsonify({"sucesso": True, "role": user[0]})
    return jsonify({"sucesso": False, "mensagem": "Acesso Negado."})

@app.route('/gerar_chapa', methods=['POST'])
def rota_gerar_chapa():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM chapas")
    proximo_id = cursor.fetchone()[0] + 1
    codigo_chapa = f"C{proximo_id:02d}-{''.join(str(random.randint(1, 9)) for _ in range(7))}"
    data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("INSERT INTO chapas VALUES (?, ?, ?)", (codigo_chapa, data_atual, 'CORTADA'))
    cursor.execute("INSERT INTO pecas VALUES (?, ?, ?, ?)", (f"P01{codigo_chapa}", codigo_chapa, data_atual, 'CORTADA'))
    cursor.execute("INSERT INTO pecas VALUES (?, ?, ?, ?)", (f"P02{codigo_chapa}", codigo_chapa, data_atual, 'CORTADA'))
    conn.commit()
    conn.close()
    return jsonify({"sucesso": True, "codigo": codigo_chapa})

@app.route('/scanner', methods=['POST'])
def rota_scanner():
    data = request.get_json()
    caminho_temp = "temp_scan.png"
    with open(caminho_temp, "wb") as fh: fh.write(base64.b64decode(data['imagem'].split(',')[1]))
    
    img = cv2.imread(caminho_temp)
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    tratada = cv2.adaptiveThreshold(cinza, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    texto_lido = pytesseract.image_to_string(tratada, config=r'--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-').strip().upper()
    if os.path.exists(caminho_temp): os.remove(caminho_temp)
        
    if not texto_lido: return jsonify({"sucesso": False, "mensagem": "Aproxime a câmera."})
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    resposta = {"sucesso": True, "codigo_detectado": texto_lido, "dados": {}}
    if texto_lido.startswith('C'):
        cursor.execute("SELECT * FROM chapas WHERE codigo_chapa = ?", (texto_lido,))
        res = cursor.fetchone()
        if res: resposta.update({"tipo": "CHAPA MÃE", "dados": {"status": res[2]}})
        else: resposta.update({"sucesso": False, "mensagem": "Não encontrada."})
    elif texto_lido.startswith('P'):
        cursor.execute("SELECT * FROM pecas WHERE codigo_peca = ?", (texto_lido,))
        res = cursor.fetchone()
        if res: resposta.update({"tipo": "PEÇA CORTADA", "dados": {"status": res[3], "chapa": res[1]}})
        else: resposta.update({"sucesso": False, "mensagem": "Não encontrada."})
    else: resposta.update({"sucesso": False, "mensagem": "Padrão inválido."})
    conn.close()
    return jsonify(resposta)

@app.route('/inventario', methods=['GET'])
def inventario():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT codigo_chapa, status FROM chapas")
    chapas = cursor.fetchall()
    dados = []
    for c in chapas:
        cursor.execute("SELECT codigo_peca, status FROM pecas WHERE codigo_chapa_mae = ?", (c[0],))
        dados.append({"chapa": c[0], "status": c[1], "pecas": [{"codigo": p[0], "status": p[1]} for p in cursor.fetchall()]})
    conn.close()
    return jsonify({"sucesso": True, "inventario": dados})

@app.route('/dashboard_dados', methods=['GET'])
def dashboard_dados():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM pecas")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pecas WHERE status = 'FINALIZADA'")
    finalizadas = cursor.fetchone()[0]
    cursor.execute("SELECT status, COUNT(*) FROM pecas GROUP BY status")
    grafico = dict(cursor.fetchall())
    conn.close()
    
    # Simulação de lucro: R$ 350 salvos por cada peça não perdida no refugo
    lucro = finalizadas * 350.00 
    porcentagem = (finalizadas / total * 100) if total > 0 else 0
    
    return jsonify({"total": total, "finalizadas": finalizadas, "porcentagem": round(porcentagem, 1), "lucro": lucro, "grafico": grafico})

@app.route('/atualizar_status', methods=['POST'])
def atualizar_status():
    data = request.get_json()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE pecas SET status = ? WHERE codigo_peca = ?", (data.get('status'), data.get('codigo')))
    conn.commit()
    conn.close()
    return jsonify({"sucesso": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)