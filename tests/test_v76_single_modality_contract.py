"""Contract tests for the V76 single-modality experiment package."""

from rarepdet.experimental.v76_single_modality_detector import INPUT_CHANNELS


def test_v76_input_channel_contract():
    assert INPUT_CHANNELS == {"rgb": 3, "thermal": 1, "event": 1}


def test_v76_invalid_mode_is_not_authorized():
    assert "rgbte" not in INPUT_CHANNELS
