import math

import pandas as pd

from funcguard.pd_utils.filter import pd_filter
from funcguard.pd_utils.statistics.mask_utils import _is_empty, _is_not_empty


def test_empty_helpers_handle_empty_list_correctly():
    assert _is_empty([]) is True
    assert _is_not_empty([]) is False
    assert _is_empty([1]) is False
    assert _is_not_empty([1]) is True


def test_pd_filter_not_empty_excludes_real_empty_containers_and_nan():
    df = pd.DataFrame(
        {
            "segments": [
                [],
                [1, 2],
                None,
                math.nan,
                "",
                "[]",
                {},
                {"a": 1},
            ]
        }
    )

    filtered = pd_filter(df, ("segments", "not empty"))

    assert filtered["segments"].tolist() == [[1, 2], "[]", {"a": 1}]
