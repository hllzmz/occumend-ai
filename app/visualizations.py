import io
import base64
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import textwrap


def create_radar_chart_image(user_profile_values):
    """Creates a visually enhanced radar chart and returns it as a Base64 string."""
    labels = np.array(
        [
            "Realistic",
            "Investigative",
            "Artistic",
            "Social",
            "Enterprising",
            "Conventional",
        ]
    )
    stats = np.concatenate((user_profile_values, [user_profile_values[0]]))
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))

    sns.set_theme(style="whitegrid")
    radar_color = "#007bff"

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    ax.plot(angles, stats, color=radar_color, linewidth=3)
    ax.fill(angles, stats, color=radar_color, alpha=0.25)

    ax.set_thetagrids(
        angles[:-1] * 180 / np.pi, labels, fontsize=13, weight="bold", color="#333"
    )
    ax.set_yticks(np.arange(1, 6))
    ax.set_yticklabels(["1", "2", "3", "4", "5"], color="grey", size=11)
    ax.set_ylim(0, 5)

    ax.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.7)
    ax.spines["polar"].set_visible(False)

    return _fig_to_base64(fig)


def create_bar_chart_image(recommendations):
    """Creates a bar chart with wrapped occupation labels inside the bars to prevent overflow."""
    top_recommendations = recommendations[:10]

    data = {
        "Occupation": [rec["Title"] for rec in top_recommendations],
        "Similarity": [(rec["similarity"] * 100) for rec in top_recommendations],
    }
    df = pd.DataFrame(data).sort_values("Similarity", ascending=False)

    sns.set_theme(style="whitegrid")

    fig, ax = plt.subplots(figsize=(8, 8))

    bars = sns.barplot(
        x="Similarity",
        y=df.index,
        data=df,
        orient="h",
        ax=ax,
        color="#007bff",
    )

    max_similarity = df["Similarity"].max()
    min_similarity = df["Similarity"].min()
    ax.set_xlim(left=min_similarity - 5, right=max_similarity + 0.1)

    ax.set_xlabel("")
    ax.set_ylabel("")

    ax.set_yticklabels([])
    ax.set_yticks([])

    ax.grid(axis="x", linestyle="-", linewidth=0.7, alpha=0.3)

    sns.despine(left=True, bottom=True)
    ax.tick_params(axis="x", labelbottom=False)

    for index, (bar, row) in enumerate(zip(bars.patches, df.itertuples())):
        width = bar.get_width()

        wrapped_label = textwrap.fill(row.Occupation, width=40)

        ax.text(
            ax.get_xlim()[0] + 0.5,
            bar.get_y() + bar.get_height() / 2,
            wrapped_label,
            ha="left",
            va="center",
            fontsize=12,
            color="white",
            weight="bold",
        )

        ax.text(
            width + 0.3,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.1f}%",
            va="center",
            ha="left",
            color="#444",
            fontsize=12,
        )

    fig.tight_layout(pad=1.5)

    return _fig_to_base64(fig)


def _fig_to_base64(fig):
    """Converts a Matplotlib figure to a Base64 string with high resolution."""
    buf = io.BytesIO()
    plt.savefig(buf, format="png", pad_inches=0.3)
    plt.close(fig)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{image_base64}"
