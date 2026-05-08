from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.preprocessing import load_reviews_dir


def _write_csv(path: Path, df: pd.DataFrame) -> None:
    df.to_csv(path, index=False)


def test_load_reviews_dir_merges_compatible_files_and_skips_others(tmp_path: Path) -> None:
    file_a = tmp_path / "amazon_a.csv"
    file_b = tmp_path / "amazon_b.csv"
    file_unrelated = tmp_path / "submissions.csv"

    _write_csv(
        file_a,
        pd.DataFrame(
            {
                "name": ["A", "B"],
                "reviews.text": ["great battery", "broken remote"],
                "reviews.rating": [5, 2],
                "categories": ["Electronics", "Electronics"],
            }
        ),
    )
    _write_csv(
        file_b,
        pd.DataFrame(
            {
                "name": ["A", "C"],
                "reviews.text": ["great battery", "loud"],
                "reviews.rating": [5, 4],
                "categories": ["Electronics", "Audio"],
            }
        ),
    )
    _write_csv(
        file_unrelated,
        pd.DataFrame(
            {
                "title": ["unrelated"],
                "subreddit": ["pics"],
                "score": [42],
            }
        ),
    )

    merged = load_reviews_dir(tmp_path)

    assert "source_file" in merged.columns
    assert set(merged["source_file"].unique()) == {"amazon_a.csv", "amazon_b.csv"}
    # The duplicate (A, "great battery", 5) collapses across files.
    assert len(merged) == 3
    assert sorted(merged["name"].tolist()) == ["A", "B", "C"]


def test_load_reviews_dir_skips_malformed_file_with_incompatible_header(tmp_path: Path) -> None:
    _write_csv(
        tmp_path / "amazon.csv",
        pd.DataFrame(
            {
                "name": ["A"],
                "reviews.text": ["great battery"],
                "reviews.rating": [5],
                "categories": ["Electronics"],
            }
        ),
    )
    malformed = tmp_path / "submissions.csv"
    malformed.write_text(
        "title,subreddit,score\n"
        "ok,pics,42\n"
        "too,many,fields,on,this,line\n",
        encoding="utf-8",
    )

    merged = load_reviews_dir(tmp_path)

    assert len(merged) == 1
    assert merged.loc[0, "source_file"] == "amazon.csv"


def test_load_reviews_dir_raises_when_no_compatible_files(tmp_path: Path) -> None:
    _write_csv(
        tmp_path / "submissions.csv",
        pd.DataFrame({"title": ["x"], "subreddit": ["y"], "score": [1]}),
    )
    with pytest.raises(ValueError, match="No CSV files"):
        load_reviews_dir(tmp_path)


def test_load_reviews_dir_raises_when_directory_empty(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="No CSV files found"):
        load_reviews_dir(tmp_path)
