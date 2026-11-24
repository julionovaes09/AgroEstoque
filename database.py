import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from auth import hash_password

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "estoque_agro.db")

CATEGORIAS_PADRAO = [
    "Fertilizantes e Adubos",
    "Defensivos Agrícolas",
    "Sementes e Mudas",
    "Nutrição Animal",
    "Medicamentos Veterinários",
    "Combustíveis e Lubrificantes",
    "Peças e Ferramentas",
    "Outros Insumos"
]

UNIDADES_MEDIDA = ["kg", "litros", "sacas", "unidades"]

def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão ativa com o banco SQLite."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """
    Inicializa o banco de dados SQLite, cria as tabelas necessárias
    e popula com dados iniciais do agronegócio e usuários padrão se estiver vazio.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Tabela de Usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            perfil TEXT NOT NULL CHECK(perfil IN ('administrador', 'funcionario')),
            ativo INTEGER NOT NULL DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Tabela de Produtos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            unidade_medida TEXT NOT NULL,
            quantidade REAL NOT NULL DEFAULT 0.0 CHECK(quantidade >= 0),
            estoque_minimo REAL NOT NULL DEFAULT 0.0 CHECK(estoque_minimo >= 0),
            preco_unitario REAL NOT NULL DEFAULT 0.0 CHECK(preco_unitario >= 0),
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 3. Tabela de Movimentações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('ENTRADA', 'SAIDA')),
            quantidade REAL NOT NULL CHECK(quantidade > 0),
            saldo_anterior REAL NOT NULL,
            saldo_posterior REAL NOT NULL,
            data_movimentacao TEXT NOT NULL,
            observacao TEXT,
            usuario_id INTEGER,
            usuario_nome TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE RESTRICT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
        );
    """)

    conn.commit()

    # Inserção de dados iniciais padrão se as tabelas estiverem vazias
    _seed_initial_data(conn)
    conn.close()

def _seed_initial_data(conn: sqlite3.Connection):
    """Insere dados de exemplo do agronegócio e usuários caso o banco seja novo."""
    cursor = conn.cursor()

    # Verificar usuários
    cursor.execute("SELECT COUNT(*) AS total FROM usuarios")
    if cursor.fetchone()["total"] == 0:
        h_admin, s_admin = hash_password("admin123")
        h_func, s_func = hash_password("func123")

        cursor.executemany("""
            INSERT INTO usuarios (nome, username, password_hash, salt, perfil, ativo)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ("Administrador Geral", "admin", h_admin, s_admin, "administrador", 1),
            ("Operador da Fazenda", "funcionario", h_func, s_func, "funcionario", 1)
        ])
        conn.commit()

    # Verificar produtos
    cursor.execute("SELECT COUNT(*) AS total FROM produtos")
    if cursor.fetchone()["total"] == 0:
        produtos_iniciais = [
            ("ADU-001", "Fertilizante NPK 04-14-08", "Fertilizantes e Adubos", "sacas", 120.0, 50.0, 145.00),
            ("ADU-002", "Ureia Agrícola 46%", "Fertilizantes e Adubos", "sacas", 25.0, 60.0, 160.00),  # Estoque baixo proposital
            ("DEF-001", "Glifosato 480 SL", "Defensivos Agrícolas", "litros", 180.0, 40.0, 48.50),
            ("DEF-002", "Fungicida Azoxistrobina", "Defensivos Agrícolas", "litros", 15.0, 30.0, 195.00),  # Estoque baixo proposital
            ("SEM-001", "Semente de Milho Híbrido VT PRO", "Sementes e Mudas", "sacas", 50.0, 30.0, 380.00),
            ("SEM-002", "Semente de Soja Tratada", "Sementes e Mudas", "sacas", 200.0, 80.0, 210.00),
            ("ANI-001", "Ração Bovinos Confinamento", "Nutrição Animal", "sacas", 18.0, 40.0, 78.90),  # Estoque baixo proposital
            ("ANI-002", "Sal Mineral com Ureia 80", "Nutrição Animal", "sacas", 65.0, 25.0, 92.00),
            ("COMB-001", "Óleo Diesel S10", "Combustíveis e Lubrificantes", "litros", 2800.0, 600.0, 5.89),
            ("PEC-001", "Disco de Plantadeira 24 Furos", "Peças e Ferramentas", "unidades", 24.0, 10.0, 65.00),
        ]

        cursor.executemany("""
            INSERT INTO produtos (codigo, nome, categoria, unidade_medida, quantidade, estoque_minimo, preco_unitario)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, produtos_iniciais)
        conn.commit()

        # Inserir algumas movimentações iniciais para histórico realista
        hoje = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute("SELECT id, codigo, quantidade FROM produtos")
        prods = {r["codigo"]: r for r in cursor.fetchall()}

        movimentacoes_iniciais = [
            (prods["ADU-001"]["id"], "ENTRADA", 150.0, 0.0, 150.0, hoje, "Compra inicial para safra verão - NF 4501", 1, "Administrador Geral"),
            (prods["ADU-001"]["id"], "SAIDA", 30.0, 150.0, 120.0, hoje, "Aplicação no Talhão 02", 2, "Operador da Fazenda"),
            (prods["ADU-002"]["id"], "ENTRADA", 50.0, 0.0, 50.0, hoje, "Recebimento lote fornecedor", 1, "Administrador Geral"),
            (prods["ADU-002"]["id"], "SAIDA", 25.0, 50.0, 25.0, hoje, "Adubação de cobertura Talhão 01", 2, "Operador da Fazenda"),
            (prods["DEF-001"]["id"], "ENTRADA", 200.0, 0.0, 200.0, hoje, "Aquisição pré-plantio", 1, "Administrador Geral"),
            (prods["DEF-001"]["id"], "SAIDA", 20.0, 200.0, 180.0, hoje, "Dessecação de área 3", 2, "Operador da Fazenda"),
            (prods["COMB-001"]["id"], "ENTRADA", 3000.0, 0.0, 3000.0, hoje, "Abastecimento tanque central", 1, "Administrador Geral"),
            (prods["COMB-001"]["id"], "SAIDA", 200.0, 3000.0, 2800.0, hoje, "Abastecimento Tratores 1 e 2", 2, "Operador da Fazenda"),
        ]

        cursor.executemany("""
            INSERT INTO movimentacoes (produto_id, tipo, quantidade, saldo_anterior, saldo_posterior, data_movimentacao, observacao, usuario_id, usuario_nome)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, movimentacoes_iniciais)
        conn.commit()

# ==================== OPERAÇÕES DE PRODUTOS ====================

def get_produtos(termo_busca: Optional[str] = None, categoria: Optional[str] = None, apenas_estoque_baixo: bool = False) -> List[Dict[str, Any]]:
    """Consulta produtos com filtros opcionais de busca, categoria e alerta de estoque."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT id, codigo, nome, categoria, unidade_medida, quantidade, estoque_minimo, preco_unitario,
               (quantidade * preco_unitario) AS valor_total,
               CASE 
                   WHEN quantidade <= 0 THEN 'Zerado'
                   WHEN quantidade <= estoque_minimo THEN 'Estoque Baixo'
                   ELSE 'Normal'
               END AS status_estoque,
               criado_em, atualizado_em
        FROM produtos
        WHERE 1=1
    """
    params = []

    if termo_busca:
        query += " AND (LOWER(nome) LIKE ? OR LOWER(codigo) LIKE ?)"
        busca = f"%{termo_busca.strip().lower()}%"
        params.extend([busca, busca])

    if categoria and categoria != "Todas":
        query += " AND categoria = ?"
        params.append(categoria)

    if apenas_estoque_baixo:
        query += " AND quantidade <= estoque_minimo"

    query += " ORDER BY nome ASC"
    
    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_produto_by_id(produto_id: int) -> Optional[Dict[str, Any]]:
    """Retorna detalhes de um produto específico por ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_produto_by_codigo(codigo: str) -> Optional[Dict[str, Any]]:
    """Retorna um produto pelo código único."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE UPPER(codigo) = UPPER(?)", (codigo.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_produto(codigo: str, nome: str, categoria: str, unidade_medida: str,
                quantidade: float, estoque_minimo: float, preco_unitario: float,
                usuario_id: Optional[int] = None, usuario_nome: Optional[str] = None) -> Tuple[bool, str]:
    """Cadastra um novo produto e registra movimentação de entrada inicial se quantidade > 0."""
    codigo = codigo.strip().upper()
    nome = nome.strip()

    if not codigo:
        return False, "O código do produto é obrigatório."
    if not nome:
        return False, "O nome do produto é obrigatório."
    if quantidade < 0:
        return False, "A quantidade inicial não pode ser negativa."
    if estoque_minimo < 0:
        return False, "O estoque mínimo não pode ser negativo."
    if preco_unitario < 0:
        return False, "O preço unitário não pode ser negativo."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Verificar duplicidade de código
        cursor.execute("SELECT id FROM produtos WHERE UPPER(codigo) = ?", (codigo,))
        if cursor.fetchone():
            conn.close()
            return False, f"Já existe um produto com o código '{codigo}' cadastrado."

        cursor.execute("""
            INSERT INTO produtos (codigo, nome, categoria, unidade_medida, quantidade, estoque_minimo, preco_unitario)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (codigo, nome, categoria, unidade_medida, quantidade, estoque_minimo, preco_unitario))
        
        produto_id = cursor.lastrowid

        # Se quantidade inicial for maior que zero, registrar como movimentação de entrada inicial
        if quantidade > 0:
            hoje = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute("""
                INSERT INTO movimentacoes (produto_id, tipo, quantidade, saldo_anterior, saldo_posterior, data_movimentacao, observacao, usuario_id, usuario_nome)
                VALUES (?, 'ENTRADA', ?, 0.0, ?, ?, 'Estoque inicial de cadastro', ?, ?)
            """, (produto_id, quantidade, quantidade, hoje, usuario_id, usuario_nome or "Sistema"))

        conn.commit()
        conn.close()
        return True, f"Produto '{nome}' cadastrado com sucesso!"
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Erro ao cadastrar produto: {str(e)}"

def update_produto(produto_id: int, codigo: str, nome: str, categoria: str,
                   unidade_medida: str, estoque_minimo: float, preco_unitario: float) -> Tuple[bool, str]:
    """Atualiza dados cadastrais do produto (sem alterar saldo direto; saldo altera por movimentação)."""
    codigo = codigo.strip().upper()
    nome = nome.strip()

    if not codigo:
        return False, "O código do produto é obrigatório."
    if not nome:
        return False, "O nome do produto é obrigatório."
    if estoque_minimo < 0:
        return False, "O estoque mínimo não pode ser negativo."
    if preco_unitario < 0:
        return False, "O preço unitário não pode ser negativo."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Verificar se código pertence a outro produto
        cursor.execute("SELECT id FROM produtos WHERE UPPER(codigo) = ? AND id != ?", (codigo, produto_id))
        if cursor.fetchone():
            conn.close()
            return False, f"O código '{codigo}' já está em uso por outro produto."

        cursor.execute("""
            UPDATE produtos
            SET codigo = ?, nome = ?, categoria = ?, unidade_medida = ?,
                estoque_minimo = ?, preco_unitario = ?, atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (codigo, nome, categoria, unidade_medida, estoque_minimo, preco_unitario, produto_id))
        
        conn.commit()
        conn.close()
        return True, "Produto atualizado com sucesso!"
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Erro ao atualizar produto: {str(e)}"

# ==================== OPERAÇÕES DE MOVIMENTAÇÃO ====================

def registrar_movimentacao(produto_id: int, tipo: str, quantidade: float,
                           data_mov: str, observacao: str,
                           usuario_id: Optional[int], usuario_nome: Optional[str]) -> Tuple[bool, str]:
    """
    Registra uma movimentação de estoque (ENTRADA ou SAIDA) de forma atômica e segura.
    Atualiza o saldo na tabela 'produtos' e impede saídas maiores que o saldo disponível.
    """
    if quantidade <= 0:
        return False, "A quantidade movimentada deve ser maior que zero."
    
    tipo = tipo.upper()
    if tipo not in ('ENTRADA', 'SAIDA'):
        return False, "Tipo de movimentação inválido. Deve ser ENTRADA ou SAIDA."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Bloqueio / Consulta do produto atual
        cursor.execute("SELECT id, nome, quantidade, unidade_medida FROM produtos WHERE id = ?", (produto_id,))
        produto = cursor.fetchone()
        
        if not produto:
            conn.close()
            return False, "Produto selecionado não foi encontrado."

        saldo_atual = float(produto["quantidade"])
        nome_prod = produto["nome"]
        und = produto["unidade_medida"]

        # Regra de negócio estrita: Bloquear saída maior que saldo
        if tipo == 'SAIDA':
            if quantidade > saldo_atual:
                conn.close()
                return False, (
                    f"Operação cancelada! Saída de {quantidade:.2f} {und} é maior que o "
                    f"saldo disponível ({saldo_atual:.2f} {und}) para o produto '{nome_prod}'."
                )
            novo_saldo = saldo_atual - quantidade
        else: # ENTRADA
            novo_saldo = saldo_atual + quantidade

        
        cursor.execute("""
            UPDATE produtos
            SET quantidade = ?, atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (novo_saldo, produto_id))

        # Registrar histórico da movimentação
        cursor.execute("""
            INSERT INTO movimentacoes (
                produto_id, tipo, quantidade, saldo_anterior, saldo_posterior,
                data_movimentacao, observacao, usuario_id, usuario_nome
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (produto_id, tipo, quantidade, saldo_atual, novo_saldo, data_mov, observacao.strip(), usuario_id, usuario_nome))

        conn.commit()
        conn.close()

        acao_str = "entrada" if tipo == 'ENTRADA' else "saída"
        return True, (
            f"Movimentação de {acao_str} registrada com sucesso para '{nome_prod}'!\n"
            f"Saldo anterior: {saldo_atual:.2f} {und} | Novo saldo: {novo_saldo:.2f} {und}."
        )
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Falha ao registrar movimentação: {str(e)}"

def get_movimentacoes(limite: Optional[int] = None, produto_id: Optional[int] = None,
                      tipo: Optional[str] = None, data_inicio: Optional[str] = None,
                      data_fim: Optional[str] = None) -> List[Dict[str, Any]]:
    """Consulta o histórico de movimentações com múltiplos filtros."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT m.id, m.produto_id, p.codigo AS produto_codigo, p.nome AS produto_nome,
               p.categoria AS produto_categoria, p.unidade_medida,
               m.tipo, m.quantidade, m.saldo_anterior, m.saldo_posterior,
               m.data_movimentacao, m.observacao, m.usuario_nome, m.criado_em
        FROM movimentacoes m
        JOIN produtos p ON p.id = m.produto_id
        WHERE 1=1
    """
    params = []

    if produto_id:
        query += " AND m.produto_id = ?"
        params.append(produto_id)

    if tipo and tipo != "TODOS":
        query += " AND m.tipo = ?"
        params.append(tipo.upper())

    if data_inicio:
        query += " AND substr(m.data_movimentacao, 1, 10) >= ?"
        params.append(data_inicio)

    if data_fim:
        query += " AND substr(m.data_movimentacao, 1, 10) <= ?"
        params.append(data_fim)

    query += " ORDER BY m.id DESC"

    if limite:
        query += f" LIMIT {int(limite)}"

    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

# ==================== DADOS PARA DASHBOARD E RELATÓRIOS ====================

def get_dashboard_data() -> Dict[str, Any]:
    """Coleta todos os indicadores consolidados para alimentar o Dashboard."""
    conn = get_connection()
    cursor = conn.cursor()

    # Métricas agregadas de produtos
    cursor.execute("""
        SELECT 
            COUNT(*) AS total_produtos,
            COALESCE(SUM(quantidade), 0.0) AS total_itens_estoque,
            COALESCE(SUM(quantidade * preco_unitario), 0.0) AS valor_total_estoque,
            COUNT(CASE WHEN quantidade <= estoque_minimo THEN 1 END) AS produtos_estoque_baixo
        FROM produtos
    """)
    metricas = dict(cursor.fetchone())

    # Produtos por categoria (para gráfico)
    cursor.execute("""
        SELECT categoria, COUNT(*) AS qtd_produtos, SUM(quantidade) AS total_quantidade
        FROM produtos
        GROUP BY categoria
        ORDER BY qtd_produtos DESC
    """)
    categorias = [dict(r) for r in cursor.fetchall()]

    # Produtos com estoque baixo / crítico
    cursor.execute("""
        SELECT id, codigo, nome, categoria, unidade_medida, quantidade, estoque_minimo, preco_unitario
        FROM produtos
        WHERE quantidade <= estoque_minimo
        ORDER BY (quantidade - estoque_minimo) ASC
    """)
    estoque_baixo = [dict(r) for r in cursor.fetchall()]

    # Últimas movimentações (10 mais recentes)
    cursor.execute("""
        SELECT m.id, p.codigo, p.nome AS produto_nome, p.unidade_medida,
               m.tipo, m.quantidade, m.data_movimentacao, m.observacao, m.usuario_nome
        FROM movimentacoes m
        JOIN produtos p ON p.id = m.produto_id
        ORDER BY m.id DESC
        LIMIT 10
    """)
    ultimas_mov = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "metricas": metricas,
        "categorias": categorias,
        "estoque_baixo": estoque_baixo,
        "ultimas_movimentacoes": ultimas_mov
    }
