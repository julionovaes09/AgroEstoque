import os
import sqlite3
import database
import auth

def run_tests():
    print("=" * 60)
    print("INICIANDO SUITE DE TESTES DO AGROESTOQUE")
    print("=" * 60)

    # 1. Testar Inicialização do Banco
    print("\n[1] Testando Inicialização do Banco de Dados...")
    database.init_db()
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = [row["name"] for row in cursor.fetchall()]
    assert "usuarios" in tabelas, "Tabela usuarios ausente!"
    assert "produtos" in tabelas, "Tabela produtos ausente!"
    assert "movimentacoes" in tabelas, "Tabela movimentacoes ausente!"
    print("  -> Tabelas SQLite criadas com sucesso:", tabelas)

    # 2. Testar Autenticação e Hashing Seguro
    print("\n[2] Testando Autenticação e Hash de Senhas...")
    user_admin = auth.autenticar_usuario(conn, "admin", "admin123")
    assert user_admin is not None, "Falha ao autenticar admin!"
    assert user_admin["perfil"] == "administrador", "Perfil admin incorreto!"
    print(f"  -> Admin autenticado com sucesso: {user_admin['nome']} ({user_admin['perfil']})")

    user_func = auth.autenticar_usuario(conn, "funcionario", "func123")
    assert user_func is not None, "Falha ao autenticar funcionario!"
    assert user_func["perfil"] == "funcionario", "Perfil funcionario incorreto!"
    print(f"  -> Funcionário autenticado com sucesso: {user_func['nome']} ({user_func['perfil']})")

    # Testar senha incorreta
    user_inv = auth.autenticar_usuario(conn, "admin", "senha_errada")
    assert user_inv is None, "Autenticação deveria falhar com senha incorreta!"
    print("  -> Proteção de senha incorreta: OK")

    # 3. Testar Cadastro de Produtos e Validações
    print("\n[3] Testando Cadastro de Produtos...")
    codigo_teste = "TEST-999"
    # Remover se existir de teste anterior
    cursor.execute("DELETE FROM movimentacoes WHERE produto_id IN (SELECT id FROM produtos WHERE codigo = ?)", (codigo_teste,))
    cursor.execute("DELETE FROM produtos WHERE codigo = ?", (codigo_teste,))
    conn.commit()

    ok, msg = database.add_produto(
        codigo=codigo_teste,
        nome="Adubo Especial de Teste",
        categoria="Fertilizantes e Adubos",
        unidade_medida="sacas",
        quantidade=50.0,
        estoque_minimo=20.0,
        preco_unitario=120.0,
        usuario_id=user_admin["id"],
        usuario_nome=user_admin["nome"]
    )
    assert ok, f"Falha ao cadastrar produto: {msg}"
    print(f"  -> Produto cadastrado: {msg}")

    # Testar duplicidade de código
    ok_dup, msg_dup = database.add_produto(
        codigo=codigo_teste,
        nome="Outro Produto",
        categoria="Outros Insumos",
        unidade_medida="unidades",
        quantidade=10.0,
        estoque_minimo=5.0,
        preco_unitario=10.0
    )
    assert not ok_dup, "Deveria impedir código duplicado!"
    print(f"  -> Bloqueio de código duplicado: OK ({msg_dup})")

    # 4. Testar Movimentação de ENTRADA
    print("\n[4] Testando Movimentação de ENTRADA...")
    prod = database.get_produto_by_codigo(codigo_teste)
    saldo_inicial = prod["quantidade"]
    assert saldo_inicial == 50.0

    ok_ent, msg_ent = database.registrar_movimentacao(
        produto_id=prod["id"],
        tipo="ENTRADA",
        quantidade=30.0,
        data_mov="2026-11-24 10:00",
        observacao="Compra adicional teste",
        usuario_id=user_admin["id"],
        usuario_nome=user_admin["nome"]
    )
    assert ok_ent, f"Falha na entrada: {msg_ent}"
    prod_apos_entrada = database.get_produto_by_codigo(codigo_teste)
    assert prod_apos_entrada["quantidade"] == 80.0, f"Saldo incorreto: {prod_apos_entrada['quantidade']}"
    print(f"  -> Entrada realizada com sucesso! Novo saldo: {prod_apos_entrada['quantidade']} sacas")

    # 5. Testar Movimentação de SAÍDA VÁLIDA
    print("\n[5] Testando Movimentação de SAÍDA VÁLIDA...")
    ok_sai, msg_sai = database.registrar_movimentacao(
        produto_id=prod["id"],
        tipo="SAIDA",
        quantidade=25.0,
        data_mov="2026-11-24 10:30",
        observacao="Aplicação teste",
        usuario_id=user_func["id"],
        usuario_nome=user_func["nome"]
    )
    assert ok_sai, f"Falha na saída: {msg_sai}"
    prod_apos_saida = database.get_produto_by_codigo(codigo_teste)
    assert prod_apos_saida["quantidade"] == 55.0, f"Saldo incorreto: {prod_apos_saida['quantidade']}"
    print(f"  -> Saída realizada com sucesso! Novo saldo: {prod_apos_saida['quantidade']} sacas")

    # 6. Testar Regra Rígida: IMPEDIR SAÍDA MAIOR QUE O SALDO DISPONÍVEL
    print("\n[6] Testando Bloqueio de Saída Superior ao Saldo...")
    saldo_atual = prod_apos_saida["quantidade"] # 55.0
    saida_excessiva = 60.0
    ok_bloq, msg_bloq = database.registrar_movimentacao(
        produto_id=prod["id"],
        tipo="SAIDA",
        quantidade=saida_excessiva,
        data_mov="2026-11-24 11:00",
        observacao="Tentativa de saída excessiva",
        usuario_id=user_func["id"],
        usuario_nome=user_func["nome"]
    )
    assert not ok_bloq, "O sistema NÃO DEVERIA permitir saída maior que o estoque!"
    prod_intacto = database.get_produto_by_codigo(codigo_teste)
    assert prod_intacto["quantidade"] == 55.0, "O saldo foi alterado indevidamente!"
    print(f"  -> Bloqueio funcionou perfeitamente: '{msg_bloq}'")

    # 7. Testar Dashboard e Métricas
    print("\n[7] Testando Indicadores do Dashboard...")
    dash = database.get_dashboard_data()
    metricas = dash["metricas"]
    assert metricas["total_produtos"] >= 10
    assert metricas["total_itens_estoque"] > 0
    assert metricas["produtos_estoque_baixo"] >= 1
    assert len(dash["ultimas_movimentacoes"]) > 0
    print(f"  -> Métricas consolidadas: {metricas}")
    print(f"  -> Produtos estoque baixo identificados: {metricas['produtos_estoque_baixo']}")

    # 8. Testar Gestão de Usuários
    print("\n[8] Testando Gestão de Usuários...")
    novo_user = "operador_novo"
    cursor.execute("DELETE FROM usuarios WHERE username = ?", (novo_user,))
    conn.commit()

    ok_u, msg_u = auth.cadastrar_usuario(conn, "Operador Novo Teste", novo_user, "senha123", "funcionario")
    assert ok_u, f"Falha ao criar usuário: {msg_u}"
    u_criado = auth.autenticar_usuario(conn, novo_user, "senha123")
    assert u_criado is not None
    print(f"  -> Novo usuário criado e autenticado: {u_criado['username']}")

    # Testar alternar status
    ok_alt, msg_alt = auth.alternar_status_usuario(conn, u_criado["id"], user_admin["id"])
    assert ok_alt
    u_inativo = auth.autenticar_usuario(conn, novo_user, "senha123")
    assert u_inativo == {"erro": "usuario_inativo"}
    print("  -> Desativação de usuário testada com sucesso (bloqueado no login).")

    # Reativar
    auth.alternar_status_usuario(conn, u_criado["id"], user_admin["id"])

    # Limpar dados de teste
    cursor.execute("DELETE FROM movimentacoes WHERE produto_id = ?", (prod["id"],))
    cursor.execute("DELETE FROM produtos WHERE id = ?", (prod["id"],))
    cursor.execute("DELETE FROM usuarios WHERE username = ?", (novo_user,))
    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print("TODOS OS TESTES FORAM CONCLUÍDOS COM 100% DE SUCESSO!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
