import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime
from docx import Document

# -------------------------
# Funções auxiliares
# -------------------------

def carregar_pedidos():
    if os.path.exists('pedidos.xlsx'):
        df = pd.read_excel('pedidos.xlsx')
        # Preencher valores NaN com string vazia para evitar erros
        df['Produtos'] = df['Produtos'].fillna('')
        df['Quantidades'] = df['Quantidades'].fillna('')
        df['Cliente'] = df['Cliente'].fillna('')
        df['DataHora'] = df['DataHora'].fillna('')
        return df
    else:
        return pd.DataFrame(columns=['Cliente', 'Produtos', 'Quantidades', 'DataHora'])

def salvar_pedidos(df):
    df.to_excel('pedidos.xlsx', index=False, engine='openpyxl')

def gerar_word(df):
    doc = Document()
    doc.add_heading('📦 Lista de Pedidos', level=1)

    tabela = doc.add_table(rows=1, cols=len(df.columns))
    tabela.style = 'Light List Accent 1'

    hdr_cells = tabela.rows[0].cells
    for i, coluna in enumerate(df.columns):
        hdr_cells[i].text = coluna

    for _, row in df.iterrows():
        row_cells = tabela.add_row().cells
        for i, coluna in enumerate(df.columns):
            row_cells[i].text = str(row[coluna])

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

def gerar_ficha_pedido(pedido):
    doc = Document()
    doc.add_heading('🛒 Ficha do Pedido', level=1)

    doc.add_paragraph(f"Cliente: {pedido['Cliente']}")
    doc.add_paragraph(f"Data do Pedido: {pedido['DataHora']}")

    doc.add_heading('Produtos:', level=2)

    # Converte para string e evita erro se valor for NaN
    produtos_str = str(pedido['Produtos']) if pd.notna(pedido['Produtos']) else ''
    quantidades_str = str(pedido['Quantidades']) if pd.notna(pedido['Quantidades']) else ''

    produtos = produtos_str.split(',')
    quantidades = quantidades_str.split(',')

    for produto, quantidade in zip(produtos, quantidades):
        doc.add_paragraph(f"- {produto.strip()} — {quantidade.strip()} unidades")

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# -------------------------
# Configuração da página
# -------------------------

st.set_page_config(page_title="Sistema de Pedidos", page_icon="🛒")
st.title("🛒 Sistema de Pedidos - Sabor da Feira")

# -------------------------
# Carregar histórico
# -------------------------

if 'pedidos' not in st.session_state:
    st.session_state['pedidos'] = carregar_pedidos()

# -------------------------
# Formulário de cadastro
# -------------------------

st.subheader("📦 Cadastrar Pedido")

with st.form("form_pedido"):
    cliente = st.text_input("👤 Nome do cliente")
    produtos = st.text_input("📦 Produtos (separe por vírgula)")
    quantidades = st.text_input("🔢 Quantidades (na mesma ordem, separadas por vírgula)")

    enviar = st.form_submit_button("Salvar Pedido")

    if enviar:
        produtos_lista = [p.strip() for p in produtos.split(',')]
        quantidades_lista = [q.strip() for q in quantidades.split(',')]

        if len(produtos_lista) != len(quantidades_lista):
            st.error("❌ O número de produtos e quantidades não confere!")
        else:
            try:
                quantidades_int = [int(q) for q in quantidades_lista]
                data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                novo_pedido = pd.DataFrame(
                    [[cliente, ', '.join(produtos_lista), ', '.join(map(str, quantidades_int)), data_hora]],
                    columns=['Cliente', 'Produtos', 'Quantidades', 'DataHora']
                )

                st.session_state['pedidos'] = pd.concat(
                    [st.session_state['pedidos'], novo_pedido],
                    ignore_index=True
                )

                salvar_pedidos(st.session_state['pedidos'])
                st.success(f"✅ Pedido do cliente {cliente} cadastrado com sucesso!")

            except ValueError:
                st.error("❌ Verifique se as quantidades estão corretas. Use apenas números.")

# -------------------------
# Visualização dos pedidos
# -------------------------

st.subheader("🧾 Lista de Pedidos")
st.dataframe(st.session_state['pedidos'], use_container_width=True)

# -------------------------
# Exportar Dados
# -------------------------

st.subheader("💾 Exportar Dados")

col1, col2, col3 = st.columns(3)

with col1:
    excel_buffer = io.BytesIO()
    st.session_state['pedidos'].to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)

    st.download_button(
        label="⬇️ Baixar Excel",
        data=excel_buffer,
        file_name='pedidos.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

with col2:
    csv = st.session_state['pedidos'].to_csv(index=False, sep=';').encode('utf-8')
    st.download_button(
        label="⬇️ Baixar CSV",
        data=csv,
        file_name='pedidos.csv',
        mime='text/csv'
    )

with col3:
    word_file = gerar_word(st.session_state['pedidos'])
    st.download_button(
        label="⬇️ Baixar Word (Todos os Pedidos)",
        data=word_file,
        file_name='pedidos.docx',
        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

# -------------------------
# Gerar ficha individual
# -------------------------

st.subheader("📄 Gerar Ficha Individual (Word)")

if not st.session_state['pedidos'].empty:
    pedido_selecionado = st.selectbox(
        "Selecione o pedido",
        options=st.session_state['pedidos'].index,
        format_func=lambda idx: f"{st.session_state['pedidos'].loc[idx, 'Cliente']} - {st.session_state['pedidos'].loc[idx, 'DataHora']}"
    )

    ficha_word = gerar_ficha_pedido(st.session_state['pedidos'].loc[pedido_selecionado])

    st.download_button(
        label="⬇️ Baixar Ficha Individual (.docx)",
        data=ficha_word,
        file_name=f"pedido_{pedido_selecionado}.docx",
        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
else:
    st.info("Nenhum pedido cadastrado ainda.")
