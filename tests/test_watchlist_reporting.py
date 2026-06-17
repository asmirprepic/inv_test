from pathlib import Path

from altintel.pipeline import export_ai_watchlist_pipeline


def test_export_ai_watchlist_pipeline_writes_artifacts(tmp_path: Path) -> None:
    artifacts = export_ai_watchlist_pipeline(
        portfolio_case="balanced_institution",
        quarters=8,
        seed=7,
        output_dir=tmp_path,
    )

    assert artifacts.json_path.exists()
    assert artifacts.markdown_path.exists()
