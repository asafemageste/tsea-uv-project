# ⚡ TSEA PRO - Sistema de Rastreabilidade Oculta UV

O **TSEA PRO** é um ecossistema de software desenvolvido para o controle estatístico e rastreabilidade de peças industriais através de marcações invisíveis reagentes à luz ultravioleta (UV). O sistema utiliza visão computacional e OCR para automatizar a leitura de dados e alimentar um banco de dados relacional.

---

## 🚀 Como Executar o Projeto Localmente

### 1. Pré-requisitos
Antes de iniciar, certifique-se de ter instalado em sua máquina:
* **Python 3.10 ou superior** (com a opção *Add to PATH* marcada)
* **Motor Tesseract OCR** instalado no caminho padrão do Windows:  
  `C:\Program Files\Tesseract-OCR\tesseract.exe`

### 2. Instalação das Dependências
Abra o terminal na pasta do projeto e execute:
```bash
pip install Flask opencv-python pytesseract
3. Inicialização do Servidor
Rode o arquivo principal para levantar o servidor local:

Bash
python app.py
Acesse no seu navegador: http://localhost:5000

📦 Guia de Uso (Módulo de Operação)
Controle de Acesso (Login):

E-mail: adminuv@gmail.com

Senha: lineallium123

Geração de Lotes: Na aba Produção Chapa, clique em Emitir Código para simular a criação de matérias-primas e suas respectivas peças filhas no banco de dados SQLite.

Gerenciamento: Na aba Gestão e Inventário, altere o status das peças para simular o avanço delas na linha de produção (Fase 1 a 4).

Visão Computacional: Na aba Leitor Óptico UV, ative a câmera para realizar a captura de frames e processamento de imagens via OpenCV e OCR.

Análise de Dados: Acompanhe os gráficos de eficiência e os indicadores de economia financeira gerados em tempo real na aba principal.

Desenvolvido para fins de apresentação de TCC.


---

### Passo 2: Subir o Manual para o GitHub
Agora que o arquivo foi criado no seu computador, abra o terminal do VS Code e rode estes 3 comandos rápidos para atualizar o GitHub:

1. **Preparar apenas o novo arquivo:**
   ```bash
   git add README.md