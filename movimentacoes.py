import streamlit as st
import pandas as pd
from datetime import datetime, date
import database

def render_movimentacoes():
    """Renderiza a tela de movimentações de estoque (entradas e saídas)."""
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="color: #2E7D32; margin-bottom: 0.2rem;">🔄 Movimentação de Estoque</h2>
            <p style="color: #666; font-size: 0.95rem;">Lance entradas (compras/recebimentos) e saídas (aplicações/consumo) com controle automático de saldo</p>
        </div>
    """, unsafe_allow_html=True)

    usuario = st.session_state.get("usuario", {})
    produtos = database.get_produtos()

    if not produtos:
        st.warning("Nenhum produto cadastrado no momento. Cadastre produtos no menu 'Cadastro de Produtos' antes de realizar movimentações.")
        return

    # Mapear produtos para seleção rápida
    prod_map = {f"[{p['codigo']}] {p['nome']} (Disponível: {p['quantidade']:.2f} {p['unidade_medida']})": p for p in produtos}

    tab_lancar, tab_historico = st.tabs(["📝 Lançar Nova Movimentação", "📜 Histórico Rápido de Movimentações"])

    # ==================== ABA 1: LANÇAR MOVIMENTAÇÃO ====================
    with tab_lancar:
        col_form, col_info = st.columns([1.8, 1.2])

        with col_form:
            st.markdown("##### Informações do Lançamento")
            
            tipo_mov = st.radio(
                "Tipo de Operação*",
                options=["ENTRADA", "SAIDA"],
                format_func=lambda x: "🟢 ENTRADA (Compra / Chegada na Fazenda)" if x == "ENTRADA" else "🔴 SAÍDA (Aplicação na Lavoura / Consumo)",
                horizontal=True
            )

            produto_chave = st.selectbox("Selecione o Produto / Insumo*", options=list(prod_map.keys()))
            prod_selecionado = prod_map[produto_chave]
            saldo_atual = float(prod_selecionado["quantidade"])
            unidade = prod_selecionado["unidade_medida"]

            col_q, col_d = st.columns(2)
            with col_q:
                quantidade = st.number_input(
                    f"Quantidade ({unidade})*",
                    min_value=0.01,
                    value=1.00,
                    step=1.00,
                    format="%.2f"
                )
            with col_d:
                data_hoje = date.today()
                data_selecionada = st.date_input("Data da Operação*", value=data_hoje)

            hora_atual = datetime.now().strftime("%H:%M")
            data_hora_formatada = f"{data_selecionada.strftime('%Y-%m-%d')} {hora_atual}"

            observacao = st.text_area(
                "Observação / Justificativa",
                placeholder="Ex: Aplicação no Talhão 03 da Soja; Compra NF 12345; Manutenção preventiva trator..."
            ).strip()

            btn_confirmar = st.button("🚀 Confirmar e Salvar Movimentação", type="primary", use_container_width=True)

        with col_info:
            st.markdown("##### 📌 Resumo da Operação")
            
            # Card com status do produto
            st.markdown(f"""
                <div style="background-color: #F8FAF8; border-left: 4px solid #2E7D32; padding: 12px; border-radius: 4px; margin-bottom: 15px;">
                    <div style="font-size: 0.85rem; color: #666;">PRODUTO SELECIONADO</div>
                    <div style="font-weight: bold; font-size: 1.05rem; color: #1B2A1E;">{prod_selecionado['nome']}</div>
                    <div style="font-size: 0.9rem; color: #444;">Código: <code>{prod_selecionado['codigo']}</code></div>
                    <div style="font-size: 0.9rem; color: #444;">Categoria: {prod_selecionado['categoria']}</div>
                </div>
            """, unsafe_allow_html=True)

            # Cálculo de simulação de saldo
            if tipo_mov == "ENTRADA":
                novo_saldo_simulado = saldo_atual + quantidade
                st.info(f"""
                - **Saldo Atual:** {saldo_atual:.2f} {unidade}
                - **Entrada Solicitada:** +{quantidade:.2f} {unidade}
                - **Previsão de Saldo Final:** **{novo_saldo_simulado:.2f} {unidade}**
                """)
            else:
                novo_saldo_simulado = saldo_atual - quantidade
                if quantidade > saldo_atual:
                    st.error(f"""
                    ⛔ **BLOQUEIO DE SAÍDA:**
                    
                    A quantidade solicitada (**{quantidade:.2f} {unidade}**) é **maior que o saldo disponível** em estoque (**{saldo_atual:.2f} {unidade}**)!
                    
                    *O sistema não permite saldo negativo.*
                    """)
                else:
                    st.warning(f"""
                    - **Saldo Atual:** {saldo_atual:.2f} {unidade}
                    - **Saída Solicitada:** -{quantidade:.2f} {unidade}
                    - **Previsão de Saldo Final:** **{novo_saldo_simulado:.2f} {unidade}**
                    """)

        # Processar submissão ao clicar no botão
        if btn_confirmar:
            # Validação imediata de saída
            if tipo_mov == "SAIDA" and quantidade > saldo_atual:
                st.error(
                    f"❌ Movimentação RECUSADA! A quantidade de saída ({quantidade:.2f} {unidade}) "
                    f"é superior ao saldo disponível em estoque ({saldo_atual:.2f} {unidade})."
                )
            else:
                sucesso, msg = database.registrar_movimentacao(
                    produto_id=prod_selecionado["id"],
                    tipo=tipo_mov,
                    quantidade=quantidade,
                    data_mov=data_hora_formatada,
                    observacao=observacao,
                    usuario_id=usuario.get("id"),
                    usuario_nome=usuario.get("nome", "Usuário")
                )
                if sucesso:
                    st.success(msg)
                    st.balloons()
                    st.rerun()
                else:
                    st.error(msg)

    # ==================== ABA 2: HISTÓRICO RÁPIDO ====================
    with tab_historico:
        st.markdown("##### 📜 Últimas 20 Movimentações de Estoque")
        movs = database.get_movimentacoes(limite=20)
        
        if movs:
            df = pd.DataFrame(movs)
            df_display = pd.DataFrame({
                "Data/Hora": df["data_movimentacao"],
                "Operação": df["tipo"].apply(lambda t: "🟢 ENTRADA" if t == "ENTRADA" else "🔴 SAÍDA"),
                "Código": df["produto_codigo"],
                "Produto": df["produto_nome"],
                "Qtd Movimentada": df.apply(lambda r: f"{r['quantidade']:.2f} {r['unidade_medida']}", axis=1),
                "Saldo Anterior": df.apply(lambda r: f"{r['saldo_anterior']:.2f}", axis=1),
                "Saldo Atualizado": df.apply(lambda r: f"{r['saldo_posterior']:.2f}", axis=1),
                "Responsável": df["usuario_nome"].fillna("—"),
                "Observação": df["observacao"].fillna("")
            })
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma movimentação realizada ainda.")
