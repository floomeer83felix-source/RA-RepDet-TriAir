from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "rarepdet/tools/run_v83_post_v81_weight_evidence.py"


def test_v83_contract_is_fail_closed_and_label_free():
    text = SOURCE.read_text(encoding="utf-8")
    assert "V81 identity preflight failed" in text
    assert "checkpoint_sha256" in text
    assert "EXPECTED_SPLIT_SHA256" in text
    assert "holdout_accessed\": False" in text
    assert "DetectionTriAirDataset" not in text


def test_v83_primary_timing_contract_is_fixed():
    text = SOURCE.read_text(encoding="utf-8")
    assert 'default=50' in text
    assert 'default=200' in text
    assert "torch.cuda.synchronize(device)" in text
    assert '"precision": "FP32"' in text
    assert '"amp": False' in text
    assert '"torch_compile": False' in text


def test_v83_does_not_train_or_open_holdout():
    text = SOURCE.read_text(encoding="utf-8")
    assert ".backward(" not in text
    assert "optimizer" not in text.lower()
    assert "locked_holdout" not in text
