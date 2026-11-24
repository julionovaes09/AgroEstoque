import streamlit as st
import database
import auth

def render_login():
    """Renderiza a tela de login e cadastro de usuários do AgroEstoque."""
    
    
    st.markdown("""
        <div style="text-align: center; padding: 1.5rem 0 2rem 0;">
            <h1 style="color: #2E7D32; margin-bottom: 0.2rem; font-size: 2.3rem;">
                🌾 AgroEstoque
            </h1>
            <p style="color: #555555; font-size: 1.1rem; margin-top: 0;">
                Sistema de Controle de Estoque para Propriedades Rurais
            </p>
        </div>
    """, unsafe_allow_html=True)

    
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        tab_login, tab_cadastro = st.tabs(["🔐 Entrar no Sistema", "📝 Criar Novo Usuário"])

        with tab_login:
            st.markdown("##### Informe suas credenciais de acesso")
            with st.form("form_login", clear_on_submit=False):
                username = st.text_input("Usuário", placeholder="Ex: admin ou seu usuário").strip()
                password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
                btn_login = st.form_submit_button("Acessar Sistema", use_container_width=True, type="primary")

                if btn_login:
                    if not username or not password:
                        st.warning("Por favor, preencha o usuário e a senha.")
                    else:
                        conn = database.get_connection()
                        usuario = auth.autenticar_usuario(conn, username, password)
                        conn.close()

                        if usuario and "erro" in usuario and usuario["erro"] == "usuario_inativo":
                            st.error("Este usuário está inativo. Contate o administrador do sistema.")
                        elif usuario:
                            st.session_state["autenticado"] = True
                            st.session_state["usuario"] = usuario
                            st.success(f"Bem-vindo(a), {usuario['nome']}!")
                            st.rerun()
                        else:
                            st.error("Usuário ou senha incorretos. Verifique suas credenciais.")

            with st.expander("ℹ️ Credenciais Padrão para Demonstração"):
                st.markdown("""
                O sistema já vem inicializado com dois perfis de teste:
                
                - **Administrador:**
                  - Usuário: `admin`
                  - Senha: `admin123`
                  - *Permissões:* Acesso total, relatórios, cadastros e gestão de usuários.
                
                - **Funcionário:**
                  - Usuário: `funcionario`
                  - Senha: `func123`
                  - *Permissões:* Operação diária, registro de entradas/saídas e consultas.
                """)

        with tab_cadastro:
            st.markdown("##### Cadastrar novo usuário")
            with st.form("form_novo_usuario", clear_on_submit=True):
                novo_nome = st.text_input("Nome Completo", placeholder="Ex: João da Silva").strip()
                novo_username = st.text_input("Nome de Usuário (login)", placeholder="Ex: joaosilva").strip()
                nova_senha = st.text_input("Senha", type="password", placeholder="Mínimo 4 caracteres")
                novo_perfil = st.selectbox(
                    "Nível de Acesso",
                    options=["funcionario", "administrador"],
                    format_func=lambda x: "👤 Funcionário (Operações e Consultas)" if x == "funcionario" else "👑 Administrador (Acesso Completo)"
                )
                btn_cadastrar = st.form_submit_button("Cadastrar Usuário", use_container_width=True)

                if btn_cadastrar:
                    if not novo_nome or not novo_username or not nova_senha:
                        st.warning("Preencha todos os campos obrigatórios.")
                    else:
                        conn = database.get_connection()
                        sucesso, msg = auth.cadastrar_usuario(conn, novo_nome, novo_username, nova_senha, novo_perfil)
                        conn.close()
                        if sucesso:
                            st.success(msg + " Você já pode fazer login na aba 'Entrar no Sistema'.")
                        else:
                            st.error(msg)
