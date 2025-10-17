#!/usr/bin/env python3

"""Test timestamp precision handling for different CBV versions."""

import unittest
from epcis_event_hash_generator.hash_generator import _fix_time_stamp_format


class TestTimestampPrecision(unittest.TestCase):
    """Test timestamp precision handling for CBV2.0 vs CBV2.1."""

    def test_cbv20_no_rounding_high_precision(self):
        """CBV2.0 should preserve high precision timestamps without rounding."""
        # Test with 6 digit microsecond precision
        timestamp = "2023-02-02T11:04:03.123456+01:00"
        result = _fix_time_stamp_format(timestamp, "CBV2.0")
        # Should preserve all 6 digits, convert to UTC
        expected = "2023-02-02T10:04:03.123456Z"
        self.assertEqual(result, expected)

    def test_cbv21_rounds_high_precision(self):
        """CBV2.1 should round high precision timestamps to 3 digits."""
        # Test with 6 digit microsecond precision
        timestamp = "2023-02-02T11:04:03.123456+01:00"
        result = _fix_time_stamp_format(timestamp, "CBV2.1")
        # Should round to 3 digits, convert to UTC
        expected = "2023-02-02T10:04:03.123Z"
        self.assertEqual(result, expected)

    def test_cbv20_pads_low_precision(self):
        """CBV2.0 should pad low precision timestamps to 3 digits."""
        # Test with 1 digit precision
        timestamp = "2023-02-02T11:04:03.1+01:00"
        result = _fix_time_stamp_format(timestamp, "CBV2.0")
        # Should pad to 3 digits, convert to UTC
        expected = "2023-02-02T10:04:03.100Z"
        self.assertEqual(result, expected)

    def test_cbv21_pads_low_precision(self):
        """CBV2.1 should also pad low precision timestamps to 3 digits."""
        # Test with 1 digit precision
        timestamp = "2023-02-02T11:04:03.1+01:00"
        result = _fix_time_stamp_format(timestamp, "CBV2.1")
        # Should pad to 3 digits, convert to UTC
        expected = "2023-02-02T10:04:03.100Z"
        self.assertEqual(result, expected)

    def test_cbv20_no_fractional_seconds(self):
        """CBV2.0 should add .000 when no fractional seconds are present."""
        timestamp = "2023-02-02T11:04:03+01:00"
        result = _fix_time_stamp_format(timestamp, "CBV2.0")
        expected = "2023-02-02T10:04:03.000Z"
        self.assertEqual(result, expected)

    def test_cbv21_no_fractional_seconds(self):
        """CBV2.1 should add .000 when no fractional seconds are present."""
        timestamp = "2023-02-02T11:04:03+01:00"
        result = _fix_time_stamp_format(timestamp, "CBV2.1")
        expected = "2023-02-02T10:04:03.000Z"
        self.assertEqual(result, expected)

    def test_cbv20_exact_3_digits(self):
        """CBV2.0 should preserve exactly 3 digit precision."""
        timestamp = "2023-02-02T11:04:03.123+01:00"
        result = _fix_time_stamp_format(timestamp, "CBV2.0")
        expected = "2023-02-02T10:04:03.123Z"
        self.assertEqual(result, expected)

    def test_cbv21_exact_3_digits(self):
        """CBV2.1 should preserve exactly 3 digit precision."""
        timestamp = "2023-02-02T11:04:03.123+01:00"
        result = _fix_time_stamp_format(timestamp, "CBV2.1")
        expected = "2023-02-02T10:04:03.123Z"
        self.assertEqual(result, expected)

    def test_cbv20_rounding_edge_case(self):
        """CBV2.0 should not round, even when microseconds would round up."""
        # 1415 microseconds = 1.415 milliseconds, would round to 1 ms in CBV2.1
        timestamp = "2023-02-02T11:04:03.001415+01:00"
        result = _fix_time_stamp_format(timestamp, "CBV2.0")
        expected = "2023-02-02T10:04:03.001415Z"
        self.assertEqual(result, expected)

    def test_cbv21_rounding_edge_case(self):
        """CBV2.1 should round microseconds to nearest millisecond."""
        # 1415 microseconds = 1.415 milliseconds, should round to 1 ms
        timestamp = "2023-02-02T11:04:03.001415+01:00"
        result = _fix_time_stamp_format(timestamp, "CBV2.1")
        expected = "2023-02-02T10:04:03.001Z"
        self.assertEqual(result, expected)

    def test_utc_timestamp_cbv20(self):
        """Test CBV2.0 with UTC timestamp (no timezone conversion needed)."""
        timestamp = "2023-02-02T11:04:03.123456Z"
        result = _fix_time_stamp_format(timestamp, "CBV2.0")
        expected = "2023-02-02T11:04:03.123456Z"
        self.assertEqual(result, expected)

    def test_utc_timestamp_cbv21(self):
        """Test CBV2.1 with UTC timestamp (no timezone conversion needed)."""
        timestamp = "2023-02-02T11:04:03.123456Z"
        result = _fix_time_stamp_format(timestamp, "CBV2.1")
        expected = "2023-02-02T11:04:03.123Z"
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
