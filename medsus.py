import streamlit as st
import pandas as pd
from scraper import buscar_medicamento
from ibge import find_states_by_input, find_municipios
from bnafar import buscar_bnafar
from datetime import datetime, date

st.set_page_config(layout="wide")
st.title("MEDSUS - Consulta de Medicamentos")

# =======================
#  BUSCA DE MEDICAMENTO
# =======================f

with st.container():
    col1, col2 = st.columns([3, 5])

    with col1:
        st.header("🔎 Nome do Medicamento")
        medicamento = st.text_input(
            "Insira o nome do medicamento que deseja buscar:",
            key="med_text"
        )

        if st.button("Buscar medicamento", key="btn_medic"):
            if medicamento.strip() == "":
                st.warning("Por favor, insira um nome de medicamento.")
            else:
                df_medic = buscar_medicamento(medicamento)
                df_medic = df_medic.copy()
                df_medic.insert(0, "Selecionar", False)
                st.session_state["med_df"] = df_medic

    with col2:
        if "med_df" in st.session_state:
            st.subheader("📋 Resultado da Busca")

            df = st.session_state["med_df"]

            df_editado = st.data_editor(
                df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Selecionar": st.column_config.CheckboxColumn(
                        "Selecionar",
                        help="Selecione apenas um medicamento"
                    )
                }
            )

            # ---- garante apenas um checkbox marcado
            selecionados = df_editado[df_editado["Selecionar"]]

            if len(selecionados) > 1:
                idx = selecionados.index[0]
                df_editado["Selecionar"] = False
                df_editado.loc[idx, "Selecionar"] = True
                st.warning("Apenas um medicamento pode ser selecionado.")

            st.session_state["med_df"] = df_editado

            selecionado = df_editado[df_editado["Selecionar"]]

            if len(selecionado) == 1:
                st.success("Medicamento selecionado:")
                st.dataframe(
                    selecionado.drop(columns=["Selecionar"]),
                    use_container_width=True
                )

st.markdown("---")

# ===========================
#  BUSCA DE ESTADO / MUNICÍPIO
# ===========================

with st.container():
    col_left, col_right = st.columns([3, 6])

    with col_left:
        st.header("📍 Informe UF e Município")

        estado_input = st.text_input(
            "Digite código, sigla ou nome parcial do estado:",
            key="est_text"
        )

        estado_selected = None
        estados_suggestions = []

        if estado_input:
            estados_suggestions = find_states_by_input(estado_input)

            if len(estados_suggestions) == 1:
                estado_selected = estados_suggestions[0]
            elif len(estados_suggestions) > 1:
                estado_selected = st.selectbox(
                    "Várias opções de estados encontrados:",
                    options=estados_suggestions,
                    format_func=lambda e: f"{e['sigla']} — {e['nome']} (ID {e['id']})"
                )
            else:
                st.warning("Nenhum estado encontrado.")

        municipio_input = None
        if estado_selected:
            municipio_input = st.text_input(
                f"Digite código ou nome parcial do município em {estado_selected['nome']}:",
                key="mun_text"
            )

    with col_right:
        if estado_selected:
            st.subheader("📍 Estado selecionado")
            st.success(
                f"{estado_selected['nome']} ({estado_selected['sigla']}) — ID {estado_selected['id']}"
            )

        if estado_selected and municipio_input:
            municipios_suggestions = find_municipios(
                estado_selected["id"],
                municipio_input
            )

            if len(municipios_suggestions) == 0:
                st.warning("Nenhum município encontrado.")

            else:
                st.subheader("📍 Municípios encontrados")

                df_munis = pd.DataFrame([
                    {
                        "Selecionar": False,
                        "Nome": m["nome"],
                        "ID": m["id"]
                    }
                    for m in municipios_suggestions
                ])

                # mantém seleção anterior
                if "mun_df" in st.session_state:
                    df_ant = st.session_state["mun_df"]
                    for i in df_munis.index:
                        if (
                            i in df_ant.index
                            and df_ant.loc[i, "Selecionar"]
                        ):
                            df_munis.loc[i, "Selecionar"] = True

                df_munis_editado = st.data_editor(
                    df_munis,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "Selecionar": st.column_config.CheckboxColumn(
                            "Selecionar",
                            help="Selecione apenas um município"
                        )
                    }
                )

                # ---- garante apenas um checkbox marcado
                selecionados = df_munis_editado[df_munis_editado["Selecionar"]]

                if len(selecionados) > 1:
                    idx = selecionados.index[0]
                    df_munis_editado["Selecionar"] = False
                    df_munis_editado.loc[idx, "Selecionar"] = True
                    st.warning("Apenas um município pode ser selecionado.")

                st.session_state["mun_df"] = df_munis_editado

                mun_sel = df_munis_editado[df_munis_editado["Selecionar"]]

                if len(mun_sel) == 1:
                    st.success(
                        f"Município selecionado: {mun_sel.iloc[0]['Nome']} — ID {mun_sel.iloc[0]['ID']}"
                    )

st.markdown("---")
st.header("📦 Consulta de Estoque Medicamentos")

if (
    "med_df" in st.session_state
    and "mun_df" in st.session_state
):

    med_sel = st.session_state["med_df"]
    med_sel = med_sel[med_sel["Selecionar"]]

    mun_sel = st.session_state["mun_df"]
    mun_sel = mun_sel[mun_sel["Selecionar"]]

    if len(med_sel) == 1 and len(mun_sel) == 1:

        codigo_catmat = med_sel.iloc[0]["Código"]
        codigo_catmat = f"BR0{codigo_catmat}"

        codigo_uf = estado_selected["id"]
        codigo_municipio = mun_sel.iloc[0]["ID"]

        # =============================
        # COMPETÊNCIA (ANO / MÊS)
        # =============================

        st.subheader("🗓️ Competência do Estoque")

        col_ano, col_mes = st.columns(2)

        with col_ano:
            ano = st.selectbox(
                "Ano",
                options=list(range(2015, datetime.now().year + 1)),
                index=(datetime.now().year - 2015)
            )

        with col_mes:
            mes = st.selectbox(
                "Mês",
                options=list(range(1, 13)),
                format_func=lambda x: f"{x:02d}"
            )

        hoje = date.today()

        # 🚫 BLOQUEAR DATA FUTURA
        if ano > hoje.year or (ano == hoje.year and mes > hoje.month):
            st.error("Não é possível consultar meses futuros.")
            st.stop()

        anomes = f"{ano}{mes:02d}"

        # =============================
        # BOTÃO CONSULTA
        # =============================

        if st.button("Buscar estoque BNAFAR"):
            with st.spinner("Consultando BNAFAR..."):

                df_bnafar = buscar_bnafar(
                    codigo_uf=codigo_uf,
                    codigo_municipio=codigo_municipio,
                    codigo_catmat=codigo_catmat,
                    anomes_posicao_estoque=anomes
                )

            if df_bnafar.empty:
                st.warning("Nenhum registro encontrado para os filtros informados.")
            else:

                # ====================================
                # FILTRAR APENAS ESTOQUE > 0
                # ====================================

                df_bnafar = df_bnafar[df_bnafar["quantidade_estoque"] > 0]

                if df_bnafar.empty:
                    st.warning("Não há estoque disponível (quantidade > 0).")
                else:

                    # ====================================
                    # MÉTRICAS RESUMO
                    # ====================================

                    estoque_total = df_bnafar["quantidade_estoque"].sum()

                    total_cnes = df_bnafar["codigo_cnes"].nunique()

                    col1, col2 = st.columns(2)

                    col1.metric("📦 Estoque Total Disponível", f"{estoque_total:,}")
                    col2.metric("🏥 Total de Estabelecimentos (CNES)", total_cnes)

                    st.markdown("---")

                    # ====================================
                    # SOMA POR CNES
                    # ====================================

                    st.subheader("📊 Estoque por Estabelecimento (CNES)")

                    df_por_cnes = (
                        df_bnafar
                        .groupby(
                            [
                                "codigo_cnes",
                                "razao_social",
                                "municipio"
                            ],
                            as_index=False
                        )["quantidade_estoque"]
                        .sum()
                        .sort_values("quantidade_estoque", ascending=False)
                    )

                    st.dataframe(df_por_cnes, use_container_width=True)

                    st.markdown("---")

                    # ====================================
                    # DETALHAMENTO COMPLETO
                    # ====================================

                    st.subheader("📋 Detalhamento Completo")

                    st.dataframe(df_bnafar, use_container_width=True)

    else:
        st.info("Selecione exatamente UM medicamento e UM localidade para consultar o estoque.")
