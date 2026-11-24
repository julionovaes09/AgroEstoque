import streamlit as st
import pandas as pd
import database

def render_dashboard():
    """Renderiza a página principal do Dashboard com indicadores e gráficos."""
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="color: #2E7D32; margin-bottom: 0.2rem;">📊 Painel de Controle do Estoque</h2>
            <p style="color: #666; font-size: 0.95rem;">Visão consolidada das operações, itens e alertas da propriedade rural</p>
        </div>
    """, unsafe_allow_html=True)

    dados = database.get_dashboard_data()
    metricas = dados["metricas"]
    estoque_baixo = dados["estoque_baixo"]
    categorias = dados["categorias"]
    ultimas_mov = dados["ultimas_movimentacoes"]

    # 1. Cards de Indicadores (Métricas Principais)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📦 Produtos Cadastrados",
            value=f"{metricas['total_produtos']} itens",
            help="Total de produtos ativos registrados no sistema"
        )

    with col2:
        st.metric(
            label="🚜 Volume Total em Estoque",
            value=f"{metricas['total_itens_estoque']:,.1f}",
            help="Soma total das quantidades de todos os insumos"
        )

    with col3:
        qtd_baixo = metricas["produtos_estoque_baixo"]
        st.metric(
            label="⚠️ Estoque Baixo / Crítico",
            value=f"{qtd_baixo} produtos",
            delta=f"-{qtd_baixo} atenção" if qtd_baixo > 0 else "Normal",
            delta_color="inverse" if qtd_baixo > 0 else "normal",
            help="Produtos cuja quantidade atual é igual ou inferior ao estoque mínimo"
        )

    with col4:
        st.metric(
            label="💰 Valor Estimado em Estoque",
            value=f"R$ {metricas['valor_total_estoque']:,.2f}",
            help="Valor financeiro total baseado no preço unitário dos itens em estoque"
        )

    st.divider()

    # 2. Alerta visual de Estoque Baixo se houver itens críticos
    if qtd_baixo > 0:
        st.warning(f"🚨 **Atenção:** Existem **{qtd_baixo} produto(s)** com quantidade igual ou abaixo do estoque mínimo de segurança!")
        with st.expander("🔍 Ver produtos que necessitam de reposição imediata", expanded=True):
            df_baixo = pd.DataFrame(estoque_baixo)
            df_baixo_display = df_baixo[[
                "codigo", "nome", "categoria", "quantidade", "estoque_minimo", "unidade_medida"
            ]].copy()
            df_baixo_display.columns = [
                "Código", "Produto", "Categoria", "Estoque Atual", "Estoque Mínimo", "Unidade"
            ]
            st.dataframe(
                df_baixo_display,
                use_container_width=True,
                hide_index=True
            )

    # 3. Gráficos Básicos do Sistema
    col_g1, col_g2 = st.columns([1, 1])

    with col_g1:
        st.markdown("##### 🌾 Insumos por Categoria")
        if categorias:
            df_cat = pd.DataFrame(categorias)
            # Gráfico de barras simples com Streamlit nativo
            df_cat_chart = df_cat.set_index("categoria")[["qtd_produtos"]]
            df_cat_chart.columns = ["Qtd de Produtos"]
            st.bar_chart(df_cat_chart, color="#2E7D32")
        else:
            st.info("Nenhum dado de categoria disponível no momento.")

    with col_g2:
        st.markdown("##### 🚨 Status do Estoque de Segurança")
        total_prods = metricas["total_produtos"]
        if total_prods > 0:
            normais = max(0, total_prods - qtd_baixo)
            df_status = pd.DataFrame({
                "Status": ["Estoque Normal", "Estoque Baixo"],
                "Quantidade": [normais, qtd_baixo]
            }).set_index("Status")
            st.bar_chart(df_status, color="#D32F2F" if qtd_baixo > 0 else "#2E7D32")
        else:
            st.info("Cadastre produtos para visualizar os gráficos de status.")

    st.divider()

    # 4. Tabela de Últimas Movimentações
    st.markdown("##### 🕒 Últimas 10 Movimentações Registradas")
    if ultimas_mov:
        df_mov = pd.DataFrame(ultimas_mov)
        
        # Formatar colunas para exibição amigável
        df_mov_display = pd.DataFrame({
            "Data/Hora": df_mov["data_movimentacao"],
            "Tipo": df_mov["tipo"].apply(lambda t: "🟢 ENTRADA" if t == "ENTRADA" else "🔴 SAÍDA"),
            "Código": df_mov["codigo"],
            "Produto": df_mov["produto_nome"],
            "Quantidade": df_mov.apply(lambda r: f"{r['quantidade']:.2f} {r['unidade_medida']}", axis=1),
            "Responsável": df_mov["usuario_nome"].fillna("Não informado"),
            "Observação": df_mov["observacao"].fillna("")
        })

        st.dataframe(
            df_mov_display,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhuma movimentação registrada até o momento.")
