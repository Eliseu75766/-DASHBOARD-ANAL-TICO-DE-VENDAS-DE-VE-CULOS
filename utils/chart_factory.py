import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Função para carregar os dados
def load_data():
    vendas = pd.read_csv('data/vendas.csv')
    metas = pd.read_csv('data/metas.csv')
    modelos = pd.read_csv('data/modelos.csv')
    
    # Converter data_venda para datetime
    vendas['data_venda'] = pd.to_datetime(vendas['data_venda'])
    
    # Adicionar colunas de data para facilitar análises
    vendas['data'] = vendas['data_venda'].dt.date
    vendas['mes'] = vendas['data_venda'].dt.month
    vendas['ano'] = vendas['data_venda'].dt.year
    vendas['dia_semana'] = vendas['data_venda'].dt.dayofweek
    vendas['hora'] = vendas['data_venda'].dt.hour
    vendas['periodo'] = vendas['data_venda'].dt.strftime('%Y-%m')
    
    return vendas, metas, modelos

# Função para criar gráfico de faturamento
def create_faturamento_chart(vendas, metas, filtro_periodo=None, filtro_categorias=None, filtro_canais=None):
    # Aplicar filtros se fornecidos
    df = vendas.copy()
    if filtro_periodo:
        data_inicio, data_fim = filtro_periodo
        df = df[(df['data_venda'] >= data_inicio) & (df['data_venda'] <= data_fim)]
    
    if filtro_categorias:
        df = df[df['categoria'].isin(filtro_categorias)]
    
    if filtro_canais:
        df = df[df['canal_venda'].isin(filtro_canais)]
    
    # Agrupar por período (mês)
    faturamento_mensal = df.groupby('periodo').agg({
        'preco_venda': 'sum',
        'id_venda': 'count'
    }).reset_index()
    
    faturamento_mensal.columns = ['periodo', 'faturamento', 'quantidade']
    
    # Mesclar com metas
    metas_copy = metas.copy()
    metas_copy['periodo'] = metas_copy['periodo']
    faturamento_mensal = pd.merge(faturamento_mensal, metas_copy[['periodo', 'meta_faturamento']], on='periodo', how='left')
    
    # Calcular percentual de atingimento da meta
    faturamento_mensal['atingimento'] = (faturamento_mensal['faturamento'] / faturamento_mensal['meta_faturamento']) * 100
    
    # Criar gráfico de linha e área para faturamento
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Gráfico de área para faturamento
    fig.add_trace(
        go.Scatter(
            x=faturamento_mensal['periodo'],
            y=faturamento_mensal['faturamento'],
            name="Faturamento",
            line=dict(color="#00FFFF", width=3),
            mode='lines',
            fill='tozeroy',
            fillcolor='rgba(0, 255, 255, 0.2)'
        )
    )
    
    # Gráfico de linha para meta
    fig.add_trace(
        go.Scatter(
            x=faturamento_mensal['periodo'],
            y=faturamento_mensal['meta_faturamento'],
            name="Meta",
            line=dict(color="#FF5F1F", width=3, dash='dash'),
            mode='lines'
        )
    )
    
    # Gráfico de barras para quantidade de vendas no eixo secundário
    fig.add_trace(
        go.Bar(
            x=faturamento_mensal['periodo'],
            y=faturamento_mensal['quantidade'],
            name="Quantidade",
            marker=dict(color="rgba(248, 248, 255, 0.3)"),
            opacity=0.7
        ),
        secondary_y=True
    )
    
    # Adicionar anotações para campanhas
    campanhas = metas[metas['campanhas_ativas'].notna()]
    for _, campanha in campanhas.iterrows():
        fig.add_annotation(
            x=campanha['periodo'],
            y=campanha['meta_faturamento'] * 1.1,
            text=campanha['campanhas_ativas'],
            showarrow=True,
            arrowhead=2,
            arrowcolor="#FF5F1F",
            arrowsize=1,
            arrowwidth=2,
            bgcolor="rgba(13, 13, 13, 0.7)",
            bordercolor="#FF5F1F",
            borderwidth=2,
            borderpad=4,
            font=dict(color="#F8F8FF", family="Orbitron")
        )
    
    # Personalizar layout
    fig.update_layout(
        title={
            'text': "Evolução do Faturamento vs. Meta",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(family="Orbitron", size=24, color="#F8F8FF")
        },
        paper_bgcolor='rgba(13, 13, 13, 0.0)',
        plot_bgcolor='rgba(13, 13, 13, 0.0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family="Montserrat", color="#F8F8FF")
        ),
        margin=dict(l=20, r=20, t=80, b=20),
        height=500,
        hovermode="x unified"
    )
    
    # Personalizar eixos
    fig.update_xaxes(
        title=dict(
            text="Período",
            font=dict(family="Montserrat", color="#F8F8FF")
        ),
        tickfont=dict(family="Montserrat", color="#F8F8FF"),
        showgrid=True,
        gridcolor='rgba(248, 248, 255, 0.1)',
        zeroline=False
    )
    
    fig.update_yaxes(
        title=dict(
            text="Faturamento (R$)",
            font=dict(family="Montserrat", color="#00FFFF")
        ),
        tickfont=dict(family="Montserrat", color="#00FFFF"),
        showgrid=True,
        gridcolor='rgba(0, 255, 255, 0.1)',
        zeroline=False,
        secondary_y=False
    )
    
    fig.update_yaxes(
        title=dict(
            text="Quantidade de Vendas",
            font=dict(family="Montserrat", color="#F8F8FF")
        ),
        tickfont=dict(family="Montserrat", color="#F8F8FF"),
        showgrid=False,
        zeroline=False,
        secondary_y=True
    )
    
    return fig, faturamento_mensal

# Função para criar gráfico de margem de lucro
def create_margem_chart(vendas, filtro_periodo=None, filtro_categorias=None, filtro_canais=None):
    # Aplicar filtros se fornecidos
    df = vendas.copy()
    if filtro_periodo:
        data_inicio, data_fim = filtro_periodo
        df = df[(df['data_venda'] >= data_inicio) & (df['data_venda'] <= data_fim)]
    
    if filtro_categorias:
        df = df[df['categoria'].isin(filtro_categorias)]
    
    if filtro_canais:
        df = df[df['canal_venda'].isin(filtro_canais)]
    
    # Agrupar por categoria e período
    margem_categoria = df.groupby(['categoria', 'periodo']).agg({
        'preco_venda': 'sum',
        'custo': 'sum',
        'lucro': 'sum',
        'id_venda': 'count'
    }).reset_index()
    
    # Calcular margens
    margem_categoria['margem_percentual'] = (margem_categoria['lucro'] / margem_categoria['preco_venda']) * 100
    
    # Criar gráfico de barras empilhadas
    fig = go.Figure()
    
    categorias = margem_categoria['categoria'].unique()
    periodos = sorted(margem_categoria['periodo'].unique())
    
    # Cores para cada categoria
    cores = {
        'SUV': '#00FFFF',
        'Sedan': '#FF5F1F',
        'Hatch': '#F8F8FF',
        'Pickup': '#9933FF',
        'Elétrico': '#33FF99'
    }
    
    # Adicionar barras para cada categoria
    for categoria in categorias:
        df_cat = margem_categoria[margem_categoria['categoria'] == categoria]
        fig.add_trace(
            go.Bar(
                x=df_cat['periodo'],
                y=df_cat['lucro'],
                name=categoria,
                marker=dict(color=cores.get(categoria, '#F8F8FF')),
                hovertemplate='<b>%{x}</b><br>Lucro: R$ %{y:,.2f}<br>Margem: %{customdata:.2f}%<extra></extra>',
                customdata=df_cat['margem_percentual'],
                text=df_cat['margem_percentual'].apply(lambda x: f'{x:.2f}%'),
                textposition='inside'
            )
        )
    
    # Adicionar linha para margem média
    margem_media = df.groupby('periodo').apply(lambda x: (x['lucro'].sum() / x['preco_venda'].sum()) * 100).reset_index()
    margem_media.columns = ['periodo', 'margem_media']
    
    fig.add_trace(
        go.Scatter(
            x=margem_media['periodo'],
            y=margem_media['margem_media'],
            name="Margem Média (%)",
            line=dict(color="#FFFFFF", width=3, dash='dot'),
            mode='lines+markers+text',
            marker=dict(size=8, symbol='diamond', color="#FFFFFF"),
            text=margem_media['margem_media'].apply(lambda x: f'{x:.2f}%'),
            textposition='top center',
            yaxis="y2"
        )
    )
    
    # Personalizar layout
    fig.update_layout(
        title={
            'text': "Margem de Lucro por Categoria",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(family="Orbitron", size=24, color="#F8F8FF")
        },
        paper_bgcolor='rgba(13, 13, 13, 0.0)',
        plot_bgcolor='rgba(13, 13, 13, 0.0)',
        barmode='stack',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family="Montserrat", color="#F8F8FF")
        ),
        margin=dict(l=20, r=20, t=80, b=20),
        height=500,
        hovermode="x unified",
        yaxis=dict(
            title=dict(
                text="Lucro (R$)",
                font=dict(family="Montserrat", color="#F8F8FF")
            ),
            tickfont=dict(family="Montserrat", color="#F8F8FF"),
            showgrid=True,
            gridcolor='rgba(248, 248, 255, 0.1)',
            zeroline=False
        ),
        yaxis2=dict(
            title=dict(
                text="Margem (%)",
                font=dict(family="Montserrat", color="#FFFFFF")
            ),
            tickfont=dict(family="Montserrat", color="#FFFFFF"),
            overlaying="y",
            side="right",
            showgrid=False,
            zeroline=False,
            range=[0, max(margem_media['margem_media']) * 1.2]
        ),
        xaxis=dict(
            title=dict(
                text="Período",
                font=dict(family="Montserrat", color="#F8F8FF")
            ),
            tickfont=dict(family="Montserrat", color="#F8F8FF"),
            showgrid=True,
            gridcolor='rgba(248, 248, 255, 0.1)',
            zeroline=False
        )
    )
    
    return fig, margem_categoria

# Função para criar gráfico de ticket médio
def create_ticket_chart(vendas, metas, filtro_periodo=None, filtro_categorias=None, filtro_canais=None):
    # Aplicar filtros se fornecidos
    df = vendas.copy()
    if filtro_periodo:
        data_inicio, data_fim = filtro_periodo
        df = df[(df['data_venda'] >= data_inicio) & (df['data_venda'] <= data_fim)]
    
    if filtro_categorias:
        df = df[df['categoria'].isin(filtro_categorias)]
    
    if filtro_canais:
        df = df[df['canal_venda'].isin(filtro_canais)]
    
    # Calcular ticket médio por período
    ticket_medio = df.groupby('periodo').agg({
        'preco_venda': 'mean',
        'id_venda': 'count'
    }).reset_index()
    
    ticket_medio.columns = ['periodo', 'ticket_medio', 'quantidade']
    
    # Criar gráfico de velocímetro para o ticket médio atual
    ultimo_periodo = ticket_medio.iloc[-1]
    ticket_atual = ultimo_periodo['ticket_medio']
    
    # Definir valores mínimo e máximo para o velocímetro
    min_ticket = ticket_medio['ticket_medio'].min() * 0.8
    max_ticket = ticket_medio['ticket_medio'].max() * 1.2
    
    # Criar gráfico de velocímetro
    fig_gauge = go.Figure()
    
    # Adicionar arco de fundo
    fig_gauge.add_trace(go.Indicator(
        mode = "gauge+number",
        value = ticket_atual,
        number = {"prefix": "R$ ", "valueformat": ",.2f", "font": {"size": 24, "family": "Orbitron", "color": "#F8F8FF"}},
        gauge = {
            'axis': {'range': [min_ticket, max_ticket], 'tickwidth': 1, 'tickcolor': "#F8F8FF"},
            'bar': {'color': "#FF5F1F"},
            'bgcolor': "rgba(13, 13, 13, 0.7)",
            'borderwidth': 2,
            'bordercolor': "#00FFFF",
            'steps': [
                {'range': [min_ticket, min_ticket + (max_ticket-min_ticket)*0.33], 'color': 'rgba(255, 95, 31, 0.3)'},
                {'range': [min_ticket + (max_ticket-min_ticket)*0.33, min_ticket + (max_ticket-min_ticket)*0.66], 'color': 'rgba(255, 95, 31, 0.5)'},
                {'range': [min_ticket + (max_ticket-min_ticket)*0.66, max_ticket], 'color': 'rgba(255, 95, 31, 0.7)'}
            ],
            'threshold': {
                'line': {'color': "#00FFFF", 'width': 4},
                'thickness': 0.75,
                'value': ticket_atual
            }
        },
        title = {
            'text': "Ticket Médio Atual",
            'font': {"size": 24, "family": "Orbitron", "color": "#F8F8FF"}
        },
        domain = {'x': [0, 1], 'y': [0, 1]}
    ))
    
    # Personalizar layout do velocímetro
    fig_gauge.update_layout(
        paper_bgcolor='rgba(13, 13, 13, 0.0)',
        plot_bgcolor='rgba(13, 13, 13, 0.0)',
        margin=dict(l=20, r=20, t=80, b=20),
        height=300
    )
    
    # Criar gráfico de linha para evolução do ticket médio
    fig_line = go.Figure()
    
    # Adicionar linha para ticket médio
    fig_line.add_trace(
        go.Scatter(
            x=ticket_medio['periodo'],
            y=ticket_medio['ticket_medio'],
            name="Ticket Médio",
            line=dict(color="#00FFFF", width=3),
            mode='lines+markers+text',
            marker=dict(size=8, symbol='circle', color="#00FFFF"),
            text=ticket_medio['ticket_medio'].apply(lambda x: f'R$ {x:,.2f}'),
            textposition='top center'
        )
    )
    
    # Personalizar layout do gráfico de linha
    fig_line.update_layout(
        title={
            'text': "Evolução do Ticket Médio",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(family="Orbitron", size=24, color="#F8F8FF")
        },
        paper_bgcolor='rgba(13, 13, 13, 0.0)',
        plot_bgcolor='rgba(13, 13, 13, 0.0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family="Montserrat", color="#F8F8FF")
        ),
        margin=dict(l=20, r=20, t=80, b=20),
        height=300,
        hovermode="x unified",
        yaxis=dict(
            title=dict(
                text="Ticket Médio (R$)",
                font=dict(family="Montserrat", color="#F8F8FF")
            ),
            tickfont=dict(family="Montserrat", color="#F8F8FF"),
            showgrid=True,
            gridcolor='rgba(248, 248, 255, 0.1)',
            zeroline=False
        ),
        xaxis=dict(
            title=dict(
                text="Período",
                font=dict(family="Montserrat", color="#F8F8FF")
            ),
            tickfont=dict(family="Montserrat", color="#F8F8FF"),
            showgrid=True,
            gridcolor='rgba(248, 248, 255, 0.1)',
            zeroline=False
        )
    )
    
    return fig_gauge, fig_line, ticket_medio

# Função para criar heatmap de análise mensal
def create_heatmap(vendas, filtro_periodo=None, filtro_categorias=None, filtro_canais=None):
    # Aplicar filtros se fornecidos
    df = vendas.copy()
    if filtro_periodo:
        data_inicio, data_fim = filtro_periodo
        df = df[(df['data_venda'] >= data_inicio) & (df['data_venda'] <= data_fim)]
    
    if filtro_categorias:
        df = df[df['categoria'].isin(filtro_categorias)]
    
    if filtro_canais:
        df = df[df['canal_venda'].isin(filtro_canais)]
    
    # Agrupar por modelo e período
    vendas_modelo = df.groupby(['modelo', 'periodo']).agg({
        'id_venda': 'count',
        'preco_venda': 'sum'
    }).reset_index()
    
    # Pivotar para criar matriz para heatmap
    matriz_vendas = vendas_modelo.pivot(index='modelo', columns='periodo', values='id_venda').fillna(0)
    
    # Criar heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matriz_vendas.values,
        x=matriz_vendas.columns,
        y=matriz_vendas.index,
        colorscale=[
            [0, 'rgba(13, 13, 13, 0.7)'],
            [0.2, 'rgba(0, 255, 255, 0.3)'],
            [0.4, 'rgba(0, 255, 255, 0.5)'],
            [0.6, 'rgba(0, 255, 255, 0.7)'],
            [0.8, 'rgba(0, 255, 255, 0.9)'],
            [1, '#00FFFF']
        ],
        hovertemplate='<b>Modelo:</b> %{y}<br><b>Período:</b> %{x}<br><b>Vendas:</b> %{z}<extra></extra>',
        text=matriz_vendas.values.astype(int),
        texttemplate="%{text}",
        textfont={"family": "Montserrat", "size": 12, "color": "#F8F8FF"}
    ))
    
    # Personalizar layout
    fig.update_layout(
        title={
            'text': "Análise de Vendas por Modelo e Período",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(family="Orbitron", size=24, color="#F8F8FF")
        },
        paper_bgcolor='rgba(13, 13, 13, 0.0)',
        plot_bgcolor='rgba(13, 13, 13, 0.0)',
        margin=dict(l=20, r=20, t=80, b=20),
        height=500,
        xaxis=dict(
            title=dict(
                text="Período",
                font=dict(family="Montserrat", color="#F8F8FF")
            ),
            tickfont=dict(family="Montserrat", color="#F8F8FF"),
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title=dict(
                text="Modelo",
                font=dict(family="Montserrat", color="#F8F8FF")
            ),
            tickfont=dict(family="Montserrat", color="#F8F8FF"),
            showgrid=False,
            zeroline=False
        )
    )
    
    return fig, matriz_vendas

# Função para criar gráfico de margem por canal
def create_margem_canal_chart(vendas, filtro_periodo=None, filtro_categorias=None, filtro_canais=None):
    # Aplicar filtros se fornecidos
    df = vendas.copy()
    if filtro_periodo:
        data_inicio, data_fim = filtro_periodo
        df = df[(df['data_venda'] >= data_inicio) & (df['data_venda'] <= data_fim)]
    
    if filtro_categorias:
        df = df[df['categoria'].isin(filtro_categorias)]
    
    if filtro_canais:
        df = df[df['canal_venda'].isin(filtro_canais)]
    
    # Agrupar por canal
    margem_canal = df.groupby('canal_venda').agg({
        'preco_venda': 'sum',
        'custo': 'sum',
        'lucro': 'sum',
        'id_venda': 'count'
    }).reset_index()
    
    # Calcular margens
    margem_canal['margem_percentual'] = (margem_canal['lucro'] / margem_canal['preco_venda']) * 100
    
    # Ordenar por margem
    margem_canal = margem_canal.sort_values('margem_percentual', ascending=False)
    
    # Criar gráfico de barras horizontais
    fig = go.Figure()
    
    # Cores para cada canal
    cores = {
        'Showroom': '#00FFFF',
        'Online': '#FF5F1F',
        'Concessionária': '#F8F8FF',
        'Parceiro': '#9933FF'
    }
    
    # Adicionar barras para cada canal
    fig.add_trace(
        go.Bar(
            y=margem_canal['canal_venda'],
            x=margem_canal['margem_percentual'],
            orientation='h',
            name="Margem (%)",
            marker=dict(color=[cores.get(canal, '#F8F8FF') for canal in margem_canal['canal_venda']]),
            hovertemplate='<b>%{y}</b><br>Margem: %{x:.2f}%<br>Lucro: R$ %{customdata:,.2f}<extra></extra>',
            customdata=margem_canal['lucro'],
            text=margem_canal['margem_percentual'].apply(lambda x: f'{x:.2f}%'),
            textposition='inside'
        )
    )
    
    # Personalizar layout
    fig.update_layout(
        title={
            'text': "Margem de Lucro por Canal de Vendas",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(family="Orbitron", size=24, color="#F8F8FF")
        },
        paper_bgcolor='rgba(13, 13, 13, 0.0)',
        plot_bgcolor='rgba(13, 13, 13, 0.0)',
        margin=dict(l=20, r=20, t=80, b=20),
        height=400,
        xaxis=dict(
            title=dict(
                text="Margem (%)",
                font=dict(family="Montserrat", color="#F8F8FF")
            ),
            tickfont=dict(family="Montserrat", color="#F8F8FF"),
            showgrid=True,
            gridcolor='rgba(248, 248, 255, 0.1)',
            zeroline=False
        ),
        yaxis=dict(
            title=dict(
                text="Canal de Venda",
                font=dict(family="Montserrat", color="#F8F8FF")
            ),
            tickfont=dict(family="Montserrat", color="#F8F8FF"),
            showgrid=False,
            zeroline=False
        )
    )
    
    return fig, margem_canal

# Função para criar gráfico de ticket médio por categoria
def create_ticket_categoria_chart(vendas, filtro_periodo=None, filtro_categorias=None, filtro_canais=None):
    # Aplicar filtros se fornecidos
    df = vendas.copy()
    if filtro_periodo:
        data_inicio, data_fim = filtro_periodo
        df = df[(df['data_venda'] >= data_inicio) & (df['data_venda'] <= data_fim)]
    
    if filtro_categorias:
        df = df[df['categoria'].isin(filtro_categorias)]
    
    if filtro_canais:
        df = df[df['canal_venda'].isin(filtro_canais)]
    
    # Agrupar por categoria
    ticket_categoria = df.groupby('categoria').agg({
        'preco_venda': 'mean',
        'id_venda': 'count'
    }).reset_index()
    
    ticket_categoria.columns = ['categoria', 'ticket_medio', 'quantidade']
    
    # Ordenar por ticket médio
    ticket_categoria = ticket_categoria.sort_values('ticket_medio', ascending=False)
    
    # Criar gráfico de barras
    fig = go.Figure()
    
    # Cores para cada categoria
    cores = {
        'SUV': '#00FFFF',
        'Sedan': '#FF5F1F',
        'Hatch': '#F8F8FF',
        'Pickup': '#9933FF',
        'Elétrico': '#33FF99'
    }
    
    # Adicionar barras para cada categoria
    fig.add_trace(
        go.Bar(
            x=ticket_categoria['categoria'],
            y=ticket_categoria['ticket_medio'],
            name="Ticket Médio",
            marker=dict(color=[cores.get(cat, '#F8F8FF') for cat in ticket_categoria['categoria']]),
            hovertemplate='<b>%{x}</b><br>Ticket Médio: R$ %{y:,.2f}<br>Quantidade: %{customdata:,}<extra></extra>',
            customdata=ticket_categoria['quantidade'],
            text=ticket_categoria['ticket_medio'].apply(lambda x: f'R$ {x:,.2f}'),
            textposition='inside'
        )
    )
    
    # Personalizar layout
    fig.update_layout(
        title={
            'text': "Ticket Médio por Categoria",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(family="Orbitron", size=24, color="#F8F8FF")
        },
        paper_bgcolor='rgba(13, 13, 13, 0.0)',
        plot_bgcolor='rgba(13, 13, 13, 0.0)',
        margin=dict(l=20, r=20, t=80, b=20),
        height=400,
        xaxis=dict(
            title=dict(
                text="Categoria",
                font=dict(family="Montserrat", color="#F8F8FF")
            ),
            tickfont=dict(family="Montserrat", color="#F8F8FF"),
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title=dict(
                text="Ticket Médio (R$)",
                font=dict(family="Montserrat", color="#F8F8FF")
            ),
            tickfont=dict(family="Montserrat", color="#F8F8FF"),
            showgrid=True,
            gridcolor='rgba(248, 248, 255, 0.1)',
            zeroline=False
        )
    )
    
    return fig, ticket_categoria

# Função para criar gráfico de dispersão por hora
def create_scatter_chart(vendas, filtro_periodo=None, filtro_categorias=None, filtro_canais=None):
    # Aplicar filtros se fornecidos
    df = vendas.copy()
    if filtro_periodo:
        data_inicio, data_fim = filtro_periodo
        df = df[(df['data_venda'] >= data_inicio) & (df['data_venda'] <= data_fim)]
    
    if filtro_categorias:
        df = df[df['categoria'].isin(filtro_categorias)]
    
    if filtro_canais:
        df = df[df['canal_venda'].isin(filtro_canais)]
    
    # Agrupar por hora
    vendas_hora = df.groupby('hora').agg({
        'id_venda': 'count',
        'preco_venda': 'sum',
        'lucro': 'sum'
    }).reset_index()
    
    # Calcular margem
    vendas_hora['margem'] = (vendas_hora['lucro'] / vendas_hora['preco_venda']) * 100
    
    # Criar gráfico de dispersão
    fig = go.Figure()
    
    # Adicionar pontos
    fig.add_trace(
        go.Scatter(
            x=vendas_hora['hora'],
            y=vendas_hora['id_venda'],
            mode='markers+text',
            marker=dict(
                size=vendas_hora['id_venda'] / 10,
                color=vendas_hora['margem'],
                colorscale=[
                    [0, 'rgba(255, 95, 31, 0.7)'],
                    [0.5, 'rgba(248, 248, 255, 0.7)'],
                    [1, 'rgba(0, 255, 255, 0.7)']
                ],
                colorbar=dict(
                    title="Margem (%)",
                    titlefont=dict(family="Montserrat", color="#F8F8FF"),
                    tickfont=dict(family="Montserrat", color="#F8F8FF")
                ),
                line=dict(width=2, color='rgba(13, 13, 13, 0.7)')
            ),
            text=vendas_hora['id_venda'],
            textposition='top center',
            hovertemplate='<b>Hora:</b> %{x}:00<br><b>Vendas:</b> %{y}<br><b>Faturamento:</b> R$ %{customdata[0]:,.2f}<br><b>Margem:</b> %{customdata[1]:.2f}%<extra></extra>',
            customdata=np.column_stack((vendas_hora['preco_venda'], vendas_hora['margem']))
        )
    )
    
    # Adicionar linha de tendência
    fig.add_trace(
        go.Scatter(
            x=vendas_hora['hora'],
            y=vendas_hora['id_venda'],
            mode='lines',
            line=dict(color='rgba(248, 248, 255, 0.5)', width=2, dash='dot'),
            hoverinfo='skip',
            showlegend=False
        )
    )
    
    # Personalizar layout
    fig.update_layout(
        title={
            'text': "Análise de Vendas por Horário",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(family="Orbitron", size=24, color="#F8F8FF")
        },
        paper_bgcolor='rgba(13, 13, 13, 0.0)',
        plot_bgcolor='rgba(13, 13, 13, 0.0)',
        margin=dict(l=20, r=20, t=80, b=20),
        height=500,
        xaxis=dict(
            title=dict(
                text="Hora do Dia",
                font=dict(family="Montserrat", color="#F8F8FF")
            ),
            tickfont=dict(family="Montserrat", color="#F8F8FF"),
            showgrid=True,
            gridcolor='rgba(248, 248, 255, 0.1)',
            zeroline=False,
            tickmode='array',
            tickvals=list(range(0, 24)),
            ticktext=[f'{h}:00' for h in range(0, 24)]
        ),
        yaxis=dict(
            title=dict(
                text="Quantidade de Vendas",
                font=dict(family="Montserrat", color="#F8F8FF")
            ),
            tickfont=dict(family="Montserrat", color="#F8F8FF"),
            showgrid=True,
            gridcolor='rgba(248, 248, 255, 0.1)',
            zeroline=False
        )
    )
    
    return fig, vendas_hora

# Função para criar gráfico de linha para análise por dia da semana
def create_line_chart(vendas, filtro_periodo=None, filtro_categorias=None, filtro_canais=None):
    # Aplicar filtros se fornecidos
    df = vendas.copy()
    if filtro_periodo:
        data_inicio, data_fim = filtro_periodo
        df = df[(df['data_venda'] >= data_inicio) & (df['data_venda'] <= data_fim)]
    
    if filtro_categorias:
        df = df[df['categoria'].isin(filtro_categorias)]
    
    if filtro_canais:
        df = df[df['canal_venda'].isin(filtro_canais)]
    
    # Adicionar dia da semana
    df['dia_semana'] = df['data_venda'].dt.dayofweek
    df['dia_semana_nome'] = df['data_venda'].dt.day_name()
    
    # Mapeamento para nomes em português
    mapa_dias = {
        'Monday': 'Segunda-feira',
        'Tuesday': 'Terça-feira',
        'Wednesday': 'Quarta-feira',
        'Thursday': 'Quinta-feira',
        'Friday': 'Sexta-feira',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    
    df['dia_semana_nome'] = df['dia_semana_nome'].map(mapa_dias)
    
    # Agrupar por dia da semana
    vendas_dia = df.groupby(['dia_semana', 'dia_semana_nome']).agg({
        'id_venda': 'count',
        'preco_venda': 'sum',
        'lucro': 'sum'
    }).reset_index()
    
    # Ordenar por dia da semana
    vendas_dia = vendas_dia.sort_values('dia_semana')
    
    # Calcular margem
    vendas_dia['margem'] = (vendas_dia['lucro'] / vendas_dia['preco_venda']) * 100
    
    # Criar gráfico de linha
    fig = go.Figure()
    
    # Adicionar linha para quantidade de vendas
    fig.add_trace(
        go.Scatter(
            x=vendas_dia['dia_semana_nome'],
            y=vendas_dia['id_venda'],
            name="Quantidade de Vendas",
            line=dict(color="#00FFFF", width=3),
            mode='lines+markers+text',
            marker=dict(size=10, symbol='circle', color="#00FFFF"),
            text=vendas_dia['id_venda'],
            textposition='top center',
            hovertemplate='<b>%{x}</b><br>Vendas: %{y}<br>Faturamento: R$ %{customdata[0]:,.2f}<br>Margem: %{customdata[1]:.2f}%<extra></extra>',
            customdata=np.column_stack((vendas_dia['preco_venda'], vendas_dia['margem']))
        )
    )
    
    # Adicionar linha para margem
    fig.add_trace(
        go.Scatter(
            x=vendas_dia['dia_semana_nome'],
            y=vendas_dia['margem'],
            name="Margem (%)",
            line=dict(color="#FF5F1F", width=3, dash='dot'),
            mode='lines+markers+text',
            marker=dict(size=10, symbol='diamond', color="#FF5F1F"),
            text=vendas_dia['margem'].apply(lambda x: f'{x:.2f}%'),
            textposition='bottom center',
            yaxis="y2",
            hovertemplate='<b>%{x}</b><br>Margem: %{y:.2f}%<extra></extra>'
        )
    )
    
    # Personalizar layout
    fig.update_layout(
        title={
            'text': "Análise de Vendas por Dia da Semana",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(family="Orbitron", size=24, color="#F8F8FF")
        },
        paper_bgcolor='rgba(13, 13, 13, 0.0)',
        plot_bgcolor='rgba(13, 13, 13, 0.0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family="Montserrat", color="#F8F8FF")
        ),
        margin=dict(l=20, r=20, t=80, b=20),
        height=500,
        hovermode="x unified",
        xaxis=dict(
            title=dict(
                text="Dia da Semana",
                font=dict(family="Montserrat", color="#F8F8FF")
            ),
            tickfont=dict(family="Montserrat", color="#F8F8FF"),
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title=dict(
                text="Quantidade de Vendas",
                font=dict(family="Montserrat", color="#00FFFF")
            ),
            tickfont=dict(family="Montserrat", color="#00FFFF"),
            showgrid=True,
            gridcolor='rgba(0, 255, 255, 0.1)',
            zeroline=False
        ),
        yaxis2=dict(
            title=dict(
                text="Margem (%)",
                font=dict(family="Montserrat", color="#FF5F1F")
            ),
            tickfont=dict(family="Montserrat", color="#FF5F1F"),
            overlaying="y",
            side="right",
            showgrid=False,
            zeroline=False
        )
    )
    
    return fig, vendas_dia
