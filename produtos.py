import streamlit as st
import pandas as pd
import database

def render_produtos():
    """Renderiza a tela de listagem, consulta e cadastro de produtos."""
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="color: #2E7D32; margin-bottom: 0.2rem;">📦 Cadastro e Catálogo de Produtos</h2>
            <p style="color: #666; font-size: 0.95rem;">Gerencie os insumos, sementes, defensivos e produtos rurais da propriedade</p>
        </div>
    """, unsafe_allow_html=True)

    usuario = st.session_state.get("usuario", {})
    e_admin = usuario.get("perfil") == "administrador"

    tab_catalogo, tab_novo, tab_editar = st.tabs([
        "📋 Catálogo de Produtos",
        "➕ Cadastrar Novo Produto",
        "✏️ Editar Produto" if e_admin else "🔍 Detalhes do Produto"
    ])

    
    with tab_catalogo:
        col_filtro1, col_filtro2, col_filtro3 = st.columns([2, 1.5, 1.5])

        with col_filtro1:
            termo_busca = st.text_input("🔍 Buscar por nome ou código", placeholder="Ex: Ureia, Milho, DEF-001...").strip()
        with col_filtro2:
            opcoes_cat = ["Todas"] + database.CATEGORIAS_PADRAO
            categoria_sel = st.selectbox("Categoria", options=opcoes_cat)
        with col_filtro3:
            st.write("")
            st.write("")
            apenas_baixo = st.checkbox("⚠️ Apenas estoque baixo/crítico")

        produtos = database.get_produtos(
            termo_busca=termo_busca if termo_busca else None,
            categoria=categoria_sel,
            apenas_estoque_baixo=apenas_baixo
        )

        if produtos:
            df = pd.DataFrame(produtos)

            
            df_display = pd.DataFrame({
                "Código": df["codigo"],
                "Nome do Insumo / Produto": df["nome"],
                "Categoria": df["categoria"],
                "Unidade": df["unidade_medida"],
                "Qtd Disponível": df["quantidade"].apply(lambda q: f"{q:,.2f}"),
                "Estoque Mínimo": df["estoque_minimo"].apply(lambda m: f"{m:,.2f}"),
                "Preço Unitário": df["preco_unitario"].apply(lambda p: f"R$ {p:,.2f}"),
                "Valor Total": df["valor_total"].apply(lambda v: f"R$ {v:,.2f}"),
                "Status": df["status_estoque"].apply(
                    lambda s: "🚨 Zerado" if s == "Zerado" else ("⚠️ Estoque Baixo" if s == "Estoque Baixo" else "✅ Normal")
                )
            })

            st.dataframe(df_display, use_container_width=True, hide_index=True)
            st.caption(f"Exibindo **{len(produtos)}** produto(s) encontrado(s).")
        else:
            st.info("Nenhum produto encontrado com os filtros selecionados.")

    
    with tab_novo:
        st.markdown("##### 📝 Formulário de Cadastro de Insumo Agrícola")
        st.info("Preencha as informações do produto. Se informar quantidade maior que zero, uma movimentação de entrada inicial será registrada automaticamente.")

        with st.form("form_cadastrar_produto", clear_on_submit=True):
            col_c1, col_c2 = st.columns(2)

            with col_c1:
                codigo = st.text_input("Código do Produto / SKU*", placeholder="Ex: FERT-003, SEM-010").strip().upper()
                nome = st.text_input("Nome do Produto*", placeholder="Ex: Adubo Fosfatado Super Triplo").strip()
                categoria = st.selectbox("Categoria do Produto*", options=database.CATEGORIAS_PADRAO)
                unidade_medida = st.selectbox("Unidade de Medida*", options=database.UNIDADES_MEDIDA)

            with col_c2:
                quantidade = st.number_input("Quantidade Disponível Inicial*", min_value=0.0, value=0.0, step=1.0, format="%.2f")
                estoque_minimo = st.number_input("Estoque Mínimo de Segurança*", min_value=0.0, value=10.0, step=1.0, format="%.2f")
                preco_unitario = st.number_input("Preço Unitário (R$)*", min_value=0.0, value=0.0, step=0.50, format="%.2f")

            btn_salvar = st.form_submit_button("💾 Salvar Produto", use_container_width=True, type="primary")

            if btn_salvar:
                if not codigo or not nome:
                    st.error("Os campos 'Código' e 'Nome' são de preenchimento obrigatório.")
                else:
                    sucesso, msg = database.add_produto(
                        codigo=codigo,
                        nome=nome,
                        categoria=categoria,
                        unidade_medida=unidade_medida,
                        quantidade=quantidade,
                        estoque_minimo=estoque_minimo,
                        preco_unitario=preco_unitario,
                        usuario_id=usuario.get("id"),
                        usuario_nome=usuario.get("nome")
                    )
                    if sucesso:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

   
    with tab_editar:
        todos_prods = database.get_produtos()
        if not todos_prods:
            st.info("Não há produtos cadastrados para edição.")
        else:
            opcoes_dict = {f"[{p['codigo']}] {p['nome']} (Estoque: {p['quantidade']:.1f} {p['unidade_medida']})": p for p in todos_prods}
            escolha = st.selectbox("Selecione o produto a ser visualizado/editado:", options=list(opcoes_dict.keys()))
            prod_sel = opcoes_dict[escolha]

            st.markdown(f"##### Editando: `{prod_sel['codigo']}` - {prod_sel['nome']}")

            if not e_admin:
                st.warning("⚠️ Somente administradores têm permissão para alterar os dados cadastrais do produto.")
                st.write(f"- **Categoria:** {prod_sel['categoria']}")
                st.write(f"- **Unidade de Medida:** {prod_sel['unidade_medida']}")
                st.write(f"- **Estoque Atual:** {prod_sel['quantidade']:.2f} {prod_sel['unidade_medida']}")
                st.write(f"- **Estoque Mínimo:** {prod_sel['estoque_minimo']:.2f}")
                st.write(f"- **Preço Unitário:** R$ {prod_sel['preco_unitario']:.2f}")
            else:
                with st.form("form_editar_produto"):
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        e_codigo = st.text_input("Código do Produto*", value=prod_sel["codigo"]).strip().upper()
                        e_nome = st.text_input("Nome do Produto*", value=prod_sel["nome"]).strip()
                        
                        idx_cat = database.CATEGORIAS_PADRAO.index(prod_sel["categoria"]) if prod_sel["categoria"] in database.CATEGORIAS_PADRAO else 0
                        e_categoria = st.selectbox("Categoria*", options=database.CATEGORIAS_PADRAO, index=idx_cat)

                    with col_e2:
                        idx_und = database.UNIDADES_MEDIDA.index(prod_sel["unidade_medida"]) if prod_sel["unidade_medida"] in database.UNIDADES_MEDIDA else 0
                        e_unidade = st.selectbox("Unidade de Medida*", options=database.UNIDADES_MEDIDA, index=idx_und)
                        e_minimo = st.number_input("Estoque Mínimo*", min_value=0.0, value=float(prod_sel["estoque_minimo"]), step=1.0, format="%.2f")
                        e_preco = st.number_input("Preço Unitário (R$)*", min_value=0.0, value=float(prod_sel["preco_unitario"]), step=0.50, format="%.2f")

                    st.caption("ℹ️ O saldo de estoque físico é ajustado apenas via o menu 'Movimentação de Estoque' para manter o histórico de auditoria.")
                    btn_atualizar = st.form_submit_button("Atualizar Dados Cadastrais", type="primary")

                    if btn_atualizar:
                        sucesso, msg = database.update_produto(
                            produto_id=prod_sel["id"],
                            codigo=e_codigo,
                            nome=e_nome,
                            categoria=e_categoria,
                            unidade_medida=e_unidade,
                            estoque_minimo=e_minimo,
                            preco_unitario=e_preco
                        )
                        if sucesso:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
