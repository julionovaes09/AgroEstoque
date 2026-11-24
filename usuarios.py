import streamlit as st
import pandas as pd
import database
import auth

def render_usuarios():
    """Renderiza a tela de gestão de usuários (exclusiva para perfil Administrador)."""
    usuario_atual = st.session_state.get("usuario", {})
    if usuario_atual.get("perfil") != "administrador":
        st.error("⛔ Acesso Restrito: Apenas administradores do sistema podem acessar o gerenciamento de usuários.")
        return

    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="color: #2E7D32; margin-bottom: 0.2rem;">👥 Gestão de Usuários e Acessos</h2>
            <p style="color: #666; font-size: 0.95rem;">Controle de operadores, administradores e permissões de segurança da propriedade</p>
        </div>
    """, unsafe_allow_html=True)

    tab_listar, tab_cadastrar, tab_acoes = st.tabs([
        "📋 Usuários Cadastrados",
        "➕ Cadastrar Novo Usuário",
        "⚙️ Ações e Senhas"
    ])

    conn = database.get_connection()

    # ==================== ABA 1: LISTA DE USUÁRIOS ====================
    with tab_listar:
        usuarios = auth.listar_usuarios(conn)
        if usuarios:
            df = pd.DataFrame(usuarios)
            df_display = pd.DataFrame({
                "ID": df["id"],
                "Nome Completo": df["nome"],
                "Login (Username)": df["username"],
                "Nível de Acesso": df["perfil"].apply(
                    lambda p: "👑 Administrador" if p == "administrador" else "👤 Funcionário"
                ),
                "Status": df["ativo"].apply(lambda a: "🟢 Ativo" if a == 1 else "🔴 Inativo"),
                "Data de Cadastro": df["criado_em"]
            })
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            st.caption(f"Total de **{len(usuarios)}** usuário(s) no sistema.")
        else:
            st.info("Nenhum usuário cadastrado.")

    # ==================== ABA 2: CADASTRAR NOVO USUÁRIO ====================
    with tab_cadastrar:
        st.markdown("##### Cadastrar Novo Operador ou Administrador")
        with st.form("form_cadastrar_usuario_admin", clear_on_submit=True):
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                nome = st.text_input("Nome Completo*", placeholder="Ex: Carlos Eduardo Silveira").strip()
                username = st.text_input("Nome de Usuário (Login)*", placeholder="Ex: carlossilveira").strip()
            with col_u2:
                senha = st.text_input("Senha Inicial*", type="password", placeholder="Mínimo 4 caracteres")
                perfil = st.selectbox(
                    "Nível de Acesso*",
                    options=["funcionario", "administrador"],
                    format_func=lambda x: "👤 Funcionário (Lançamentos e Consultas)" if x == "funcionario" else "👑 Administrador (Acesso Total)"
                )

            btn_salvar = st.form_submit_button("Cadastrar Usuário", type="primary")

            if btn_salvar:
                if not nome or not username or not senha:
                    st.warning("Preencha todos os campos obrigatórios.")
                else:
                    sucesso, msg = auth.cadastrar_usuario(conn, nome, username, senha, perfil)
                    if sucesso:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # ==================== ABA 3: AÇÕES E SENHAS ====================
    with tab_acoes:
        st.markdown("##### Gerenciamento de Status e Redefinição de Senha")
        todos = auth.listar_usuarios(conn)
        opcoes = {f"{u['nome']} (@{u['username']}) - {u['perfil']}": u for u in todos}

        if opcoes:
            escolha = st.selectbox("Selecione o usuário:", options=list(opcoes.keys()))
            u_sel = opcoes[escolha]

            col_a1, col_a2 = st.columns(2)

            with col_a1:
                st.markdown("###### Status da Conta")
                status_atual = "🟢 Ativo" if u_sel["ativo"] == 1 else "🔴 Inativo"
                st.write(f"Status atual: **{status_atual}**")
                
                acao_label = "Desativar Acesso" if u_sel["ativo"] == 1 else "Ativar Acesso"
                if st.button(f"Alterar para: {acao_label}"):
                    sucesso, msg = auth.alternar_status_usuario(conn, u_sel["id"], usuario_atual.get("id"))
                    if sucesso:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            with col_a2:
                st.markdown("###### Redefinir Senha do Usuário")
                with st.form("form_reset_senha"):
                    nova_senha = st.text_input("Nova Senha", type="password", placeholder="Mínimo 4 caracteres")
                    btn_reset = st.form_submit_button("Atualizar Senha")

                    if btn_reset:
                        sucesso, msg = auth.redefinir_senha_usuario(conn, u_sel["id"], nova_senha)
                        if sucesso:
                            st.success(msg)
                        else:
                            st.error(msg)

    conn.close()
