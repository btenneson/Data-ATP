from data_atp.sentinel import ResourceSample, RobustBaseline, Sentinel, SentinelConfig


def _sentinel() -> Sentinel:
    return Sentinel(
        RobustBaseline(
            median_time_s=10.0,
            mad_time_s=2.0,
            median_rss_mb=100.0,
            mad_rss_mb=10.0,
            median_ram_growth_mb_s=1.0,
            mad_ram_growth_mb_s=0.5,
        ),
        SentinelConfig(
            time_z_threshold=6.0,
            rss_z_threshold=6.0,
            growth_z_threshold=6.0,
            min_joint_signals=2,
            hard_time_s=300.0,
            hard_rss_mb=8192.0,
        ),
    )


def test_memory_outlier_alone_is_allowed():
    decision = _sentinel().inspect(
        ResourceSample(elapsed_s=10.0, peak_rss_mb=1000.0, ram_growth_mb_s=1.0)
    )
    assert decision.action == "continue"
    assert decision.anomaly_signals == 1


def test_joint_time_and_memory_outlier_is_quarantined():
    decision = _sentinel().inspect(
        ResourceSample(elapsed_s=100.0, peak_rss_mb=1000.0, ram_growth_mb_s=1.0)
    )
    assert decision.action == "quarantine"
    assert decision.reason == "joint_resource_anomaly"
    assert decision.anomaly_signals >= 2


def test_growth_plus_memory_can_quarantine_even_before_long_timeout():
    decision = _sentinel().inspect(
        ResourceSample(elapsed_s=10.0, peak_rss_mb=1000.0, ram_growth_mb_s=20.0)
    )
    assert decision.action == "quarantine"


def test_hard_ceiling_is_reported_separately():
    decision = _sentinel().inspect(
        ResourceSample(elapsed_s=301.0, peak_rss_mb=100.0, ram_growth_mb_s=1.0)
    )
    assert decision.action == "hard_stop"
    assert decision.reason == "hard_time_ceiling"
