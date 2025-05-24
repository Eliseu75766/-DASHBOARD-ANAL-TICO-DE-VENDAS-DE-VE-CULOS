import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import re

def generate_advanced_insights(vendas, metas, modelos, filtro_periodo=None, filtro_categorias=None, filtro_canais=None):
    """
    Gera insights avançados com base nos dados de vendas, metas e modelos.
    """
    # Filtrar dados
    df_filtrado = vendas.copy()
    if filtro_periodo:
        data_inicio, data_fim = filtro_periodo
        df_filtrado = df_filtrado[(df_filtrado['data_venda'] >= data_inicio) & (df_filtrado['data_venda'] <= data_fim)]
    
    if filtro_categorias:
        df_filtrado = df_filtrado[df_filtrado['categoria'].isin(filtro_categorias)]
    
    if filtro_canais:
        df_filtrado = df_filtrado[df_filtrado['canal_venda'].isin(filtro_canais)]
    
    # Estrutura de dados para insights
    insights_data = {
        'resumo_geral': {},
        'categorias': {},
        'canais': {},
        'modelos': {},
        'periodos': {},
        'metas': {},
        'tendencias': {},
        'recomendacoes': {}
    }
    
    # Resumo geral
    insights_data['resumo_geral']['faturamento_total'] = df_filtrado['preco_venda'].sum()
    insights_data['resumo_geral']['total_vendas'] = len(df_filtrado)
    insights_data['resumo_geral']['lucro_total'] = df_filtrado['lucro'].sum()
    insights_data['resumo_geral']['margem_media'] = (insights_data['resumo_geral']['lucro_total'] / insights_data['resumo_geral']['faturamento_total']) * 100 if insights_data['resumo_geral']['faturamento_total'] > 0 else 0
    
    # Tendência de crescimento (últimos 3 períodos)
    faturamento_periodo = df_filtrado.groupby('periodo').agg({
        'preco_venda': 'sum'
    }).reset_index()
    
    if len(faturamento_periodo) >= 3:
        ultimos_periodos = faturamento_periodo.tail(3)
        insights_data['resumo_geral']['tendencia_crescimento'] = ultimos_periodos['preco_venda'].pct_change().mean() * 100
    else:
        insights_data['resumo_geral']['tendencia_crescimento'] = None
    
    # Análise por categoria
    categoria_stats = df_filtrado.groupby('categoria').agg({
        'id_venda': 'count',
        'preco_venda': 'sum',
        'lucro': 'sum'
    }).reset_index()
    
    categoria_stats['margem'] = (categoria_stats['lucro'] / categoria_stats['preco_venda']) * 100
    
    if not categoria_stats.empty:
        # Categoria mais lucrativa
        idx_mais_lucrativa = categoria_stats['lucro'].idxmax()
        insights_data['categorias']['mais_lucrativa'] = categoria_stats.iloc[idx_mais_lucrativa].to_dict()
        
        # Categoria com maior volume
        idx_maior_volume = categoria_stats['id_venda'].idxmax()
        insights_data['categorias']['maior_volume'] = categoria_stats.iloc[idx_maior_volume].to_dict()
        
        # Categoria com menor margem
        idx_menor_margem = categoria_stats['margem'].idxmin()
        insights_data['categorias']['menor_margem'] = categoria_stats.iloc[idx_menor_margem].to_dict()
    else:
        insights_data['categorias']['mais_lucrativa'] = None
        insights_data['categorias']['maior_volume'] = None
        insights_data['categorias']['menor_margem'] = None
    
    # Análise por canal
    canal_stats = df_filtrado.groupby('canal_venda').agg({
        'id_venda': 'count',
        'preco_venda': 'sum',
        'lucro': 'sum'
    }).reset_index()
    
    canal_stats['margem'] = (canal_stats['lucro'] / canal_stats['preco_venda']) * 100
    
    if not canal_stats.empty:
        # Canal mais lucrativo
        idx_mais_lucrativo = canal_stats['lucro'].idxmax()
        insights_data['canais']['mais_lucrativo'] = canal_stats.iloc[idx_mais_lucrativo].to_dict()
        
        # Canal com maior volume
        idx_maior_volume = canal_stats['id_venda'].idxmax()
        insights_data['canais']['maior_volume'] = canal_stats.iloc[idx_maior_volume].to_dict()
        
        # Canal com menor margem
        idx_menor_margem = canal_stats['margem'].idxmin()
        insights_data['canais']['menor_margem'] = canal_stats.iloc[idx_menor_margem].to_dict()
    else:
        insights_data['canais']['mais_lucrativo'] = None
        insights_data['canais']['maior_volume'] = None
        insights_data['canais']['menor_margem'] = None
    
    # Análise por modelo
    modelo_stats = df_filtrado.groupby('modelo').agg({
        'id_venda': 'count',
        'preco_venda': 'sum',
        'lucro': 'sum'
    }).reset_index()
    
    modelo_stats['margem'] = (modelo_stats['lucro'] / modelo_stats['preco_venda']) * 100
    modelo_stats['ticket_medio'] = modelo_stats['preco_venda'] / modelo_stats['id_venda']
    
    if not modelo_stats.empty:
        # Modelo mais vendido
        idx_mais_vendido = modelo_stats['id_venda'].idxmax()
        insights_data['modelos']['mais_vendido'] = modelo_stats.iloc[idx_mais_vendido].to_dict()
        
        # Modelo mais lucrativo
        idx_mais_lucrativo = modelo_stats['lucro'].idxmax()
        insights_data['modelos']['mais_lucrativo'] = modelo_stats.iloc[idx_mais_lucrativo].to_dict()
        
        # Modelo com maior ticket
        idx_maior_ticket = modelo_stats['ticket_medio'].idxmax()
        insights_data['modelos']['maior_ticket'] = modelo_stats.iloc[idx_maior_ticket].to_dict()
    else:
        insights_data['modelos']['mais_vendido'] = None
        insights_data['modelos']['mais_lucrativo'] = None
        insights_data['modelos']['maior_ticket'] = None
    
    # Análise por período
    periodo_stats = df_filtrado.groupby('periodo').agg({
        'id_venda': 'count',
        'preco_venda': 'sum',
        'lucro': 'sum'
    }).reset_index()
    
    periodo_stats['margem'] = (periodo_stats['lucro'] / periodo_stats['preco_venda']) * 100
    
    if not periodo_stats.empty:
        # Último período
        ultimo_periodo = periodo_stats.iloc[-1].to_dict()
        insights_data['periodos']['ultimo'] = ultimo_periodo
        
        # Melhor período em faturamento
        idx_melhor_faturamento = periodo_stats['preco_venda'].idxmax()
        insights_data['periodos']['melhor_faturamento'] = periodo_stats.iloc[idx_melhor_faturamento].to_dict()
        
        # Pior período em faturamento
        idx_pior_faturamento = periodo_stats['preco_venda'].idxmin()
        insights_data['periodos']['pior_faturamento'] = periodo_stats.iloc[idx_pior_faturamento].to_dict()
    else:
        insights_data['periodos']['ultimo'] = None
        insights_data['periodos']['melhor_faturamento'] = None
        insights_data['periodos']['pior_faturamento'] = None
    
    # Análise de metas
    metas_filtradas = metas.copy()
    if filtro_periodo:
        data_inicio, data_fim = filtro_periodo
        # Converter datas para strings no formato 'YYYY-MM' para comparar com o período
        data_inicio_str = data_inicio.strftime('%Y-%m')
        data_fim_str = data_fim.strftime('%Y-%m')
        # Filtrar metas por período
        metas_filtradas = metas_filtradas[(metas_filtradas['periodo'] >= data_inicio_str) & (metas_filtradas['periodo'] <= data_fim_str)]
    
    # Juntar metas com faturamento
    if not periodo_stats.empty and not metas_filtradas.empty:
        metas_periodo = metas_filtradas.groupby('periodo').agg({
            'meta_faturamento': 'sum'
        }).reset_index()
        
        # Juntar com faturamento
        metas_faturamento = pd.merge(periodo_stats, metas_periodo, on='periodo', how='left')
        metas_faturamento['atingimento'] = (metas_faturamento['preco_venda'] / metas_faturamento['meta_faturamento']) * 100
        
        # Atingimento médio
        insights_data['metas']['atingimento_medio'] = metas_faturamento['atingimento'].mean()
        
        # Último atingimento
        insights_data['metas']['ultimo_atingimento'] = metas_faturamento.iloc[-1]['atingimento'] if len(metas_faturamento) > 0 else None
        
        # Melhor atingimento
        idx_melhor_atingimento = metas_faturamento['atingimento'].idxmax()
        insights_data['metas']['melhor_atingimento'] = metas_faturamento.iloc[idx_melhor_atingimento].to_dict()
        
        # Pior atingimento
        idx_pior_atingimento = metas_faturamento['atingimento'].idxmin()
        insights_data['metas']['pior_atingimento'] = metas_faturamento.iloc[idx_pior_atingimento].to_dict()
    else:
        insights_data['metas']['atingimento_medio'] = None
        insights_data['metas']['ultimo_atingimento'] = None
        insights_data['metas']['melhor_atingimento'] = None
        insights_data['metas']['pior_atingimento'] = None
    
    # Análise de tendências
    if len(periodo_stats) >= 3:
        # Tendência de faturamento
        tendencia_faturamento = periodo_stats['preco_venda'].pct_change().mean() * 100
        insights_data['tendencias']['faturamento'] = tendencia_faturamento
        
        # Tendência de volume
        tendencia_volume = periodo_stats['id_venda'].pct_change().mean() * 100
        insights_data['tendencias']['volume'] = tendencia_volume
        
        # Tendência de margem
        tendencia_margem = periodo_stats['margem'].pct_change().mean() * 100
        insights_data['tendencias']['margem'] = tendencia_margem
    else:
        insights_data['tendencias']['faturamento'] = None
        insights_data['tendencias']['volume'] = None
        insights_data['tendencias']['margem'] = None
    
    # Análise por dia da semana
    df_filtrado['dia_semana'] = df_filtrado['data_venda'].dt.dayofweek
    df_filtrado['dia_semana_nome'] = df_filtrado['data_venda'].dt.day_name()
    
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
    
    df_filtrado['dia_semana_nome'] = df_filtrado['dia_semana_nome'].map(mapa_dias)
    
    dia_stats = df_filtrado.groupby('dia_semana_nome').agg({
        'id_venda': 'count',
        'preco_venda': 'sum',
        'lucro': 'sum'
    }).reset_index()
    
    if not dia_stats.empty:
        # Dia com maior volume
        idx_maior_volume = dia_stats['id_venda'].idxmax()
        insights_data['tendencias']['dia_maior_volume'] = dia_stats.iloc[idx_maior_volume].to_dict()
        
        # Dia com menor volume
        idx_menor_volume = dia_stats['id_venda'].idxmin()
        insights_data['tendencias']['dia_menor_volume'] = dia_stats.iloc[idx_menor_volume].to_dict()
    else:
        insights_data['tendencias']['dia_maior_volume'] = None
        insights_data['tendencias']['dia_menor_volume'] = None
    
    # Análise por hora
    hora_stats = df_filtrado.groupby('hora').agg({
        'id_venda': 'count',
        'preco_venda': 'sum',
        'lucro': 'sum'
    }).reset_index()
    
    if not hora_stats.empty:
        # Hora com maior volume
        idx_maior_volume = hora_stats['id_venda'].idxmax()
        insights_data['tendencias']['hora_maior_volume'] = hora_stats.iloc[idx_maior_volume].to_dict()
        
        # Hora com menor volume
        idx_menor_volume = hora_stats['id_venda'].idxmin()
        insights_data['tendencias']['hora_menor_volume'] = hora_stats.iloc[idx_menor_volume].to_dict()
    else:
        insights_data['tendencias']['hora_maior_volume'] = None
        insights_data['tendencias']['hora_menor_volume'] = None
    
    return insights_data

def generate_narrative(insights_data):
    """
    Gera uma narrativa em linguagem natural com base nos insights.
    """
    narrativa = "<div class=\"insight-content\">\n"
    narrativa += "<span class=\"insight-subtitle\">Panorama Geral</span>\n"
    
    # Resumo geral
    faturamento_total = insights_data['resumo_geral']['faturamento_total']
    total_vendas = insights_data['resumo_geral']['total_vendas']
    margem_media = insights_data['resumo_geral']['margem_media']
    tendencia_crescimento = insights_data['resumo_geral']['tendencia_crescimento']
    
    narrativa += "<p>O período analisado registrou um faturamento total de <span class=\"highlight-positive\">R$ {0:,.2f}</span>, ".format(faturamento_total)
    narrativa += "com <span class=\"highlight-positive\">{0:,}</span> veículos vendidos e margem média de <span class=\"highlight-positive\">{1:.2f}%</span>.</p>\n".format(total_vendas, margem_media)
    
    if tendencia_crescimento is not None:
        direcao = "crescimento" if tendencia_crescimento > 0 else "queda"
        highlight_class = "highlight-positive" if tendencia_crescimento > 0 else "highlight-negative"
        narrativa += "<p>A análise dos últimos períodos indica uma tendência de <span class=\"{0}\">{1} de {2:.1f}%</span> no faturamento.</p>\n".format(
            highlight_class, direcao, abs(tendencia_crescimento)
        )
    
    # Categorias
    if insights_data['categorias']['mais_lucrativa'] is not None:
        categoria_mais_lucrativa = insights_data['categorias']['mais_lucrativa']['categoria']
        lucro_mais_lucrativa = insights_data['categorias']['mais_lucrativa']['lucro']
        margem_mais_lucrativa = insights_data['categorias']['mais_lucrativa']['margem']
        
        categoria_maior_volume = insights_data['categorias']['maior_volume']['categoria']
        volume_maior = insights_data['categorias']['maior_volume']['id_venda']
        
        categoria_menor_margem = insights_data['categorias']['menor_margem']['categoria']
        margem_menor = insights_data['categorias']['menor_margem']['margem']
        
        narrativa += "\n<span class=\"insight-subtitle\">Análise por Categoria</span>\n"
        
        narrativa += "<p>A categoria <span class=\"highlight-positive\">{0}</span> destaca-se como a mais lucrativa, ".format(categoria_mais_lucrativa)
        narrativa += "gerando <span class=\"highlight-positive\">R$ {0:,.2f}</span> de lucro com margem de <span class=\"highlight-positive\">{1:.2f}%</span>.</p>\n".format(
            lucro_mais_lucrativa, margem_mais_lucrativa
        )
        
        narrativa += "<p>Em volume de vendas, <span class=\"highlight-positive\">{0}</span> lidera com <span class=\"highlight-positive\">{1:,}</span> unidades vendidas.</p>\n".format(
            categoria_maior_volume, volume_maior
        )
        
        narrativa += "<p>A categoria <span class=\"highlight-negative\">{0}</span> apresenta a menor margem de lucro, com <span class=\"highlight-negative\">{1:.2f}%</span>, ".format(
            categoria_menor_margem, margem_menor
        )
        narrativa += "indicando oportunidade para revisão de custos ou estratégia de precificação.</p>\n"
    
    # Canais
    if insights_data['canais']['mais_lucrativo'] is not None:
        canal_mais_lucrativo = insights_data['canais']['mais_lucrativo']['canal_venda']
        lucro_canal = insights_data['canais']['mais_lucrativo']['lucro']
        
        canal_maior_volume = insights_data['canais']['maior_volume']['canal_venda']
        volume_canal = insights_data['canais']['maior_volume']['id_venda']
        
        narrativa += "\n<span class=\"insight-subtitle\">Canais de Venda</span>\n"
        
        narrativa += "<p>O canal <span class=\"highlight-positive\">{0}</span> apresenta o melhor desempenho em lucratividade, ".format(canal_mais_lucrativo)
        narrativa += "com <span class=\"highlight-positive\">R$ {0:,.2f}</span> de lucro gerado.</p>\n".format(lucro_canal)
        
        narrativa += "<p>Em volume, o canal <span class=\"highlight-positive\">{0}</span> lidera com <span class=\"highlight-positive\">{1:,}</span> unidades vendidas.</p>\n".format(
            canal_maior_volume, volume_canal
        )
    
    # Modelos
    if insights_data['modelos']['mais_vendido'] is not None:
        modelo_mais_vendido = insights_data['modelos']['mais_vendido']['modelo']
        qtd_mais_vendido = insights_data['modelos']['mais_vendido']['id_venda']
        
        modelo_mais_lucrativo = insights_data['modelos']['mais_lucrativo']['modelo']
        lucro_mais_lucrativo = insights_data['modelos']['mais_lucrativo']['lucro']
        
        modelo_maior_ticket = insights_data['modelos']['maior_ticket']['modelo']
        ticket_maior = insights_data['modelos']['maior_ticket']['ticket_medio']
        
        narrativa += "\n<span class=\"insight-subtitle\">Desempenho por Modelo</span>\n"
        
        narrativa += "<p>O <span class=\"highlight-positive\">{0}</span> é o modelo mais vendido, com <span class=\"highlight-positive\">{1:,}</span> unidades.</p>\n".format(
            modelo_mais_vendido, qtd_mais_vendido
        )
        
        narrativa += "<p>Em termos de lucratividade, o <span class=\"highlight-positive\">{0}</span> destaca-se com <span class=\"highlight-positive\">R$ {1:,.2f}</span> de lucro.</p>\n".format(
            modelo_mais_lucrativo, lucro_mais_lucrativo
        )
        
        narrativa += "<p>O <span class=\"highlight-positive\">{0}</span> apresenta o maior ticket médio, com <span class=\"highlight-positive\">R$ {1:,.2f}</span> por unidade.</p>\n".format(
            modelo_maior_ticket, ticket_maior
        )
    
    # Metas
    if insights_data['metas']['atingimento_medio'] is not None:
        atingimento_medio = insights_data['metas']['atingimento_medio']
        ultimo_atingimento = insights_data['metas']['ultimo_atingimento']
        
        narrativa += "\n<span class=\"insight-subtitle\">Atingimento de Metas</span>\n"
        
        highlight_class_medio = "highlight-positive" if atingimento_medio >= 100 else "highlight-negative"
        status_medio = "acima" if atingimento_medio >= 100 else "abaixo"
        
        narrativa += "<p>O atingimento médio de metas no período foi de <span class=\"{0}\">{1:.1f}%</span>, ficando {2} da meta estabelecida.</p>\n".format(
            highlight_class_medio, atingimento_medio, status_medio
        )
        
        if ultimo_atingimento is not None:
            highlight_class_ultimo = "highlight-positive" if ultimo_atingimento >= 100 else "highlight-negative"
            status_ultimo = "acima" if ultimo_atingimento >= 100 else "abaixo"
            
            narrativa += "<p>No último período, o atingimento foi de <span class=\"{0}\">{1:.1f}%</span>, ficando {2} da meta estabelecida.</p>\n".format(
                highlight_class_ultimo, ultimo_atingimento, status_ultimo
            )
    
    # Padrões temporais
    if insights_data['tendencias']['dia_maior_volume'] is not None and insights_data['tendencias']['hora_maior_volume'] is not None:
        dia_maior_volume = insights_data['tendencias']['dia_maior_volume']['dia_semana_nome']
        qtd_dia_maior = insights_data['tendencias']['dia_maior_volume']['id_venda']
        
        hora_maior_volume = insights_data['tendencias']['hora_maior_volume']['hora']
        qtd_hora_maior = insights_data['tendencias']['hora_maior_volume']['id_venda']
        
        narrativa += "\n<span class=\"insight-subtitle\">Padrões Temporais</span>\n"
        
        narrativa += "<p><span class=\"highlight-positive\">{0}</span> é o dia da semana com maior volume de vendas, registrando <span class=\"highlight-positive\">{1:,}</span> unidades.</p>\n".format(
            dia_maior_volume, qtd_dia_maior
        )
        
        narrativa += "<p>O horário de pico ocorre às <span class=\"highlight-positive\">{0}h</span>, com <span class=\"highlight-positive\">{1}</span> vendas registradas.</p>\n".format(
            hora_maior_volume, qtd_hora_maior
        )
    
    narrativa += "</div>"
    
    return narrativa

def generate_ticket_insights(vendas, filtro_periodo=None, filtro_categorias=None, filtro_canais=None):
    """
    Gera insights específicos sobre o ticket médio.
    """
    # Aplicar filtros se fornecidos
    df = vendas.copy()
    if filtro_periodo:
        data_inicio, data_fim = filtro_periodo
        df = df[(df['data_venda'] >= data_inicio) & (df['data_venda'] <= data_fim)]
    
    if filtro_categorias:
        df = df[df['categoria'].isin(filtro_categorias)]
    
    if filtro_canais:
        df = df[df['canal_venda'].isin(filtro_canais)]
    
    # Calcular ticket médio atual
    ticket_medio_atual = df['preco_venda'].mean()
    
    # Calcular ticket médio por período
    ticket_periodo = df.groupby('periodo').agg({
        'preco_venda': 'mean'
    }).reset_index()
    
    ticket_periodo.columns = ['periodo', 'ticket_medio']
    
    # Calcular variação em relação ao período anterior
    if len(ticket_periodo) >= 2:
        ultimo_ticket = ticket_periodo.iloc[-1]['ticket_medio']
        penultimo_ticket = ticket_periodo.iloc[-2]['ticket_medio']
        
        variacao_percentual = ((ultimo_ticket - penultimo_ticket) / penultimo_ticket) * 100
    else:
        variacao_percentual = 0
    
    # Calcular ticket médio por categoria
    ticket_categoria = df.groupby('categoria').agg({
        'preco_venda': 'mean'
    }).reset_index()
    
    ticket_categoria.columns = ['categoria', 'ticket_medio']
    
    # Identificar categoria com maior e menor ticket
    if not ticket_categoria.empty:
        idx_maior_ticket = ticket_categoria['ticket_medio'].idxmax()
        categoria_maior_ticket = ticket_categoria.iloc[idx_maior_ticket]['categoria']
        valor_maior_ticket = ticket_categoria.iloc[idx_maior_ticket]['ticket_medio']
        
        idx_menor_ticket = ticket_categoria['ticket_medio'].idxmin()
        categoria_menor_ticket = ticket_categoria.iloc[idx_menor_ticket]['categoria']
        valor_menor_ticket = ticket_categoria.iloc[idx_menor_ticket]['ticket_medio']
    else:
        categoria_maior_ticket = None
        valor_maior_ticket = 0
        categoria_menor_ticket = None
        valor_menor_ticket = 0
    
    # Gerar texto de insights
    insights = "<p>O ticket médio atual é de R$ {0:,.2f}, representando uma {1} de {2:.2f}% em relação ao período anterior.</p>\n".format(
        ticket_medio_atual,
        "alta" if variacao_percentual >= 0 else "queda",
        abs(variacao_percentual)
    )
    
    if categoria_maior_ticket and categoria_menor_ticket:
        insights += "<p>A categoria <span class=\"highlight-positive\">{0}</span> apresenta o maior ticket médio com <span class=\"highlight-positive\">R$ {1:,.2f}</span>, ".format(
            categoria_maior_ticket, valor_maior_ticket
        )
        insights += "enquanto <span class=\"highlight-negative\">{0}</span> registra o menor com <span class=\"highlight-negative\">R$ {1:,.2f}</span>.</p>\n".format(
            categoria_menor_ticket, valor_menor_ticket
        )
    
    return insights

def generate_strategic_recommendations(insights_data):
    """
    Gera recomendações estratégicas com base nos insights.
    """
    recomendacoes = "<div class=\"recommendations-content\">\n"
    
    # Recomendações para categorias
    if insights_data['categorias']['mais_lucrativa'] is not None:
        categoria_mais_lucrativa = insights_data['categorias']['mais_lucrativa']['categoria']
        categoria_menor_margem = insights_data['categorias']['menor_margem']['categoria']
        
        recomendacoes += "<span class=\"recommendation-title\">Estratégias para Categorias</span>\n"
        
        recomendacoes += "<p>Potencialize o desempenho da categoria <span class=\"highlight-positive\">{0}</span> com campanhas direcionadas e aumento de estoque, aproveitando sua alta lucratividade.</p>\n".format(categoria_mais_lucrativa)
        
        recomendacoes += "<p>Implemente uma revisão de custos e precificação para a categoria <span class=\"highlight-negative\">{0}</span>, buscando melhorar sua margem de contribuição.</p>\n".format(categoria_menor_margem)
    
    # Recomendações para canais
    if insights_data['canais']['mais_lucrativo'] is not None:
        canal_mais_lucrativo = insights_data['canais']['mais_lucrativo']['canal_venda']
        
        recomendacoes += "\n<span class=\"recommendation-title\">Otimização de Canais</span>\n"
        
        recomendacoes += "<p>Amplie os investimentos no canal <span class=\"highlight-positive\">{0}</span>, que demonstra o melhor desempenho em lucratividade.</p>\n".format(canal_mais_lucrativo)
        
        recomendacoes += "<p>Desenvolva estratégias de cross-selling e up-selling em todos os canais para aumentar o ticket médio e a rentabilidade geral.</p>\n"
    
    # Recomendações para modelos
    if insights_data['modelos']['mais_vendido'] is not None:
        modelo_mais_vendido = insights_data['modelos']['mais_vendido']['modelo']
        modelo_maior_ticket = insights_data['modelos']['maior_ticket']['modelo']
        
        recomendacoes += "\n<span class=\"recommendation-title\">Gestão de Portfólio</span>\n"
        
        recomendacoes += "<p>Garanta disponibilidade contínua do modelo <span class=\"highlight-positive\">{0}</span>, líder em volume de vendas, evitando rupturas de estoque.</p>\n".format(modelo_mais_vendido)
        
        recomendacoes += "<p>Crie pacotes promocionais combinando o modelo <span class=\"highlight-positive\">{0}</span> com acessórios premium para maximizar o valor do ticket alto.</p>\n".format(modelo_maior_ticket)
    
    # Recomendações para metas
    if insights_data['metas']['atingimento_medio'] is not None:
        atingimento_medio = insights_data['metas']['atingimento_medio']
        
        recomendacoes += "\n<span class=\"recommendation-title\">Gestão de Metas</span>\n"
        
        if atingimento_medio < 90:
            recomendacoes += "<p>Revise as metas estabelecidas considerando o atingimento atual de <span class=\"highlight-negative\">{0:.1f}%</span>, ajustando-as para patamares mais realistas ou implementando ações corretivas imediatas.</p>\n".format(atingimento_medio)
        elif atingimento_medio >= 90 and atingimento_medio < 100:
            recomendacoes += "<p>Intensifique as ações comerciais para superar o gap de <span class=\"highlight-negative\">{0:.1f}%</span> no atingimento das metas, com foco nos produtos e canais de maior potencial.</p>\n".format(100 - atingimento_medio)
        else:
            recomendacoes += "<p>Avalie a possibilidade de estabelecer metas mais desafiadoras para o próximo período, considerando o excelente atingimento atual de <span class=\"highlight-positive\">{0:.1f}%</span>.</p>\n".format(atingimento_medio)
    
    # Recomendações para padrões temporais
    if insights_data['tendencias']['dia_maior_volume'] is not None and insights_data['tendencias']['hora_maior_volume'] is not None:
        dia_maior_volume = insights_data['tendencias']['dia_maior_volume']['dia_semana_nome']
        hora_maior_volume = insights_data['tendencias']['hora_maior_volume']['hora']
        
        recomendacoes += "\n<span class=\"recommendation-title\">Otimização Temporal</span>\n"
        
        recomendacoes += "<p>Reforce a equipe de vendas e atendimento às <span class=\"highlight-positive\">{0}h</span> e nos dias de <span class=\"highlight-positive\">{1}</span>, períodos de maior movimento.</p>\n".format(
            hora_maior_volume, dia_maior_volume
        )
        
        recomendacoes += "<p>Desenvolva promoções específicas para horários e dias de menor movimento, equilibrando o fluxo de vendas ao longo da semana.</p>\n"
    
    recomendacoes += "</div>"
    
    return recomendacoes
