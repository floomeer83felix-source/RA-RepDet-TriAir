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


def test_channel_removal_contract_is_fixed_and_holdout_free():
    text = source("run_v84_channel_removal_2x2.py")
    assert 'result[0:3].zero_()' in text
    assert 'result[3:4].zero_()' in text
    assert 'result[4:5].zero_()' in text
    assert 'CONDITIONS = ("full", "no_rgb", "no_thermal", "no_event")' in text
    assert "v40_guard_unchanged_archival" not in text


def test_gate_quality_contract_uses_no_dropout_and_fixed_severities():
    text = source("run_v84_gate_quality_analysis.py")
    assert 'row["variant"] == "ra_no_moddrop"' in text
    assert 'LEVELS = (0, 1, 2, 3)' in text
    assert '(3, 7, 11)' in text
    assert '(0.75, 0.50, 0.25)' in text
    assert "day/night" in text
    assert "v40_guard_unchanged_archival" not in text


def test_component_bootstrap_contract_uses_components_and_5000_replicates():
    text = source("run_v84_component_cluster_bootstrap.py")
    assert "REPLICATES = 5000" in text
    assert "BOOTSTRAP_SEED = 8404" in text
    assert 'row["v39_partition"] == "VALIDATION"' in text
    assert "component-macro" in text
    assert "v40_guard_unchanged_archival" not in text


def test_post_training_queue_waits_for_p1_and_orders_p2_to_p4():
    text = source("run_v84_post_training_queue.py")
    assert "while not p1_complete()" in text
    assert text.index("P2_CHANNEL_REMOVAL") < text.index("P3_GATE_QUALITY")
    assert text.index("P3_GATE_QUALITY") < text.index("P4_COMPONENT_BOOTSTRAP")
    assert "v40_guard_unchanged_archival" not in text
