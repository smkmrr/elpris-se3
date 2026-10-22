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
