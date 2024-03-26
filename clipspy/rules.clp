; Initialize state facts to normal
(deffacts initial-states
    (BatteryState (state_value 0) (state_description "Normal"))
    (SensorAnomalyState (state_value 0) (state_description "Normal"))
    (OverallState (state_value 0) (state_description "Normal")))


; Function to map state value to state description
(deffunction getStateDescription (?state-value)
    (if (eq ?state-value 0) then
        (return "Normal")
    else
        (if (eq ?state-value 1) then
            (return "Mild")
        else
            (if (eq ?state-value 2) then
                (return "Severe")
            else
                (if (eq ?state-value 3) then
                    (return "Critical")
                else
                    (return "Unknown"))))))


; Rules for setting BatteryState based on BatteryStatus percentage
(defrule battery_state_normal
    (BatteryStatus (percent ?p&:(> ?p 75)))
    ?f <- (BatteryState (state_value ?v&:(neq ?v 0))) ;; Bind the BatteryState fact to ?f and check if current state_value is not equal to the new state value
    =>
    (modify ?f (state_value 0) (state_description "Normal"))
    (printout t "Battery State 0: Normal" crlf))

(defrule battery_state_mild
    (BatteryStatus (percent ?p&:(> ?p 50) &:(<= ?p 75)))
    ?f <- (BatteryState (state_value ?v&:(neq ?v 1))) ;; Check if current state_value is not equal to the new state value
    =>
    (modify ?f (state_value 1) (state_description "Mild"))
    (printout t "Battery State 1: Mild" crlf))

(defrule battery_state_severe
    (BatteryStatus (percent ?p&:(> ?p 25) &:(<= ?p 50)))
    ?f <- (BatteryState (state_value ?v&:(neq ?v 2))) ;; Check if current state_value is not equal to the new state value
    =>
    (modify ?f (state_value 2) (state_description "Severe"))
    (printout t "Battery State 2: Severe" crlf))

(defrule battery_state_critical
    (BatteryStatus (percent ?p&:(<= ?p 25)))
    ?f <- (BatteryState (state_value ?v&:(neq ?v 3))) ;; Check if current state_value is not equal to the new state value
    =>
    (modify ?f (state_value 3) (state_description "Critical"))
    (printout t "Battery State 3: Critical" crlf))


; Rules for setting SensorAnomalyState based on SensorAnomalyStatus confidence
(defrule sensor_anomaly_state_normal
    (SensorAnomalyStatus (confidence ?c&:(<= ?c 0.25)))
    ?f <- (SensorAnomalyState (state_value ?v&:(neq ?v 0)))
    =>
    (modify ?f (state_value 0) (state_description "Normal"))
    (printout t "Sensor Anomaly State 0: Normal" crlf))

(defrule sensor_anomaly_state_mild
    (SensorAnomalyStatus (confidence ?c&:(> ?c 0.25) &:(<= ?c 0.5)))
    ?f <- (SensorAnomalyState (state_value ?v&:(neq ?v 1)))
    =>
    (modify ?f (state_value 1) (state_description "Mild"))
    (printout t "Sensor Anomaly State 1: Mild" crlf))

(defrule sensor_anomaly_state_severe
    (SensorAnomalyStatus (confidence ?c&:(> ?c 0.5) &:(<= ?c 0.75)))
    ?f <- (SensorAnomalyState (state_value ?v&:(neq ?v 2)))
    =>
    (modify ?f (state_value 2) (state_description "Severe"))
    (printout t "Sensor Anomaly State 2: Severe" crlf))

(defrule sensor_anomaly_state_critical
    (SensorAnomalyStatus (confidence ?c&:(> ?c 0.75)))
    ?f <- (SensorAnomalyState (state_value ?v&:(neq ?v 3)))
    =>
    (modify ?f (state_value 3) (state_description "Critical"))
    (printout t "Sensor Anomaly State 3: Critical" crlf))


; Rule for determining the OverallState based on the highest severity level
; between BatteryState and SensorAnomalyState
(defrule determine-and-update-overall-state
    ?b <- (BatteryState (state_value ?batteryState))
    ?s <- (SensorAnomalyState (state_value ?sensorState))
    ?o <- (OverallState (state_value ?overallState))
    =>
    (bind ?newOverallState (max ?batteryState ?sensorState))
    (if (neq ?overallState ?newOverallState) then
        (modify ?o (state_value ?newOverallState) (state_description (getStateDescription ?newOverallState)))
        (printout t "Overall State " ?newOverallState ": " (getStateDescription ?newOverallState) crlf)))


; Rules to fire actions according to overall state
(defrule action_normal
    (OverallState (state_value 0))
    =>
    (action_for_normal_state))

(defrule action_mild
    (OverallState (state_value 1))
    =>
    (action_for_mild_state))

(defrule action_severe
    (OverallState (state_value 2))
    =>
    (action_for_severe_state))

(defrule action_critical
    (OverallState (state_value 3))
    =>
    (action_for_critical_state))






