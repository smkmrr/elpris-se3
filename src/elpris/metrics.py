import pandas as pd


def mae(y_true, y_pred):
    """Genomsnittligt absolut fel mellan verkliga och förutspådda värden."""
    errors = (y_true - y_pred).abs()
    return errors.mean()


def mae_table(predictions):
    """MAE per modell, målvärde och prognosdag.

    predictions ska ha kolumnerna model, target, horizon, y_true och y_pred.
    """
    errors = (predictions["y_true"] - predictions["y_pred"]).abs()
    predictions = predictions.assign(abs_error=errors)

    table = (
        predictions.groupby(["model", "target", "horizon"])["abs_error"]
        .mean()
        .unstack("horizon")
    )
    return table


SEASONS = {
    12: "vinter",
    1: "vinter",
    2: "vinter",
    3: "vår",
    4: "vår",
    5: "vår",
    6: "sommar",
    7: "sommar",
    8: "sommar",
    9: "höst",
    10: "höst",
    11: "höst",
}


def _season(predictions):
    """Årstid för varje rad, bestämd av target_date."""
    return pd.to_datetime(predictions["target_date"]).dt.month.map(SEASONS)


def mae_by_season(predictions):
    """MAE per modell, målvärde och årstid (årstiden bestäms av target_date)."""
    abs_error = (predictions["y_true"] - predictions["y_pred"]).abs()
    return (
        predictions.assign(season=_season(predictions), abs_error=abs_error)
        .groupby(["model", "target", "season"])["abs_error"]
        .mean()
        .unstack("season")
    )


def bias_by_season(predictions):
    """Medelfel med tecken (y_pred - y_true) per modell, målvärde och årstid.

    Negativt värde betyder att modellen i genomsnitt förutsäger för lågt.
    """
    error = predictions["y_pred"] - predictions["y_true"]
    return (
        predictions.assign(season=_season(predictions), error=error)
        .groupby(["model", "target", "season"])["error"]
        .mean()
        .unstack("season")
    )


def mae_spike_vs_normal(predictions, quantile=0.9):
    """MAE på spikdagar jämfört med vanliga dagar.

    En spikdag är en måldag vars verkliga max ligger bland de högsta
    (1 - quantile) av måldagarna i predictions.
    """
    max_rows = predictions[predictions["target"] == "max"].drop_duplicates(
        "target_date"
    )
    threshold = max_rows["y_true"].quantile(quantile)
    spike_dates = set(max_rows.loc[max_rows["y_true"] >= threshold, "target_date"])

    day_type = (
        predictions["target_date"]
        .isin(spike_dates)
        .map({True: "spik", False: "normal"})
    )
    abs_error = (predictions["y_true"] - predictions["y_pred"]).abs()
    return (
        predictions.assign(day_type=day_type, abs_error=abs_error)
        .groupby(["model", "target", "day_type"])["abs_error"]
        .mean()
        .unstack("day_type")
    )
