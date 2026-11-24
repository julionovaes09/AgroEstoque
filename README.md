# 🌾 AgroEstoque - Sistema de Controle de Estoque para o Agronegócio

Sistema simples, moderno e intuitivo de controle de estoque voltado para propriedades rurais e agronegócio, desenvolvido em **Python**, **Streamlit** e **SQLite**.

---

# 1. Objetivo
Permitir que proprietários rurais, gerentes de fazenda e operadores controlem facilmente o estoque de insumos agrícolas (fertilizantes, defensivos, sementes, rações, combustíveis, peças e ferramentas), registrem movimentações com integridade garantida e monitorem níveis críticos de estoque para compras e reposição.

---

# 2. Tecnologias Utilizadas
- **Python 3.10+** (Linguagem base)
- **Streamlit** (Interface web moderna, reativa e profissional)
- **SQLite3** (Banco de dados relacional local, com persistência automática)
- **Pandas** (Estruturação e manipulação de dados para relatórios e exportações)
- **Hashlib / PBKDF2 HMAC SHA-256** (Segurança e armazenamento seguro de senhas com salt)

---

# 3. Funcionalidades do Sistema

### 🔐 1. Login e Gestão de Usuários
- Tela de login com validação de credenciais.
- Senhas armazenadas com criptografia **PBKDF2 HMAC SHA-256** e salt criptográfico individual.
- **Dois níveis de acesso:**
  - **👑 Administrador:** Acesso completo a todas as funções, relatórios, cadastros e gestão de novos usuários/senhas.
  - **👤 Funcionário:** Acesso operacional (visualização do dashboard, consulta ao estoque e lançamento de entradas/saídas).
- Opção para cadastro de novos usuários diretamente na tela de login ou pelo painel administrativo.

# 📊 2. Dashboard Rural
- **Indicadores Rápidos (KPIs):**
  - Quantidade total de produtos cadastrados.
  - Volume total de itens em estoque.
  - Quantidade de produtos com estoque baixo ou crítico.
  - Valor financeiro total estimado em estoque (R$).
- **Alertas de Reposição Urgente:** Destaque automático quando insumos atingem ou ficam abaixo do estoque mínimo.
- **Gráficos:**
  - Distribuição de insumos por categoria.
  - Gráfico de status do estoque (Normal vs. Baixo).
- **Últimas Movimentações:** Tabela com os 10 lançamentos mais recentes.

# 📦 3. Cadastro e Catálogo de Produtos
- Campos completos:
  - Código único / SKU (ex: `ADU-001`, `DEF-001`, `SEM-001`).
  - Nome do produto / insumo.
  - Categoria (*Fertilizantes e Adubos, Defensivos Agrícolas, Sementes e Mudas, Nutrição Animal, Medicamentos Veterinários, Combustíveis e Lubrificantes, Peças e Ferramentas, Outros Insumos*).
  - Unidade de medida (*kg, litros, sacas, unidades*).
  - Quantidade disponível inicial.
  - Estoque mínimo de segurança.
  - Preço unitário (R$).
- Validações de integridade (código único, campos obrigatórios, valores não-negativos).
- Filtros por nome, código, categoria e filtro rápido de estoque baixo.

# 🔄 4. Movimentação de Estoque
- Registro de **Entrada** (compras, recebimentos) e **Saída** (aplicação no talhão, consumo, abastecimento).
- Registro de data da operação e observações detalhadas (NF, talhão, máquina, etc.).
- **Atualização automática de saldo** em transação SQLite atômica.
- **Regra de Bloqueio Rígida:** O sistema **impede saídas maiores que o saldo disponível**, exibindo alerta explicativo e protegendo contra estoques negativos.
- Previsão de saldo em tempo real antes da confirmação do lançamento.

### 📑 5. Relatórios e Exportação
- **Posição Geral do Estoque:** Listagem completa com valor financeiro consolidado e status.
- **Produtos Abaixo do Estoque Mínimo:** Relatório específico para o setor de compras com cálculo de déficit e custo estimado de reposição.
- **Histórico Detalhado:** Filtro por período de datas, tipo (Entrada/Saída) e produto.
- **Exportação CSV:** Todos os relatórios podem ser baixados em formato CSV com um clique.

---

## 4. Estrutura do Projeto

```text
├── .streamlit/
│   └── config.toml          # Tema com cores do agronegócio (verde, branco, neutro)
├── views/
│   ├── __init__.py
│   ├── login.py             # Tela de login e primeiro acesso
│   ├── dashboard.py         # Dashboard com KPIs, gráficos e alertas
│   ├── produtos.py          # Catálogo, cadastro e edição de produtos
│   ├── movimentacoes.py     # Lançamento de entradas/saídas com validações
│   ├── relatorios.py        # Relatórios analíticos e exportação em CSV
│   └── usuarios.py          # Gestão de usuários (exclusivo Administrador)
├── app.py                   # Ponto de entrada do Streamlit e roteamento
├── auth.py                  # Funções de hashing PBKDF2, validação e usuários
├── database.py              # Camada de banco de dados SQLite e transações
├── requirements.txt         # Lista de dependências do Python
└── README.md                # Documentação e instruções de execução
```

---

## 5. Como Executar o Projeto Localmente

### Pré-requisitos
- Python 3.10 ou superior instalado no computador.

### Passo 1: Instalar as dependências
Abra o terminal na pasta do projeto e execute:

```bash
pip install -r requirements.txt
```

### Passo 2: Iniciar a aplicação
Execute o comando padrão do Streamlit:

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente no navegador no endereço: `http://localhost:8501`.

---

## 6. Usuários Padrão para Teste

Ao ser executado pela primeira vez, o sistema cria o banco SQLite local (`estoque_agro.db`) e popula automaticamente dois usuários de demonstração e insumos agrícolas de exemplo:

| Nível de Acesso | Usuário (Login) | Senha | Permissões |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin` | `admin123` | Acesso completo, relatórios, cadastros e gestão de usuários |
| **Funcionário** | `funcionario` | `func123` | Operação diária, lançamentos e consultas de estoque |

---

## 7. Banco de Dados e Persistência
- O banco de dados SQLite é salvo localmente no arquivo `estoque_agro.db`.
- **Todos os dados persistem** mesmo após fechar o navegador ou reiniciar a máquina.
