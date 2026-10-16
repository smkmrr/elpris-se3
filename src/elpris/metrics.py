import pandas as pd


def mae(y_true, y_pred):
    """Genomsnittligt absolut fel mellan verkliga och förutspådda värden."""
    errors = (y_true - y_pred).abs()
    return errors.mean()