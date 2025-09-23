import io
import base64
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def create_radar_chart_image(user_profile_values):
    """Creates a radar chart for the user profile and returns it as a Base64 string."""
    labels = np.array(["Realistic", "Investigative", "Artistic", "Social", "Enterprising", "Conventional"])
    stats = np.concatenate((user_profile_values, [user_profile_values[0]]))
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.set_thetagrids(angles[:-1] * 180 / np.pi, labels, fontsize=10)
    ax.plot(angles, stats, color="teal", linewidth=2)
    ax.fill(angles, stats, color="teal", alpha=0.25)
    ax.set_ylim(0, 5)
    ax.grid(True)
    fig.tight_layout(pad=1.5)

    return _fig_to_base64(fig)

def create_bar_chart_image(recommendations):
    """Creates a horizontal bar chart for job similarities and returns it as a Base64 string."""
    labels = [rec["Title"] for rec in recommendations]
    values = [(rec["similarity"] * 100) for rec in recommendations]
    labels.reverse()
    values.reverse()

    fig, ax = plt.subplots(figsize=(5, 5)) 
    ax.barh(labels, values, color="teal")
    ax.set_xlabel("Similarity (%)")
    ax.set_xlim(0, 100)
    ax.tick_params(axis="y", labelsize=8)
    fig.tight_layout()

    return _fig_to_base64(fig)

def _fig_to_base64(fig):
    """Converts a Matplotlib figure to a Base64 string."""
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{image_base64}"