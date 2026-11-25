//! Pure spending-policy math, unit tested on the host.

pub const DAY_SECONDS: i64 = 86_400;

pub fn valid_caps(per_tx: u64, daily: u64, lifetime: u64) -> bool {
    per_tx > 0 && per_tx <= daily && daily <= lifetime
}

/// Leaky-bucket daily allowance (review finding H2).
///
/// Usage decays linearly at `daily_cap` per 86,400 s instead of resetting at
/// a fixed window boundary. Guarantee: at most `daily_cap` can be spent in a
/// burst, and over any interval of length T at most
/// `daily_cap * (1 + T / 86_400)`. The fixed-window version allowed
/// 2 x `daily_cap` within seconds across a window boundary.
///
/// The clock is clamped (finding L3): `now < last` is treated as no elapsed
/// time rather than failing. Returns `(decayed_spent, new_last_refill_at)`.
/// When integer division yields no refill the timestamp is not advanced, so
/// frequent small spends cannot starve the refill.
pub fn refill(spent: u64, daily_cap: u64, last: i64, now: i64) -> (u64, i64) {
    let now = now.max(last);
    if spent == 0 {
        return (0, now);
    }
    let elapsed = (now - last) as u128;
    let refill = (daily_cap as u128).saturating_mul(elapsed) / DAY_SECONDS as u128;
    if refill == 0 {
        return (spent, last);
    }
    let refill = u64::try_from(refill).unwrap_or(u64::MAX);
    (spent.saturating_sub(refill), now)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn cap_ordering() {
        assert!(valid_caps(1, 10, 100));
        assert!(valid_caps(10, 10, 10));
        assert!(!valid_caps(0, 10, 100));
        assert!(!valid_caps(11, 10, 100));
        assert!(!valid_caps(1, 101, 100));
    }

    #[test]
    fn refill_is_linear_and_saturating() {
        let cap = 86_400_000;
        assert_eq!(refill(cap, cap, 0, 0), (cap, 0));
        assert_eq!(refill(cap, cap, 0, 3_600), (cap - 3_600_000, 3_600));
        assert_eq!(
            refill(cap, cap, 0, DAY_SECONDS / 2),
            (cap / 2, DAY_SECONDS / 2)
        );
        assert_eq!(refill(cap, cap, 0, DAY_SECONDS), (0, DAY_SECONDS));
        assert_eq!(refill(cap, cap, 0, i64::MAX), (0, i64::MAX));
        assert_eq!(refill(u64::MAX, u64::MAX, 0, i64::MAX).0, 0);
    }

    #[test]
    fn clock_regression_is_clamped() {
        assert_eq!(refill(50, 100, 1_000, 900), (50, 1_000));
        assert_eq!(refill(0, 100, 1_000, 900), (0, 1_000));
    }

    #[test]
    fn sub_unit_refill_does_not_advance_clock() {
        // cap 10/day refills 1 unit every 8,640 s.
        assert_eq!(refill(10, 10, 0, 8_639), (10, 0));
        assert_eq!(refill(10, 10, 0, 8_640), (9, 8_640));
    }

    #[test]
    fn no_boundary_burst() {
        // Spend the full cap, then 1 s later only ~cap/86_400 is available.
        let cap = 1_000_000;
        let (spent, _) = refill(cap, cap, 86_399, 86_400);
        assert_eq!(cap - spent, 11);
    }
}
