# Dashboard Analítico de Vendas de Veículos - Versão Aprimorada

Este repositório contém um dashboard analítico interativo e visualmente futurista desenvolvido com Streamlit, focado em data storytelling para vendas de veículos em uma concessionária.

## 🚀 Principais Recursos

- **Interface Futurista**: Design sci-fi com paleta de cores neon (preto, laranja neon, azul elétrico e branco)
- **Visualizações Interativas**: Gráficos dinâmicos e responsivos usando Plotly
- **Motor de IA Avançado**: Geração de insights, respostas a perguntas e recomendações estratégicas
- **Análises Detalhadas**: Faturamento, margem de lucro, ticket médio, análise mensal e por horário
- **Filtros Dinâmicos**: Período, categorias e canais de venda
- **Exportação de Dados**: Download de dados em formato CSV

## 📊 Seções do Dashboard

1. **Análise de Faturamento**: Gráficos de linha e área com comparativo mês a mês e destaques automáticos
2. **Margem de Lucro**: Barras empilhadas com margens por categoria e canal
3. **Ticket Médio**: Velocímetros neon e evolução temporal
4. **Análise Mensal**: Heatmap interativo com drill-down por modelo
5. **Análise por Horário**: Gráfico de dispersão animado e padrões por dia da semana
6. **IA Insights**: Análise inteligente com insights automáticos, perguntas & respostas e recomendações estratégicas

## 🧠 Recursos de IA

- **Insights Automáticos**: Análises geradas automaticamente para cada seção
- **Perguntas & Respostas**: Interface conversacional para consultas sobre os dados
- **Recomendações Estratégicas**: Sugestões de ações baseadas na análise dos dados

## 🛠️ Requisitos

- Python 3.9+
- Streamlit 1.45.1+
- Pandas 2.2.0+
- Plotly 5.18.0+
- NumPy 1.26.0+

## 📦 Instalação

1. Clone este repositório:
```bash
git clone https://github.com/seu-usuario/dashboard-veiculos.git
cd dashboard-veiculos
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o dashboard:
```bash
streamlit run app_aprimorado.py
```

## 📁 Estrutura do Projeto

```
dashboard_veiculos/
├── app_aprimorado.py        # Aplicação principal aprimorada
├── data/                    # Dados em formato CSV
│   ├── vendas.csv           # Dados de vendas
│   ├── metas.csv            # Metas de faturamento
│   └── modelos.csv          # Informações dos modelos
├── assets/                  # Recursos estáticos
│   └── css/                 # Estilos CSS
│       └── style.css        # Estilo personalizado
├── utils/                   # Módulos utilitários
│   ├── chart_factory.py     # Funções para criação de gráficos
│   └── ai_insights.py       # Motor de IA para insights
└── requirements.txt         # Dependências do projeto
```

## 🆕 Melhorias na Versão Atual

- **Motor de IA Aprimorado**: Capacidade avançada de responder perguntas diretas sobre os dados
- **Insights Contextuais**: Análises mais profundas e personalizadas baseadas nos dados filtrados
- **Design Mais Interativo**: Microinterações, animações e elementos visuais aprimorados
- **Visualizações Enriquecidas**: Novos tipos de gráficos e análises mais detalhadas
- **Dados Atualizados**: Todos os dados atualizados para 2024/2025
- **Recomendações Estratégicas**: Sugestões de ações baseadas em análise avançada dos dados

## 📱 Responsividade

O dashboard é totalmente responsivo e pode ser acessado em dispositivos móveis e desktops.

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.
