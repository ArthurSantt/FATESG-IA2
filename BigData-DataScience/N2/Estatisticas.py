
#  R1 — Coleta e Estatística Descritiva
#  Dataset: Steam Games (27.075 jogos)
#  Fonte: Kaggle / SteamSpy
 
import pandas as pd
import numpy as np
 

# 1. Carregamento e Limpeza dos Dados

df = pd.read_csv("steam.csv")
 
print("=" * 60)
print("  ANÁLISE ESTATÍSTICA — DATASET STEAM GAMES")
print("=" * 60)
 
print(f"\n📦 Total de jogos no dataset: {df.shape[0]}")
print(f"📋 Total de colunas: {df.shape[1]}")
print(f"\n🔎 Colunas: {df.columns.tolist()}")
 
df.dropna(subset=["developer", "publisher"], inplace=True)
print(f"\n✅ Registros após limpeza: {df.shape[0]}")
 
df["approval_rate"] = (
    df["positive_ratings"] / (df["positive_ratings"] + df["negative_ratings"])
).replace([float("inf"), float("nan")], 0) * 100
 

# 2. Documentacao das Colunas

print("\n" + "=" * 60)
print("  DOCUMENTAÇÃO DAS COLUNAS")
print("=" * 60)
 
colunas = {
    "appid":             "Identificador único do jogo na plataforma Steam.",
    "name":              "Nome do jogo.",
    "release_date":      "Data de lançamento do jogo (formato YYYY-MM-DD).",
    "english":           "Indica se o jogo possui suporte ao idioma inglês (1 = sim, 0 = não).",
    "developer":         "Nome da empresa ou pessoa responsável pelo desenvolvimento.",
    "publisher":         "Nome da empresa responsável pela publicação/distribuição.",
    "platforms":         "Plataformas suportadas (windows, mac, linux), separadas por ponto e vírgula.",
    "required_age":      "Classificação etária mínima exigida para jogar.",
    "categories":        "Categorias do jogo (ex.: Single-player, Multi-player, Co-op).",
    "genres":            "Gêneros do jogo (ex.: Action, RPG, Strategy).",
    "steamspy_tags":     "Tags atribuídas pela comunidade Steam para descrever o jogo.",
    "achievements":      "Número total de conquistas (achievements) disponíveis no jogo.",
    "positive_ratings":  "Quantidade de avaliações positivas recebidas pelos usuários.",
    "negative_ratings":  "Quantidade de avaliações negativas recebidas pelos usuários.",
    "average_playtime":  "Tempo médio de jogo por usuário (em minutos).",
    "median_playtime":   "Tempo mediano de jogo por usuário (em minutos).",
    "owners":            "Faixa estimada de proprietários do jogo (ex.: '1000000-2000000').",
    "price":             "Preço atual do jogo em dólares americanos (USD).",
    "approval_rate":     "Taxa de aprovação calculada: positive / (positive + negative) × 100.",
}
 
for col, desc in colunas.items():
    print(f"\n  • {col}: {desc}")
 

# 3. Variaveis Analisadas

variaveis = {
    "price":            "Preço (USD)",
    "positive_ratings": "Avaliações Positivas",
    "negative_ratings": "Avaliações Negativas",
    "average_playtime": "Tempo Médio de Jogo (min)",
    "achievements":     "Número de Conquistas",
    "approval_rate":    "Taxa de Aprovação (%)",
}
 

# 4. Estatistica Descritiva com Interpretacao

print("\n\n" + "=" * 60)
print("  ESTATÍSTICA DESCRITIVA COMPLETA")
print("=" * 60)
 
for col, label in variaveis.items():
    serie = df[col]
 
    media     = serie.mean()
    mediana   = serie.median()
    moda      = serie.mode().iloc[0]
    desvio    = serie.std()
    variancia = serie.var()
    minimo    = serie.min()
    maximo    = serie.max()
    q1        = serie.quantile(0.25)
    q2        = serie.quantile(0.50)
    q3        = serie.quantile(0.75)
    iqr       = q3 - q1
 
    print(f"\n{'─' * 60}")
    print(f"  📊 {label.upper()}")
    print(f"{'─' * 60}")
    print(f"  Média:           {media:>14.2f}")
    print(f"  Mediana:         {mediana:>14.2f}")
    print(f"  Moda:            {moda:>14.2f}")
    print(f"  Desvio Padrão:   {desvio:>14.2f}")
    print(f"  Variância:       {variancia:>14.2f}")
    print(f"  Mínimo:          {minimo:>14.2f}")
    print(f"  Máximo:          {maximo:>14.2f}")
    print(f"  Q1 (25%):        {q1:>14.2f}")
    print(f"  Q2 (50%):        {q2:>14.2f}")
    print(f"  Q3 (75%):        {q3:>14.2f}")
    print(f"  IQR (Q3 - Q1):   {iqr:>14.2f}")
 

    print(f"\n  📝 Interpretação:")
 
    if col == "price":
        print(
            f"  O preço médio dos jogos na Steam é de ${media:.2f}, com mediana de "
            f"${mediana:.2f}. A diferença entre média e mediana indica que jogos "
            f"muito caros (máximo ${maximo:.2f}) elevam a média. A moda de ${moda:.2f} "
            f"é o preço mais comum na plataforma. O desvio padrão de ${desvio:.2f} "
            f"revela grande variação nos preços. 75%% dos jogos custam menos de "
            f"${q3:.2f}, demonstrando que a maioria da biblioteca Steam é acessível."
        )
 
    elif col == "positive_ratings":
        print(
            f"  A média de {media:.0f} avaliações positivas por jogo é fortemente "
            f"influenciada por títulos blockbuster com milhões de reviews. A mediana "
            f"de apenas {mediana:.0f} mostra que a maioria dos jogos recebe poucas "
            f"avaliações — há forte concentração em poucos títulos populares. O valor "
            f"máximo de {maximo:.0f} pertence a jogos extremamente populares como "
            f"CS:GO ou Dota 2. O IQR de {iqr:.0f} indica que 50%% dos jogos ficam "
            f"em uma faixa bastante estreita de avaliações."
        )
 
    elif col == "negative_ratings":
        print(
            f"  A média de {media:.0f} avaliações negativas é bem menor que as "
            f"positivas, o que indica que os jogos tendem a receber mais elogios "
            f"do que críticas. A mediana de {mediana:.0f} reforça que a maioria "
            f"dos jogos tem poucas avaliações negativas. O máximo de {maximo:.0f} "
            f"pertence a jogos polêmicos. O desvio padrão de {desvio:.0f} demonstra "
            f"grande dispersão, com alguns títulos concentrando quase toda a negatividade."
        )
 
    elif col == "average_playtime":
        print(
            f"  O tempo médio de jogo é de {media:.0f} minutos (~{media/60:.1f}h). "
            f"A mediana de {mediana:.0f} minutos indica que metade dos jogos tem "
            f"tempo de jogo muito baixo — muitos títulos são pouco jogados após a "
            f"compra. O máximo de {maximo:.0f} min (~{maximo/60:.0f}h) pertence a "
            f"jogos de altíssimo engajamento (RPGs, sandbox). O alto desvio padrão "
            f"({desvio:.0f} min) reflete a diversidade de gêneros na plataforma."
        )
 
    elif col == "achievements":
        print(
            f"  A média de {media:.1f} conquistas por jogo e a moda de {moda:.0f} "
            f"indicam que muitos jogos não possuem nenhuma conquista. A mediana de "
            f"{mediana:.0f} conquistas mostra que metade dos jogos tem poucas ou "
            f"nenhuma. O máximo de {maximo:.0f} pertence a jogos com sistemas "
            f"extensos de progressão. O IQR de {iqr:.0f} demonstra que 50%% dos "
            f"jogos ficam em uma faixa de conquistas relativamente baixa."
        )
 
    elif col == "approval_rate":
        print(
            f"  A taxa de aprovação média é de {media:.1f}%%, com mediana de "
            f"{mediana:.1f}%%. Isso indica que, em geral, os jogos da Steam são bem "
            f"avaliados pela comunidade. O mínimo de {minimo:.1f}%% representa jogos "
            f"extremamente polêmicos. O Q1 de {q1:.1f}%% mostra que 75%% dos jogos "
            f"possuem aprovação acima desse valor. O desvio padrão de {desvio:.1f}%% "
            f"indica variação moderada — há tanto sucessos quanto fracassos na plataforma."
        )
 

# 5. Resumo Geral

print("\n\n" + "=" * 60)
print("  RESUMO ANALÍTICO DO DATASET")
print("=" * 60)
print("""
  O dataset Steam Games contém informações de 27.075 jogos publicados
  na plataforma Steam, coletadas via API do SteamSpy. Os dados abrangem
  características técnicas, comerciais e de engajamento dos jogos.
 
  A base permite analisar o mercado de jogos digitais sob diversas
  perspectivas: precificação, recepção da comunidade, engajamento dos
  jogadores e diversidade de gêneros. A grande variação nos valores das
  variáveis numéricas reflete a natureza heterogênea da plataforma, que
  reúne desde grandes produções (AAA) até jogos independentes (indie).
 
  A variável criada 'approval_rate' sintetiza a percepção do público em
  um único indicador percentual, facilitando comparações entre jogos com
  volumes de avaliações muito diferentes.
 
  Esta análise serve de base para a construção do dashboard (R2) e para
  a aplicação dos modelos de Machine Learning (R3), onde buscaremos
  prever se um jogo será bem avaliado com base em suas características.
""")
 
print("✅ Etapa 1 (R1) concluída com sucesso!")
 