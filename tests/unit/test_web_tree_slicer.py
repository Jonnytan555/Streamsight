from articles.enrich.web.web_tree_slicer import WebTreeSlicer

_TREE = {
    "Energy": {
        "Natural Gas": {
            "European Gas": ["TTF", "NBP"],
            "US Gas":       ["Henry Hub"],
        },
        "Oil": {
            "Crude Oil": ["Brent", "WTI"],
        },
    },
}


def test_slice_by_group_and_classification():
    result = WebTreeSlicer(_TREE).slice("Natural Gas", "European Gas")
    assert "European Gas" in result
    assert "TTF" in result
    assert "US Gas" not in result
    assert "Crude Oil" not in result


def test_slice_by_group_only_returns_all_classifications():
    result = WebTreeSlicer(_TREE).slice("Natural Gas", None)
    assert "European Gas" in result
    assert "US Gas" in result
    assert "Crude Oil" not in result


def test_slice_with_no_context_returns_full_tree():
    result = WebTreeSlicer(_TREE).slice(None, None)
    assert "Natural Gas" in result
    assert "Oil" in result
    assert "Crude Oil" in result


def test_unknown_group_returns_full_tree():
    result = WebTreeSlicer(_TREE).slice("Unknown", None)
    assert "Natural Gas" in result
    assert "Oil" in result


def test_unknown_classification_returns_all_classifications_in_group():
    result = WebTreeSlicer(_TREE).slice("Natural Gas", "Unknown")
    assert "European Gas" in result
    assert "US Gas" in result


def test_instruments_listed():
    result = WebTreeSlicer(_TREE).slice("Natural Gas", "European Gas")
    assert "TTF" in result
    assert "NBP" in result
