# Konfiguration

Die SDK-Policy bestimmt die fachliche Methode. Dateikonfigurationen teilen Angaben vollständig in `algorithm`, `budget`, `execution` und `recording` auf. Fehlende oder unbekannte Felder werden nicht durch alte experimentelle Defaults ergänzt.

| Bereich | Parameter | Bedeutung |
|---|---|---|
| algorithm | query_strategy | fixed oder reduction_per_query |
| algorithm | depth | Feste Tiefe beziehungsweise größter adaptiver Horizont, eins bis drei |
| algorithm | higher_depth_query_source | grid oder both, oberhalb der letzten Ebene |
| algorithm | grid_size | Positive ganzzahlige Gridgröße |
| algorithm | planning_evaluation | candidate_count oder stop_aware |
| algorithm | stopping | single_candidate oder volume_confidence mit threshold in (0,1] |
| budget | max_queries | Positive Gesamtantwortgrenze einschließlich Anfangshistorie oder null |
| execution | workers | Positive Zahl der unabhängigen Rootbewertungsworker |
| execution | cache_policy_id | bounded_v1, unabhängig vom Querybudget |

`SolverExecution` erhält optional einen lokalen Multiprocessingkontext. Standard für benötigte Pools ist forkserver; die Library setzt keinen globalen Startmodus und keine nativen Threadvariablen. Der Laufzeitadapter erfasst und prüft den tatsächlichen Threadrahmen vor numerischen Imports. Supervisorzeitlimit und Aufzeichnungseinstellungen gehören zur Dateilaufzeit, nicht zur mathematischen SDK-Policy.

Die Antwortwahrscheinlichkeit ist fest geometrisch. Es gibt keinen auswählbaren Samplingmodus. Auf der letzten Planungsebene entstehen Ratioqueries unabhängig von der höheren Queryquelle.

Die Matrix bestimmt Ziele und Alternativen. Simulationsgewichte oder ein Replay sind separate Eingaben des Antwortgebers. Gleiche Policy allein bestimmt bei unterschiedlichen Antworten nicht denselben Verlauf.
