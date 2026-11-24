import streamlit as st
import pandas as pd
from datetime import date, datetime
import database

def render_relatorios():
    """Renderiza a central de relatórios operacionais e gerenciais."""
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="color: #2E7D32; margin-bottom: 0.2rem;">📑 Relatórios de Estoque</h2>
            <p style="color: #666; font-size: 0.95rem;">Emissão de relatórios analíticos, controle de reposição e histórico de movimentações</p>
        </div>
    """, unsafe_allow_html=True)

    tipo_relatorio = st.radio(
        "Selecione o tipo de relatório desejado:",
        options=[
            "📦 Posição do Estoque Atual",
            "🚨 Produtos Abaixo do Estoque Mínimo (Compras)",
            "🔄 Histórico Detalhado de Entradas e Saídas"
        ],
        horizontal=True
    )

    st.divider()

     
    if "Posição do Estoque Atual" in tipo_relatorio:
        st.markdown("### 📦 Posição Consolidada do Estoque Atual")

        col1, col2 = st.columns([2, 1])
        with col1:
            termo = st.text_input("Filtrar por nome ou código", placeholder="Digite para filtrar...").strip()
        with col2:
            opcoes_cat = ["Todas"] + database.CATEGORIAS_PADRAO
            cat_filtro = st.selectbox("Filtrar por categoria", options=opcoes_cat)

        produtos = database.get_produtos(termo_busca=termo if termo else None, categoria=cat_filtro)

        if produtos:
            df = pd.DataFrame(produtos)

            # Resumo numérico no topo
            total_itens = df["quantidade"].sum()
            total_valor = df["valor_total"].sum()
            criticos = len(df[df["quantidade"] <= df["estoque_minimo"]])

            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Total de Insumos Registrados", f"{len(df)} itens")
            col_m2.metric("Volume Físico Total", f"{total_itens:,.2f}")
            col_m3.metric("Valor Financeiro em Estoque", f"R$ {total_valor:,.2f}")

            df_export = pd.DataFrame({
                "Código": df["codigo"],
                "Produto": df["nome"],
                "Categoria": df["categoria"],
                "Unidade": df["unidade_medida"],
                "Estoque Atual": df["quantidade"],
                "Estoque Mínimo": df["estoque_minimo"],
                "Preço Unitário (R$)": df["preco_unitario"],
                "Valor Total (R$)": df["valor_total"],
                "Status": df["status_estoque"]
            })

            # Tabela formatada para visualização
            df_display = df_export.copy()
            df_display["Estoque Atual"] = df_display["Estoque Atual"].apply(lambda x: f"{x:,.2f}")
            df_display["Estoque Mínimo"] = df_display["Estoque Mínimo"].apply(lambda x: f"{x:,.2f}")
            df_display["Preço Unitário (R$)"] = df_display["Preço Unitário (R$)"].apply(lambda x: f"R$ {x:,.2f}")
            df_display["Valor Total (R$)"] = df_display["Valor Total (R$)"].apply(lambda x: f"R$ {x:,.2f}")

            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # Botão de Exportação CSV
            csv_data = df_export.to_csv(index=False, sep=";", encoding="utf-8-sig")
            st.download_button(
                label="📥 Baixar Relatório de Estoque Atual (CSV)",
                data=csv_data,
                file_name=f"relatorio_estoque_atual_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.info("Nenhum produto cadastrado com os critérios selecionados.")

    # ==================== RELATÓRIO 2: PRODUTOS ABAIXO DO MÍNIMO ====================
    elif "Abaixo do Estoque Mínimo" in tipo_relatorio:
        st.markdown("### 🚨 Produtos Abaixo do Estoque Mínimo (Necessidade de Compra)")
        st.caption("Itens com saldo físico igual ou inferior ao estoque mínimo recomendado para operação.")

        produtos_criticos = database.get_produtos(apenas_estoque_baixo=True)

        if produtos_criticos:
            df_crit = pd.DataFrame(produtos_criticos)
            
            # Calcular déficit e custo estimado de reposição
            df_crit["deficit"] = df_crit["estoque_minimo"] - df_crit["quantidade"]
            df_crit["custo_reposicao"] = df_crit["deficit"] * df_crit["preco_unitario"]

            total_reposicao = df_crit["custo_reposicao"].sum()

            st.error(f"⚠️ Existem **{len(df_crit)}** produto(s) necessitando de reposição urgente! Custo estimado de reposição: **R$ {total_reposicao:,.2f}**")

            df_crit_export = pd.DataFrame({
                "Código": df_crit["codigo"],
                "Produto": df_crit["nome"],
                "Categoria": df_crit["categoria"],
                "Unidade": df_crit["unidade_medida"],
                "Estoque Atual": df_crit["quantidade"],
                "Estoque Mínimo": df_crit["estoque_minimo"],
                "Déficit (Reposição)": df_crit["deficit"],
                "Preço Unitário (R$)": df_crit["preco_unitario"],
                "Custo Reposição Estimado (R$)": df_crit["custo_reposicao"]
            })

            df_crit_display = df_crit_export.copy()
            df_crit_display["Estoque Atual"] = df_crit_display["Estoque Atual"].apply(lambda x: f"{x:,.2f}")
            df_crit_display["Estoque Mínimo"] = df_crit_display["Estoque Mínimo"].apply(lambda x: f"{x:,.2f}")
            df_crit_display["Déficit (Reposição)"] = df_crit_display["Déficit (Reposição)"].apply(lambda x: f"{x:,.2f}")
            df_crit_display["Preço Unitário (R$)"] = df_crit_display["Preço Unitário (R$)"].apply(lambda x: f"R$ {x:,.2f}")
            df_crit_display["Custo Reposição Estimado (R$)"] = df_crit_display["Custo Reposição Estimado (R$)"].apply(lambda x: f"R$ {x:,.2f}")

            st.dataframe(df_crit_display, use_container_width=True, hide_index=True)

            csv_data = df_crit_export.to_csv(index=False, sep=";", encoding="utf-8-sig")
            st.download_button(
                label="📥 Baixar Lista de Compras / Reposição (CSV)",
                data=csv_data,
                file_name=f"relatorio_reposicao_estoque_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.success("🎉 Excelente! Todos os produtos estão com níveis de estoque acima do mínimo de segurança.")

    # ==================== RELATÓRIO 3: HISTÓRICO DE ENTRADAS E SAÍDAS ====================
    elif "Histórico Detalhado" in tipo_relatorio:
        st.markdown("### 🔄 Histórico Detalhado de Movimentações")

        # Filtros avançados
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)

        with col_f1:
            tipo_filtro = st.selectbox("Tipo de Movimentação", options=["TODOS", "ENTRADA", "SAIDA"], format_func=lambda x: "Todas as Operações" if x == "TODOS" else ("🟢 Somente Entradas" if x == "ENTRADA" else "🔴 Somente Saídas"))
        
        with col_f2:
            todos_produtos = database.get_produtos()
            opcoes_prod = {"Todos": None}
            for p in todos_produtos:
                opcoes_prod[f"[{p['codigo']}] {p['nome']}"] = p["id"]
            prod_escolhido = st.selectbox("Produto", options=list(opcoes_prod.keys()))
            prod_id_filtro = opcoes_prod[prod_escolhido]

        with col_f3:
            data_ini = st.date_input("Data Inicial", value=date(2025, 1, 1))
        
        with col_f4:
            data_fim = st.date_input("Data Final", value=date.today())

        movs = database.get_movimentacoes(
            produto_id=prod_id_filtro,
            tipo=tipo_filtro,
            data_inicio=data_ini.strftime("%Y-%m-%d"),
            data_fim=data_fim.strftime("%Y-%m-%d")
        )

        if movs:
            df_mov = pd.DataFrame(movs)

            # Métricas rápidas do filtro
            total_entradas = len(df_mov[df_mov["tipo"] == "ENTRADA"])
            total_saidas = len(df_mov[df_mov["tipo"] == "SAIDA"])

            col_hm1, col_hm2, col_hm3 = st.columns(3)
            col_hm1.metric("Registros no Período", f"{len(df_mov)} lançamentos")
            col_hm2.metric("Total Entradas", f"{total_entradas} lançamentos")
            col_hm3.metric("Total Saídas", f"{total_saidas} lançamentos")

            df_mov_export = pd.DataFrame({
                "Data/Hora": df_mov["data_movimentacao"],
                "Tipo": df_mov["tipo"],
                "Código Produto": df_mov["produto_codigo"],
                "Nome Produto": df_mov["produto_nome"],
                "Categoria": df_mov["produto_categoria"],
                "Quantidade": df_mov["quantidade"],
                "Unidade": df_mov["unidade_medida"],
                "Saldo Anterior": df_mov["saldo_anterior"],
                "Saldo Posterior": df_mov["saldo_posterior"],
                "Responsável": df_mov["usuario_nome"],
                "Observação": df_mov["observacao"]
            })

            df_mov_display = pd.DataFrame({
                "Data/Hora": df_mov["data_movimentacao"],
                "Tipo": df_mov["tipo"].apply(lambda t: "🟢 ENTRADA" if t == "ENTRADA" else "🔴 SAÍDA"),
                "Código": df_mov["produto_codigo"],
                "Produto": df_mov["produto_nome"],
                "Quantidade": df_mov.apply(lambda r: f"{r['quantidade']:.2f} {r['unidade_medida']}", axis=1),
                "Saldo Anterior": df_mov["saldo_anterior"].apply(lambda s: f"{s:.2f}"),
                "Saldo Posterior": df_mov["saldo_posterior"].apply(lambda s: f"{s:.2f}"),
                "Responsável": df_mov["usuario_nome"].fillna("—"),
                "Observação": df_mov["observacao"].fillna("")
            })

            st.dataframe(df_mov_display, use_container_width=True, hide_index=True)

            csv_data = df_mov_export.to_csv(index=False, sep=";", encoding="utf-8-sig")
            st.download_button(
                label="📥 Baixar Histórico de Movimentações (CSV)",
                data=csv_data,
                file_name=f"historico_movimentacoes_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.info("Nenhuma movimentação encontrada para o período e critérios selecionados.")
