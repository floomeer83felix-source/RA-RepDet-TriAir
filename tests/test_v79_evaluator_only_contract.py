from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_eval_only_queue_has_no_training_entrypoint():
    text = (PROJECT_ROOT / "rarepdet" / "tools" / "run_v79_single_modality_eval_only.py").read_text(encoding="utf-8")
    assert "train_v76_single_modality.py" not in text
    assert '"ar1"' in text
    assert '"ar10"' in text
    assert '"ar100"' in text
    assert "best.pt" in text


def test_coco_metrics_exports_three_ar_levels():
    text = (PROJECT_ROOT / "rarepdet" / "coco_metrics.py").read_text(encoding="utf-8")
    for key in ('"ar1"', '"ar10"', '"ar100"', '"ar_by_max_dets"'):
        assert key in text


def test_summary_requires_all_nine_checkpoint_identities():
    text = (PROJECT_ROOT / "rarepdet" / "tools" / "build_v79_single_modality_evaluator_summary.py").read_text(encoding="utf-8")
    assert '"checkpoint_sha256"' in text
    assert '"split_sha256"' in text
    assert "len(records) != 9" in text
