import pytest
from unittest.mock import call
from experta_decision_engine import *

# A fixture to initialize DecisionEngine for each test
@pytest.fixture
def decision_engine(mocker):
    # Mock the CustomLogger to prevent actual file logging during tests
    mocker.patch('experta_decision_engine.CustomLogger.get_logger')
    return DecisionEngine()

# Test battery state transitions from normal to critical
@pytest.mark.parametrize("percent, expected_message", [
    (100.0, "Battery State 0: Normal"),
    (60.0, "Battery State 1: Mild"),
    (30.0, "Battery State 2: Severe"),
    (10.0, "Battery State 3: Critical"),
])
def test_battery_state_transitions(decision_engine, mocker, percent, expected_message):
    mock_log_info = mocker.patch.object(decision_engine.logger, "info")
    decision_engine.declare(BatteryStatus(percent=percent))
    decision_engine.run()
    mock_log_info.assert_any_call(expected_message)

# Test sensor anomaly state transitions from normal to critical
@pytest.mark.parametrize("confidence, expected_message", [
    (0.1, "Sensor Anomaly State 0: Normal"),
    (0.3, "Sensor Anomaly State 1: Mild"),
    (0.6, "Sensor Anomaly State 2: Severe"),
    (0.9, "Sensor Anomaly State 3: Critical"),
])
def test_sensor_anomaly_state_transitions(decision_engine, mocker, confidence, expected_message):
    mock_log_info = mocker.patch.object(decision_engine.logger, "info")
    decision_engine.declare(SensorAnomalyStatus(confidence=confidence))
    decision_engine.run()
    mock_log_info.assert_any_call(expected_message)


# Test overall state with a combination of battery and sensor anomaly states
@pytest.mark.parametrize("percent, confidence, expected_overall_state", [
    # Normal cases
    (100.0, 0.1, "Overall State 0: Normal"), 
    # Battery Mild, Sensor Anomaly varies
    (60.0, 0.1, "Overall State 1: Mild"), 
    (60.0, 0.3, "Overall State 1: Mild"), 
    (60.0, 0.6, "Overall State 2: Severe"), 
    (60.0, 0.9, "Overall State 3: Critical"), 
    # Battery Severe, Sensor Anomaly varies
    (30.0, 0.1, "Overall State 2: Severe"), 
    (30.0, 0.3, "Overall State 2: Severe"), 
    (30.0, 0.6, "Overall State 2: Severe"), 
    (30.0, 0.9, "Overall State 3: Critical"), 
    # Battery Critical, Sensor Anomaly varies
    (10.0, 0.1, "Overall State 3: Critical"), 
    (10.0, 0.3, "Overall State 3: Critical"), 
    (10.0, 0.6, "Overall State 3: Critical"), 
    (10.0, 0.9, "Overall State 3: Critical"),
    # Sensor Anomaly Mild but Battery varies
    (100.0, 0.3, "Overall State 1: Mild"),
    (60.0, 0.3, "Overall State 1: Mild"),
    (30.0, 0.3, "Overall State 2: Severe"),
    (10.0, 0.3, "Overall State 3: Critical"),
])
def test_overall_state_combination(decision_engine, mocker, percent, confidence, expected_overall_state):
    mock_log_info = mocker.patch.object(decision_engine.logger, "info")
    decision_engine.declare(BatteryStatus(percent=percent))
    decision_engine.declare(SensorAnomalyStatus(confidence=confidence))
    decision_engine.run()
    mock_log_info.assert_any_call(expected_overall_state)

# Test actions for all overall state values

@pytest.mark.parametrize("state, expected_log", [
    (0, "Action: Continue mission"),
    (1, "Action: Consider returning to home soon"),
    (2, "Action: Plan to return to home immediately"),
    (3, "Action: Emergency landing is advised"),
])
def test_actions_for_overall_states(decision_engine, mocker, state, expected_log):
    # Directly manipulating OverallState for simplicity; in a real scenario, this would be set by rules
    mock_log_info = mocker.patch.object(decision_engine.logger, "info")
    decision_engine.update_state(OverallState, state)
    decision_engine.run()
    # Check if the expected message part is present in any of the logged messages, ignoring color codes
    log_messages = [call_args[0][0] for call_args in mock_log_info.call_args_list]  # Extracts logged messages
    assert any(expected_log in message for message in log_messages)