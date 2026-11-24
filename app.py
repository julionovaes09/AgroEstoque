import streamlit as st
import database
from views.login import render_login
from views.dashboard import render_dashboard
from views.produtos import render_produtos
from views.movimentacoes import render_movimentacoes
from views.relatorios import render_relatorios
from views.usuarios import render_usuarios


st.set_page_config(
    page_title="AgroEstoque - Controle de Estoque Rural",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)


database.init_db()


if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

def main():
    
    if not st.session_state["autenticado"] or not st.session_state["usuario"]:
        render_login()
        return

    usuario = st.session_state["usuario"]
    e_admin = usuario.get("perfil") == "administrador"

    with st.sidebar:
        
        st.markdown("""
            <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
                <h2 style="color: #2E7D32; margin: 0; font-size: 1.8rem;">
                    🌾 AgroEstoque
                </h2>
                <div style="color: #666; font-size: 0.85rem; letter-spacing: 0.5px;">
                    GESTÃO DE ESTOQUE RURAL
                </div>
            </div>
        """, unsafe_allow_html=True)

        
        perfil_label = "👑 Administrador" if e_admin else "👤 Funcionário"
        perfil_cor = "#2E7D32" if e_admin else "#1565C0"
        
        st.markdown(f"""
            <div style="background-color: #F4F7F4; border: 1px solid #E0E5E0; border-radius: 8px; padding: 10px; margin-bottom: 20px;">
                <div style="font-size: 0.8rem; color: #777;">OPERADOR LOGADO</div>
                <div style="font-weight: bold; color: #1B2A1E; font-size: 1.05rem;">{usuario['nome']}</div>
                <div style="display: inline-block; background-color: {perfil_cor}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-top: 4px; font-weight: 500;">
                    {perfil_label}
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📌 Navegação")

       
        menu_opcoes = [
            "📊 Dashboard",
            "📦 Cadastro de Produtos",
            "🔄 Movimentação de Estoque",
            "📑 Relatórios"
        ]

        if e_admin:
            menu_opcoes.append("👥 Gestão de Usuários")

        pagina_selecionada = st.radio(
            "Selecione o módulo:",
            options=menu_opcoes,
            label_visibility="collapsed"
        )

        st.divider()

        
        if st.button("🚪 Sair do Sistema", use_container_width=True):
            st.session_state["autenticado"] = False
            st.session_state["usuario"] = None
            st.rerun()

        st.markdown("""
            <div style="text-align: center; margin-top: 2rem; font-size: 0.75rem; color: #888;">
                🌱 AgroEstoque v1.0<br>
                💾 Banco SQLite Persistente
            </div>
        """, unsafe_allow_html=True)

    
    if pagina_selecionada == "📊 Dashboard":
        render_dashboard()
    elif pagina_selecionada == "📦 Cadastro de Produtos":
        render_produtos()
    elif pagina_selecionada == "🔄 Movimentação de Estoque":
        render_movimentacoes()
    elif pagina_selecionada == "📑 Relatórios":
        render_relatorios()
    elif pagina_selecionada == "👥 Gestão de Usuários" and e_admin:
        render_usuarios()

if __name__ == "__main__":
    main()
