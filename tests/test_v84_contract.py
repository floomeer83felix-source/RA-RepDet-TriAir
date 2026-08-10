from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def source(name):
    return (ROOT / "rarepdet/tools" / name).read_text(encoding="utf-8")


def test_preflight_is_fail_closed_and_does_not_touch_holdout():
    text = source("run_v84_preflight.py")
    assert "V84 preflight failed closed" in text
    assert "checkpoint_inventory.json" in text
    assert '"holdout_accessed": False' in text
    assert "v40_guard_unchanged_archival" not in text


def test_rgbt_training_contract_is_frozen():
    text = source("train_v84_rgb_thermal.py")
    assert 'mode="rgbt"' in text
    assert "in_chans=4" in text
    assert "range(1, 51)" in text
    assert "highest development-validation project-local AP50" in text
    assert "modality_dropout=0.0" in text


def test_queue_runs_exactly_three_seeds_without_holdout():
    text = source("run_v84_rgb_thermal_queue.py")
    assert "for seed in (0, 1, 2)" in text
    assert '"guard_used": False' in text
    assert "v40_guard_unchanged_archival" not in text
