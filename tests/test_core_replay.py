#!/usr/bin/env python3
"""Deterministic tests of frozen 200ms rule behavior; ZERO API/account access."""
import copy
import pathlib
import sys
import unittest
from unittest.mock import patch

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(ROOT / "tools"))
import systematic_native200_scan as grid
import stress_native200_candidates as stress
import discover_new_closed_windows as runner


YES55 = "YES_55_10_MOVE10_ALIGNED_SPREAD_LE2C_FIRST_180S"


def sample_book():
    """Synthetic book only, NOT a historical market or fill."""
    n = grid.TICKS
    limits = grid.LIMITS
    q = {
        "bps": np.arange(n, dtype=np.float32) * .032,
        "bid": np.full((2, n), .49, dtype=np.float32),
        "ask": np.full((2, n), .51, dtype=np.float32),
        "bid_avg": np.full((2, n, len(limits)), .49, dtype=np.float32),
        "bid_worst": np.full((2, n, len(limits)), .49, dtype=np.float32),
        "sizes": np.asarray(
            [int((10 - .001) / (p / 100 + .07 * (p / 100) * (1 - p / 100)))
             for p in limits], dtype=int
        ),
    }
    # For BUY YES, consume opposing NO bid at 49c -> YES ask 51c.
    # From T+60s, same-side YES bid becomes >=65c for a modeled target.
    q["bid_avg"][0, 300:, :] = .66
    q["bid_worst"][0, 300:, :] = .66
    return q


class OriginalResearchContract(unittest.TestCase):
    def test_exact_24570_rule_grammar(self):
        self.assertEqual(
            2 * len(grid.LIMITS) * len(grid.TARGETS) *
            len(grid.TRAJECTORY) * len(grid.BOOK) * len(grid.TIME),
            24570,
        )
        self.assertEqual(grid.ENTRY_BEGIN, 200)
        self.assertEqual(grid.ENTRY_END, 900)
        self.assertEqual(grid.DELAY, 10)

    def test_spot_direction_is_reversed_for_no(self):
        b = sample_book()
        fs = grid.features(b)
        y = grid.regimes(fs, 0)[0]["MOVE10_ALIGNED"]
        n = grid.regimes(fs, 1)[0]["MOVE10_OPPOSED"]
        self.assertTrue(y[200])
        self.assertTrue(n[200])
        self.assertFalse(grid.regimes(fs, 1)[0]["MOVE10_ALIGNED"][200])

    def test_yes55_historical_model_buy_exit_and_fee(self):
        b = sample_book()
        with patch.object(grid, "unpack", return_value=b), patch.object(
            grid, "ORACLES", {("ETH", "0915"): {"status": "CONFIDENT", "proxy_yes_wins": True}}
        ):
            result = grid.evaluate_market("ETH", "0915")
        self.assertIn(YES55, result)
        trade = result[YES55]
        self.assertEqual(trade["qty"], 17)
        self.assertEqual(trade["status"], "LIMIT_EXIT")
        self.assertGreater(trade["pnl"], 0)
        self.assertGreaterEqual(trade["entry_s"], 40)
        self.assertLessEqual(trade["entry_s"], 180)
        self.assertGreater(trade["exit_s"], trade["entry_s"])

    def test_no_future_spot_data_can_create_earlier_momentum_signal(self):
        b = sample_book()
        fs = grid.features(b)
        first = np.flatnonzero(
            grid.regimes(fs, 0)[0]["MOVE10_ALIGNED"] & (np.arange(grid.TICKS) >= 200)
        )[0]
        # Modify future spot observations only after the first 180 seconds.
        later = copy.deepcopy(b)
        later["bps"][950:] += 999
        fs2 = grid.features(later)
        second = np.flatnonzero(
            grid.regimes(fs2, 0)[0]["MOVE10_ALIGNED"] & (np.arange(grid.TICKS) >= 200)
        )[0]
        self.assertEqual(first, second)
        self.assertTrue(np.array_equal(fs["m10"][:900], fs2["m10"][:900], equal_nan=True))

    def test_quality_boundary_and_raw_flags(self):
        raw = {
            "prev_file_count": 1, "curr_file_count": 1,
            "metadata_lag_s": 30.08, "counts": {},
        }
        prepared = {"first_valid_sec": 30.2, "coverage_pct": 80.0, "count": {}}
        self.assertEqual(runner.quality(raw, prepared), [])
        self.assertIn("LESS_THAN80PCT_FRESH_QUOTE_COVERAGE",
                      runner.quality(raw, {**prepared, "coverage_pct": 79.99}))
        self.assertIn("NO_EARLY_CONTEMPORANEOUS_MARKET_STRIKE",
                      runner.quality({**raw, "metadata_lag_s": 41}, prepared))
        self.assertIn("RAW_gap_gt5s",
                      runner.quality({**raw, "counts": {"gap_gt5s": 1}}, prepared))

    def test_stress_evaluator_not_real_fills(self):
        b = sample_book()
        case = stress.parse(YES55)
        result = stress.eval_one(
            b, case, 10, 0, {"status": "CONFIDENT", "proxy_yes_wins": True}
        )
        self.assertIsNotNone(result)
        self.assertEqual(result[1], "TARGET")
        self.assertGreater(result[0], 0)


if __name__ == "__main__":
    unittest.main()
