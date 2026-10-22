import matplotlib.pyplot as plt

COLORS = {"mean": "tab:blue", "max": "tab:red", "min": "tab:green"}
LABELS = {"mean": "mean", "max": "max", "min": "min"}


def plot_mae_by_horizon(table, model):
    """Rita MAE per prognosdag för en modell, en linje per målvärde.

    table är resultatet från mae_table.
    """
    fig, ax = plt.subplots(figsize=(8, 4))

    for target in ["max", "mean", "min"]:
        errors = table.loc[(model, target)]
        ax.plot(
            errors.index,
            errors.values,
            marker="o",
            linewidth=2,
            color=COLORS[target],
            label=LABELS[target],
        )

    ax.set_title(f"{model}: genomsnittligt fel per prognosdag")
    ax.set_xlabel("Dagar framåt")
    ax.set_ylabel("MAE (SEK/kWh)")
    ax.set_xticks(range(1, 8))
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", color="#e5e5e5")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False)

    return fig


def plot_model_comparison(
    table,
    models=("baseline", "random_forest"),
):
    """Rita båda modellerna i samma graf."""
    fig, ax = plt.subplots(figsize=(9, 5))

    linestyles = {
        "baseline": "--",
        "random_forest": "-",
    }

    for model in models:
        for target in ["mean", "max", "min"]:
            errors = table.loc[(model, target)]

            ax.plot(
                errors.index,
                errors.values,
                marker="o",
                linewidth=2,
                color=COLORS[target],
                linestyle=linestyles.get(model, "-"),
                label=f"{model}: {LABELS[target]}",
            )

    ax.set_title("MAE per modell och prognosdag")
    ax.set_xlabel("Dagar framåt")
    ax.set_ylabel("MAE (SEK/kWh)")
    ax.set_xticks(range(1, 8))
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", color="#e5e5e5")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False)

    return fig
