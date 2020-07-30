from matplotlib import pyplot as plt
from matplotlib.axes import Axes
import numpy as np

from ml_tooling.utils import DataType
from ml_tooling.plots.utils import _plot_barh


class MLToolingError(Exception):
    """Error which occurs when using ML Tooling"""


class VizError(MLToolingError):
    """Error which occurs when using a Visualization"""


def plot_target_feature_distribution(
    target: DataType,
    feature: DataType,
    title: str = "Target feature distribution",
    method: str = "mean",
    ax: plt.Axes = None,
    n_boots: int = None,
) -> Axes:
    """
    Creates a plot which compares the mean or median
    of a binary target based on the given category features.

    Parameters
    ----------
    target: DataType
        Target to aggregate per feature category
    feature: DataType
        Categorical feature to group by
    title: str
        Title of graph
    method: str
        Which method to compare with. One of 'median' or 'mean'.
    ax: plt.Axes
        Matplotlib axes to draw the graph on. Creates a new one by default
    n_boots: int
        The number of bootstrap iterations to use.
    Returns
    -------
    plt.Axes

    """
    if np.isnan(target).any() or np.isnan(feature).any():
        raise VizError(
            "Target feature distribution plot only works if feature and "
            "target do not contain NaN Values"
        )

    if ax is None:
        fig, ax = plt.subplots()

    agg_func_mapping = {"mean": np.mean, "median": np.median}

    selected_agg_func = agg_func_mapping[method]

    feature_categories = np.unique(feature)

    if len(feature_categories) > 15:
        raise VizError("Should there be a limit")

    data = np.asarray(
        [
            selected_agg_func(target[feature == category])
            for category in feature_categories
        ]
    )

    if n_boots:

        percentile = np.zeros((2, feature_categories.shape[0]))
        i = 0
        for category in feature_categories:
            data_temp = target[feature == category]
            boots_sample = np.random.choice(
                data_temp, size=n_boots * data_temp.shape[0], replace=True
            ).reshape((data_temp.shape[0], -1))
            boots_temp = np.mean(boots_sample, axis=0)
            percentile[:, i] = np.percentile(boots_temp, (2.5, 97.5))
            i += 1

    ax = _plot_barh(
        feature_categories,
        data,
        add_label=True,
        title=title,
        x_label=f"Target compared to {method}",
        y_label="Feature categories",
        ax=ax,
        xerr=percentile if n_boots else None,
    )

    ax.axvline(y=selected_agg_func(feature), linestyle="--", color="red")

    return ax
