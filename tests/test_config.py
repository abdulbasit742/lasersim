"""Validate config-driven chain building."""
import json

from config import build_from_config, NILOP_CONFIG, load_config


def test_build_nilop_from_config():
    chain = build_from_config(NILOP_CONFIG)
    results = chain.run()
    assert results[-1].e_out_mJ > 950.0


def test_config_roundtrip_json(tmp_path):
    p = tmp_path / "sys.json"
    p.write_text(json.dumps(NILOP_CONFIG))
    cfg = load_config(str(p))
    assert cfg["seed_mJ"] == 15
    chain = build_from_config(cfg)
    assert len(chain.run()) == len(NILOP_CONFIG["stages"])


def test_custom_minimal_chain():
    cfg = {
        "name": "mini", "seed_mJ": 50,
        "stages": [
            {"type": "amp", "name": "A", "diameter_cm": 1.0, "length_cm": 10,
             "stored_J": 0.5, "passes": 1, "beam_radius_cm": 0.3, "order": 2},
        ],
    }
    results = build_from_config(cfg).run()
    assert results[-1].e_out_mJ > 50.0


def test_unknown_stage_type_raises():
    cfg = {"name": "x", "seed_mJ": 10,
           "stages": [{"type": "bogus", "name": "z"}]}
    try:
        build_from_config(cfg)
        assert False, "should have raised"
    except ValueError:
        pass
