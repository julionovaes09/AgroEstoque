# 🌾 AgroEstoque - Sistema de Controle de Estoque Rural

Aplicação completa para gestão e controle de insumos agropecuários desenvolvida em **Python**, **Streamlit**, **Pandas** e **SQLite3**.

---

## Nome do Projeto
**AgroEstoque – Sistema Inteligente de Gestão e Controle de Estoque Rural**

## Objetivo da Aplicação
O agronegócio exige controle rigoroso de insumos de alto valor e prazos de validade críticos, como adubos, defensivos, sementes e combustíveis. O **AgroEstoque** foi desenvolvido para substituir anotações manuais e planilhas descentralizadas, centralizando a gestão de estoque da fazenda.

O sistema garante rastreabilidade total de entradas e saídas, bloqueio automático contra saldos negativos, monitoramento de níveis críticos com avisos de compra e relatórios gerenciais em tempo real.

## Principais Funcionalidades
- **Autenticação Segura (RBAC):** Controle de acesso com perfis de Administrador e Funcionário.
- **Criptografia Forte:** Senhas armazenadas com algoritmo PBKDF2 HMAC SHA-256 e Salt individual.
- **Dashboard Rural:** Indicadores em tempo real (KPIs), valor financeiro total (R$) e gráficos por categoria.
- **Alertas de Reposição Urgente:** Sinalização visual quando o estoque atinge ou fica abaixo do nível mínimo.
- **Catálogo de Insumos:** Cadastro com código único (SKU), categorias agrícolas, unidades de medida e preços.
- **Movimentações com Trava de Saldo:** Registro de Entradas e Saídas com previsão de saldo e bloqueio de estoque negativo.
- **Relatórios e Exportação:** Posição geral do estoque, lista de reposição para compras e exportação para CSV.
- **Gestão de Usuários:** Painel administrativo para criação e controle de operadores.

## Tecnologias e Bibliotecas Utilizadas
- **Python 3.10+:** Linguagem principal do projeto.
- **Streamlit:** Framework para criação da interface web interativa e reativa.
- **SQLite3:** Banco de dados relacional local com persistência em disco (`estoque_agro.db`).
- **Pandas:** Estruturação de dados tabulares e geração de arquivos CSV.
- **Altair:** Visualização e geração de gráficos estatísticos no dashboard.
- **Hashlib & Secrets:** Módulos nativos para segurança criptográfica e senhas com Salt.

> **Obs. (Instalação de Bibliotecas Externas):** Instale todas as dependências executando no terminal: `pip install -r requirements.txt` (ou manualmente via `pip install streamlit pandas altair`).

## Instruções para Instalação e Execução

### 1. Clonar ou Baixar o Projeto
Abra o terminal na pasta do projeto `AgroEstoque`.

### 2. Criar e Ativar o Ambiente Virtual
- **Windows:**
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```
- 

### 3. Instalar Dependências e Executar
```bash
pip install -r requirements.txt
streamlit run app.py
```
A aplicação abrirá automaticamente no navegador em `http://localhost:8501`.

### 4. Credenciais de Teste
- **Administrador:** Usuário `admin` | Senha: `admin123` (acesso completo ao sistema).
- **Funcionário:** Usuário `funcionario` | Senha: `func123` (acesso operacional e movimentações).

## Novos Conhecimentos Adquiridos
- **Desenvolvimento Web com Streamlit:** Criação de interfaces reativas, componentização modular em views e gerenciamento de estado persistente com `st.session_state`.
- **Persistência Relacional com SQLite3:** Modelagem relacional, constraints de integridade, ativação de chaves estrangeiras (`PRAGMA foreign_keys = ON`) e transações atômicas seguras com `commit`/`rollback`.
- **Segurança da Informação e Criptografia:** Armazenamento seguro de senhas utilizando `PBKDF2 HMAC SHA-256`, 100.000 iterações, salt criptográfico e controle de acesso baseado em papéis (RBAC).
- **Engenharia e Análise de Dados com Pandas:** Filtragem dinâmica de registros, cálculo automatizado de déficit de insumos e exportação de relatórios em CSV.
- **Arquitetura de Software em Camadas:** Organização desacoplada do projeto em camada de banco (`database.py`), segurança (`auth.py`) e apresentação (`views/`).
- **Regras de Negócio no Agronegócio:** Aplicação prática de conceitos rurais como estoque de segurança, unidades agronômicas (sacas, litros, kg) e bloqueio contra inconsistência física de saldo.

---


