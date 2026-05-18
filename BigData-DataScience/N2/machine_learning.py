
#  R3 — Modelagem Preditiva (Machine Learning)
#  Dataset: Steam Games (27.075 jogos)
#  Objetivo: Classificar se um jogo será bem avaliado ou não
#  Algoritmos: Random Forest e Regressão Logística

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report,
    ConfusionMatrixDisplay
)


# 1. Carregamento e Preparacao da Dados

print("=" * 60)
print("  R3 — MODELAGEM PREDITIVA — STEAM GAMES")
print("=" * 60)

df = pd.read_csv("steam.csv")
df.dropna(subset=["developer", "publisher"], inplace=True)

df["approval_rate"] = (
    df["positive_ratings"] / (df["positive_ratings"] + df["negative_ratings"])
).replace([float("inf"), float("nan")], 0) * 100

df["bem_avaliado"] = (df["approval_rate"] >= 75).astype(int)

print(f"\n✅ Registros carregados: {df.shape[0]}")
print(f"\n🎯 Variável alvo — 'bem_avaliado':")
print(f"   Jogos BEM avaliados  (≥75%): {df['bem_avaliado'].sum():>6}")
print(f"   Jogos MAL avaliados  (<75%): {(df['bem_avaliado'] == 0).sum():>6}")


# 2. Engenharia de Features


df["tem_windows"] = df["platforms"].str.contains("windows").astype(int)
df["tem_mac"]     = df["platforms"].str.contains("mac").astype(int)
df["tem_linux"]   = df["platforms"].str.contains("linux").astype(int)

df["main_genre"] = df["genres"].str.split(";").str[0].str.strip()
le = LabelEncoder()
df["genre_cod"] = le.fit_transform(df["main_genre"])

df["is_free"] = (df["price"] == 0).astype(int)

features = [
    "price",
    "achievements",
    "average_playtime",
    "median_playtime",
    "required_age",
    "tem_windows",
    "tem_mac",
    "tem_linux",
    "genre_cod",
    "is_free",
]

X = df[features]
y = df["bem_avaliado"]


# 3. Divisao Treino / Teste

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n📂 Divisão Treino/Teste:")
print(f"   Treino: {X_train.shape[0]} amostras (80%)")
print(f"   Teste:  {X_test.shape[0]} amostras (20%)")

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)


# 4. Algoritmo 1 — Random Forest

print("\n\n" + "=" * 60)
print("  ALGORITMO 1 — RANDOM FOREST CLASSIFIER")
print("=" * 60)

print("""
  📌 Justificativa da Escolha:
  O Random Forest é um algoritmo de ensemble baseado em múltiplas
  árvores de decisão. Foi escolhido por ser robusto a outliers (que
  existem em abundância neste dataset), não exigir normalização dos
  dados, lidar bem com variáveis numéricas e categóricas, e fornecer
  ranking de importância das features. É ideal para dados heterogêneos
  como os dados de jogos da Steam.

  ⚙️  Processo de Treinamento:
  Foram criadas 100 árvores de decisão (n_estimators=100), cada uma
  treinada com uma amostra aleatória dos dados e um subconjunto
  aleatório das features. A predição final é feita por votação
  majoritária entre as 100 árvores. Semente aleatória fixada em 42
  para garantir reprodutibilidade.
""")

rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)

acc_rf   = accuracy_score(y_test, y_pred_rf)
prec_rf  = precision_score(y_test, y_pred_rf)
rec_rf   = recall_score(y_test, y_pred_rf)
f1_rf    = f1_score(y_test, y_pred_rf)

print(f"  📊 Resultados:")
print(f"     Acurácia:  {acc_rf*100:.2f}%")
print(f"     Precisão:  {prec_rf*100:.2f}%")
print(f"     Recall:    {rec_rf*100:.2f}%")
print(f"     F1-Score:  {f1_rf*100:.2f}%")

print(f"\n  📋 Relatório Completo:")
print(classification_report(y_test, y_pred_rf,
      target_names=["Mal Avaliado", "Bem Avaliado"]))

print("""
  📝 Interpretação:
  A acurácia indica a proporção de jogos classificados corretamente.
  A precisão mede quantos dos jogos previstos como "bem avaliados"
  realmente são. O recall mostra quantos jogos bem avaliados o modelo
  conseguiu identificar. O F1-Score é a média harmônica entre precisão
  e recall, sendo a métrica mais equilibrada para este problema.
""")

importancias = pd.Series(rf.feature_importances_, index=features).sort_values(ascending=False)
print("  🔍 Importância das Features (Random Forest):")
for feat, imp in importancias.items():
    barra = "█" * int(imp * 50)
    print(f"     {feat:<20} {barra} {imp:.4f}")


# 5. Algoritmo 2 — Regressa Logistica

print("\n\n" + "=" * 60)
print("  ALGORITMO 2 — REGRESSÃO LOGÍSTICA")
print("=" * 60)

print("""
  📌 Justificativa da Escolha:
  A Regressão Logística é um algoritmo clássico de classificação
  binária, ideal para problemas onde a variável alvo tem duas classes
  (bem avaliado / mal avaliado). Foi escolhida como segundo algoritmo
  por ser interpretável, rápida e servir como baseline de comparação
  com o Random Forest. Ela estima a probabilidade de um jogo ser bem
  avaliado com base nas features fornecidas.

  ⚙️  Processo de Treinamento:
  Os dados foram normalizados com StandardScaler antes do treinamento,
  pois a Regressão Logística é sensível à escala das variáveis.
  O parâmetro max_iter=1000 garante convergência. Foi usada
  regularização L2 (padrão) para evitar overfitting.
""")

lr = LogisticRegression(max_iter=1000, random_state=42)
lr.fit(X_train_sc, y_train)
y_pred_lr = lr.predict(X_test_sc)

acc_lr   = accuracy_score(y_test, y_pred_lr)
prec_lr  = precision_score(y_test, y_pred_lr)
rec_lr   = recall_score(y_test, y_pred_lr)
f1_lr    = f1_score(y_test, y_pred_lr)

print(f"  📊 Resultados:")
print(f"     Acurácia:  {acc_lr*100:.2f}%")
print(f"     Precisão:  {prec_lr*100:.2f}%")
print(f"     Recall:    {rec_lr*100:.2f}%")
print(f"     F1-Score:  {f1_lr*100:.2f}%")

print(f"\n  📋 Relatório Completo:")
print(classification_report(y_test, y_pred_lr,
      target_names=["Mal Avaliado", "Bem Avaliado"]))

print("""
  📝 Interpretação:
  A Regressão Logística apresenta resultados interpretáveis através
  dos coeficientes de cada feature. Acurácia mais baixa que o Random
  Forest é esperada, pois o modelo assume relações lineares entre as
  variáveis, o que pode não capturar padrões mais complexos presentes
  nos dados de jogos da Steam.
""")

# 6.Comparacao entre algoritmos

print("\n\n" + "=" * 60)
print("  COMPARAÇÃO ENTRE OS ALGORITMOS")
print("=" * 60)

print(f"""
  {'Métrica':<15} {'Random Forest':>15} {'Reg. Logística':>15}
  {'-'*45}
  {'Acurácia':<15} {acc_rf*100:>14.2f}% {acc_lr*100:>14.2f}%
  {'Precisão':<15} {prec_rf*100:>14.2f}% {prec_lr*100:>14.2f}%
  {'Recall':<15} {rec_rf*100:>14.2f}% {rec_lr*100:>14.2f}%
  {'F1-Score':<15} {f1_rf*100:>14.2f}% {f1_lr*100:>14.2f}%
""")

melhor = "Random Forest" if acc_rf >= acc_lr else "Regressão Logística"
print(f"""
  📝 Conclusão da Comparação:
  O {melhor} obteve melhor desempenho geral neste dataset.
  O Random Forest tende a superar a Regressão Logística em dados
  com relações não-lineares e com presença de outliers — ambas as
  características presentes no dataset Steam. A Regressão Logística,
  apesar de menor acurácia, é mais rápida e mais fácil de interpretar,
  sendo útil como modelo base (baseline). Para produção, o Random
  Forest seria a escolha recomendada por sua maior robustez.
""")

# 7. Grafico — Matrizez de Confusao Comparativas

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

fig.patch.set_facecolor("#171A21")

modelos = [
    ("Random Forest", confusion_matrix(y_test, y_pred_rf)),
    ("Regressão Logística", confusion_matrix(y_test, y_pred_lr))
]

for ax, (titulo, cm) in zip(axes, modelos):

    im = ax.imshow(cm, cmap="Blues")

    ax.set_facecolor("#1B2838")

    ax.set_title(
        titulo,
        color="white",
        fontsize=15,
        fontweight="bold",
        pad=12
    )

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])

    ax.set_xticklabels(
        ["Mal Avaliado", "Bem Avaliado"],
        color="white",
        fontsize=11
    )

    ax.set_yticklabels(
        ["Mal Avaliado", "Bem Avaliado"],
        color="white",
        fontsize=11
    )

    ax.set_xlabel("Predicted label", color="white")
    ax.set_ylabel("True label", color="white")

    for i in range(2):
        for j in range(2):

            valor = cm[i, j]

 
            if i == j:
                cor = "#66C0F4"

            # erros = vermelho
            else:
                cor = "#FF6B6B"

            ax.text(
                j,
                i,
                f"{valor}",
                ha="center",
                va="center",
                color=cor,
                fontsize=14,
                fontweight="bold"
            )

    for spine in ax.spines.values():
        spine.set_edgecolor("#66C0F4")
        spine.set_linewidth(1.2)

fig.suptitle(
    "Matrizes de Confusão — Comparação dos Algoritmos",
    color="white",
    fontsize=18,
    fontweight="bold"
)

plt.tight_layout()

plt.savefig(
    "matrizes_confusao.png",
    dpi=150,
    bbox_inches="tight",
    facecolor="#171A21"
)

plt.show()

print("✅ Gráfico salvo como 'matrizes_confusao.png'")
print("\n✅ Etapa 2 (R3) concluída com sucesso!")