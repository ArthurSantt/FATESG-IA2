🎮 Análise de Dados — Steam Games

Projeto interdisciplinar de Ciência de Dados e Inteligência Artificial
Análise completa de 27.075 jogos da plataforma Steam


👥 Integrantes do Grupo

    1.Arthur Machado Santos 
    2.Guilherme Medeiro Nogueira

📁 Estrutura do Repositório
📦 steam-analysis/
├── 📄 steam.csv                  # Dataset original (SteamSpy / Kaggle)
├── 🐍 estatistica.py             # R1 — Estatística Descritiva
├── 🐍 dashboard.py               # R2 — Dashboard de Visualização
├── 🐍 machine_learning.py        # R3 — Modelagem Preditiva (ML)
├── 🖼️  dashboard.png              # Gráfico gerado pelo dashboard.py
├── 🖼️  matrizes_confusao.png      # Gráfico gerado pelo machine_learning.py
└── 📄 README.md                  # Este arquivo

📊 Sobre o Dataset
Fonte: Steam Games Dataset — Kaggle / SteamSpy
O dataset contém informações de 27.075 jogos publicados na plataforma Steam, coletadas via API do SteamSpy. Os dados abrangem características técnicas, comerciais e de engajamento dos jogos.
📋 Dicionário de Dados
ColunaTipoDescriçãoappidintIdentificador único do jogo na plataforma SteamnamestrNome do jogorelease_datestrData de lançamento (formato YYYY-MM-DD)englishintSuporte ao inglês (1 = sim, 0 = não)developerstrEmpresa ou pessoa responsável pelo desenvolvimentopublisherstrEmpresa responsável pela publicação/distribuiçãoplatformsstrPlataformas suportadas (windows, mac, linux)required_ageintClassificação etária mínima exigidacategoriesstrCategorias do jogo (Single-player, Multi-player, etc.)genresstrGêneros do jogo (Action, RPG, Strategy, etc.)steamspy_tagsstrTags atribuídas pela comunidade SteamachievementsintNúmero total de conquistas disponíveispositive_ratingsintQuantidade de avaliações positivas dos usuáriosnegative_ratingsintQuantidade de avaliações negativas dos usuáriosaverage_playtimeintTempo médio de jogo por usuário (em minutos)median_playtimeintTempo mediano de jogo por usuário (em minutos)ownersstrFaixa estimada de proprietários (ex.: '1000000-2000000')pricefloatPreço atual do jogo em dólares americanos (USD)approval_rate*floatTaxa de aprovação calculada: positive / (positive + negative) × 100

*Coluna calculada durante a análise, não presente no CSV original.


🗂️ Etapa 1 — R1: Estatística Descritiva
Arquivo: estatistica.py
Resumo Analítico
O projeto analisa o mercado de jogos digitais da plataforma Steam sob perspectivas de precificação, recepção da comunidade, engajamento dos jogadores e diversidade de gêneros. A grande variação nos valores das variáveis numéricas reflete a natureza heterogênea da plataforma, que reúne desde grandes produções (AAA) até jogos independentes (indie).
Variáveis Analisadas
Para cada variável abaixo foram calculados: média, mediana, moda, desvio padrão, variância, mínimo, máximo, Q1, Q2, Q3 e IQR, acompanhados de interpretação textual.
VariávelDescriçãopricePreço do jogo em USDpositive_ratingsTotal de avaliações positivasnegative_ratingsTotal de avaliações negativasaverage_playtimeTempo médio de jogo (minutos)achievementsNúmero de conquistas disponíveisapproval_rateTaxa de aprovação percentual
Principais Descobertas

O preço médio dos jogos é ~$6,08, mas a mediana é $3,99 — indicando que jogos muito caros distorcem a média
75% dos jogos custam menos de $7,19, mostrando que a maioria da biblioteca Steam é acessível
A taxa de aprovação média é ~70%, com mediana próxima, indicando boa recepção geral da comunidade
O tempo médio de jogo tem alta variância, refletindo a diversidade de gêneros da plataforma


📈 Etapa 2 — R2: Dashboard de Visualização
Arquivo: dashboard.py | Saída: dashboard.png
O dashboard foi desenvolvido com a biblioteca matplotlib e apresenta 3 gráficos distintos:
Gráfico 1 — Top 10 Gêneros Mais Populares
Gráfico de barras horizontais exibindo os gêneros com maior número de jogos na plataforma. Permite identificar quais categorias dominam o mercado Steam.
Gráfico 2 — Distribuição por Faixa de Preço
Gráfico de pizza segmentando os jogos em 5 faixas de preço: Gratuito, Até $5, $5–$15, $15–$30 e Acima de $30. Evidencia a forte presença de jogos acessíveis.
Gráfico 3 — Taxa de Aprovação por Faixa de Preço
Gráfico de barras verticais comparando a aprovação média dos jogos em cada faixa de preço, com linha de referência indicando a média geral. Permite analisar se jogos mais caros são melhor avaliados.

🤖 Etapa 2 — R3: Modelagem Preditiva (Machine Learning)
Arquivo: machine_learning.py | Saída: matrizes_confusao.png
Problema e Variável Alvo
Objetivo: Classificar se um jogo será bem avaliado (aprovação ≥ 75%) ou mal avaliado (< 75%).
Trata-se de um problema de classificação binária, pois a variável alvo assume dois valores: 1 (bem avaliado) e 0 (mal avaliado).
Features Utilizadas
price, achievements, average_playtime, median_playtime, required_age, tem_windows, tem_mac, tem_linux, genre_cod, is_free
Divisão dos Dados
ConjuntoProporçãoRegistrosTreino80%~21.600Teste20%~5.400

Algoritmo 1 — Random Forest Classifier
Justificativa: Algoritmo de ensemble baseado em múltiplas árvores de decisão. Escolhido por ser robusto a outliers (abundantes neste dataset), não exigir normalização, lidar bem com variáveis mistas e fornecer importância das features.
Configuração: 100 árvores (n_estimators=100), random_state=42
MétricaResultadoAcuráciaexecutar para verPrecisãoexecutar para verRecallexecutar para verF1-Scoreexecutar para ver

Algoritmo 2 — Regressão Logística
Justificativa: Algoritmo clássico de classificação binária, interpretável e rápido. Utilizado como modelo de comparação (baseline) em relação ao Random Forest. Exige normalização dos dados, realizada com StandardScaler.
Configuração: max_iter=1000, regularização L2, random_state=42
MétricaResultadoAcuráciaexecutar para verPrecisãoexecutar para verRecallexecutar para verF1-Scoreexecutar para ver

Comparação dos Algoritmos
MétricaRandom ForestRegressão LogísticaAcurácia——Precisão——Recall——F1-Score——

⚠️ Execute machine_learning.py para preencher os valores reais acima.

Conclusão: O Random Forest tende a superar a Regressão Logística em datasets com relações não-lineares e outliers — características presentes nos dados Steam. A Regressão Logística, apesar de menor acurácia esperada, oferece maior interpretabilidade e serve como baseline sólido.

▶️ Como Executar
Pré-requisitos
bashpip install pandas numpy matplotlib scikit-learn
Ordem de Execução
bash# 1. Estatística Descritiva (R1)
python estatistica.py

# 2. Dashboard de Visualização (R2)
python dashboard.py

# 3. Machine Learning (R3)
python machine_learning.py

⚠️ O arquivo steam.csv deve estar na mesma pasta que os scripts Python.


🛠️ Tecnologias Utilizadas
TecnologiaVersãoUsoPython3.xLinguagem principalPandas—Manipulação de dadosNumPy—Cálculos numéricosMatplotlib—Visualização (dashboard)Scikit-learn—Modelos de Machine Learning

📚 Referências

Dataset: Steam Store Games — Kaggle
Documentação Scikit-learn: scikit-learn.org
Documentação Pandas: pandas.pydata.org
SteamSpy API: steamspy.com/api.php