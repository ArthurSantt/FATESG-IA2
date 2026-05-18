# =============================================================
#  R2 — Dashboard de Visualização
#  Dataset: Steam Games (27.075 jogos)
#  Gráficos: 3 visualizações distintas e informativas
# =============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# -------------------------------------------------------------
# 1. CARREGAMENTO E PREPARAÇÃO
# -------------------------------------------------------------
df = pd.read_csv("steam.csv")
df.dropna(subset=["developer", "publisher"], inplace=True)

# Taxa de aprovação
df["approval_rate"] = (
    df["positive_ratings"] / (df["positive_ratings"] + df["negative_ratings"])
).replace([float("inf"), float("nan")], 0) * 100

# Extrair gênero principal (primeiro da lista)
df["main_genre"] = df["genres"].str.split(";").str[0].str.strip()

# Faixa de preço
def faixa_preco(p):
    if p == 0:
        return "Gratuito"
    elif p <= 5:
        return "Até $5"
    elif p <= 15:
        return "$5 – $15"
    elif p <= 30:
        return "$15 – $30"
    else:
        return "Acima de $30"

df["faixa_preco"] = df["price"].apply(faixa_preco)

# Paleta de cores personalizada
CORES = ["#5C85D6", "#E07B39", "#4CAF7D", "#D65C8A", "#A05CD6", "#D6C25C"]

# -------------------------------------------------------------
# 2. CONFIGURAÇÃO DO DASHBOARD
# -------------------------------------------------------------
fig = plt.figure(figsize=(18, 14))
fig.patch.set_facecolor("#0F1923")

gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

ax1 = fig.add_subplot(gs[0, 0])      # Gráfico 1 – Top Gêneros
ax2 = fig.add_subplot(gs[0, 1])      # Gráfico 2 – Distribuição de Preços
ax3 = fig.add_subplot(gs[1, :])      # Gráfico 3 – Aprovação por Faixa de Preço

# Estilo global dos eixos
def estilo_eixo(ax, titulo):
    ax.set_facecolor("#1A2635")
    ax.set_title(titulo, color="white", fontsize=13, fontweight="bold", pad=12)
    ax.tick_params(colors="white", labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor("#2E3F50")
    ax.title.set_color("white")

# -------------------------------------------------------------
# GRÁFICO 1 — Top 10 Gêneros Mais Populares
# -------------------------------------------------------------
top_generos = (
    df["main_genre"]
    .value_counts()
    .head(10)
    .sort_values(ascending=True)
)

barras = ax1.barh(
    top_generos.index,
    top_generos.values,
    color=CORES[0],
    edgecolor="#0F1923",
    height=0.65,
)

# Rótulos nas barras
for barra in barras:
    largura = barra.get_width()
    ax1.text(
        largura + 30, barra.get_y() + barra.get_height() / 2,
        f"{int(largura):,}",
        va="center", ha="left", color="white", fontsize=8
    )

estilo_eixo(ax1, "🎮 Top 10 Gêneros Mais Populares")
ax1.set_xlabel("Número de Jogos", color="#A0B0C0", fontsize=9)
ax1.set_ylabel("Gênero", color="#A0B0C0", fontsize=9)
ax1.xaxis.label.set_color("#A0B0C0")
ax1.yaxis.label.set_color("#A0B0C0")
ax1.set_xlim(0, top_generos.values.max() * 1.2)

# -------------------------------------------------------------
# GRÁFICO 2 — Distribuição por Faixa de Preço (Pizza)
# -------------------------------------------------------------
ordem = ["Gratuito", "Até $5", "$5 – $15", "$15 – $30", "Acima de $30"]
contagem_faixa = df["faixa_preco"].value_counts().reindex(ordem).fillna(0)

wedges, texts, autotexts = ax2.pie(
    contagem_faixa.values,
    labels=contagem_faixa.index,
    autopct="%1.1f%%",
    colors=CORES[:5],
    startangle=140,
    pctdistance=0.80,
    wedgeprops=dict(edgecolor="#0F1923", linewidth=1.5),
)

for text in texts:
    text.set_color("white")
    text.set_fontsize(9)
for autotext in autotexts:
    autotext.set_color("white")
    autotext.set_fontsize(8)
    autotext.set_fontweight("bold")

estilo_eixo(ax2, "💰 Distribuição por Faixa de Preço")


# Grafico 3 — Taxa de Aprovação Média por Faixa de Preço

aprovacao_por_faixa = (
    df.groupby("faixa_preco")["approval_rate"]
    .mean()
    .reindex(ordem)
    .fillna(0)
)

barras3 = ax3.bar(
    aprovacao_por_faixa.index,
    aprovacao_por_faixa.values,
    color=CORES,
    edgecolor="#0F1923",
    width=0.55,
)

# Linha de média geral
media_geral = df["approval_rate"].mean()
ax3.axhline(
    media_geral, color="#FFD700", linestyle="--", linewidth=1.5,
    label=f"Média geral: {media_geral:.1f}%"
)

for barra in barras3:
    altura = barra.get_height()
    ax3.text(
        barra.get_x() + barra.get_width() / 2,
        altura + 0.3,
        f"{altura:.1f}%",
        ha="center", va="bottom", color="white", fontsize=10, fontweight="bold"
    )

estilo_eixo(ax3, "⭐ Taxa de Aprovação Média por Faixa de Preço")
ax3.set_xlabel("Faixa de Preço", color="#A0B0C0", fontsize=10)
ax3.set_ylabel("Aprovação Média (%)", color="#A0B0C0", fontsize=10)
ax3.set_ylim(0, 100)
ax3.legend(
    facecolor="#1A2635", edgecolor="#2E3F50",
    labelcolor="white", fontsize=9
)


# Titulo Principal

fig.suptitle(
    "STEAM GAMES — DASHBOARD DE ANÁLISE",
    color="white", fontsize=18, fontweight="bold", y=0.97
)
fig.text(
    0.5, 0.935,
    "Dataset: 27.075 jogos | Fonte: SteamSpy / Kaggle",
    ha="center", color="#A0B0C0", fontsize=10
)


# Salvar e Exibir

plt.savefig("dashboard.png", dpi=150, bbox_inches="tight", facecolor="#0F1923")
plt.show()

print("✅ Dashboard salvo como 'dashboard.png'")
print("\n📊 Gráficos gerados:")
print("  1. Top 10 Gêneros Mais Populares (barras horizontais)")
print("  2. Distribuição por Faixa de Preço (pizza)")
print("  3. Taxa de Aprovação Média por Faixa de Preço (barras + linha de média)")