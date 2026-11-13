from app.services.mock_data_provider import MockDataProvider


def test_mock_provider_is_deterministic_and_in_range():
    first = MockDataProvider(seed=1)
    second = MockDataProvider(seed=1)
    assert first.snapshot().mission.progress_percent == second.snapshot().mission.progress_percent
    for _ in range(20):
        snapshot = first.tick()
        assert 0 <= snapshot.mission.progress_percent <= 100
        assert 0 <= snapshot.uav.battery_percent <= 100
        assert snapshot.telemetry.altitude_m >= 0


def test_provider_notifies_subscribers():
    provider = MockDataProvider()
    received = []
    provider.subscribe(received.append)
    provider.tick()
    assert len(received) == 1

