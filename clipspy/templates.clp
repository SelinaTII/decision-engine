(deftemplate BatteryStatus
    (slot percent (type FLOAT)))

(deftemplate SensorAnomalyStatus
    (slot confidence (type FLOAT)))

(deftemplate BatteryState
    (slot state_value (type INTEGER))
    (slot state_description (type STRING)))

(deftemplate SensorAnomalyState
    (slot state_value (type INTEGER))
    (slot state_description (type STRING)))

(deftemplate OverallState
    (slot state_value (type INTEGER))
    (slot state_description (type STRING)))