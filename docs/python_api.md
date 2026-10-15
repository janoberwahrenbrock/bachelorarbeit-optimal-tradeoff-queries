# Python-API

Das Paket exportiert `Problem`, `Query`, `Answer`, `AnsweredQuery`, `AlgorithmPolicy`, `SingleCandidateStop`, `VolumeConfidenceStop`, `QueryBudget`, `SolverExecution`, `SolverEvent`, `SolveResult` und `solve`. Der öffentliche Import startet keine Prozesse und importiert keine numerischen Bibliotheken.

```python
import otqa
from otqa.answers import SimulatedAnswers

problem = otqa.Problem(((0.9, 0.2, 0.4), (0.3, 0.8, 0.5), (0.5, 0.4, 0.9)))
policy = otqa.AlgorithmPolicy(
    query_strategy="fixed",
    depth=2,
    higher_depth_query_source="both",
    grid_size=5,
    planning_evaluation="candidate_count",
    stopping=otqa.SingleCandidateStop(),
)
result = otqa.solve(
    problem,
    policy,
    SimulatedAnswers((0.6, 0.3, 0.1)),
    budget=otqa.QueryBudget(max_queries=30),
    execution=otqa.SolverExecution(workers=1),
)
print(result.termination_reason, result.query_counts.answered_new)
```

Ein eigener Antwortgeber erhält nur die ausgewählte unveränderliche Query und liefert genau eines der Literale `<`, `>` oder `=`. Provider werden synchron im Solverparent aufgerufen. Initialantworten können über `initial_answers` ausdrücklich mitgegeben werden; sie werden unverändert geordnet übernommen und zählen zum Budget.

`recorder` und `observer` erhalten unveränderliche fachliche Ereignisse. Für jede Frage folgen Plan, Dispatch, akzeptierte Antwort, analysierter Folgezustand und abgeschlossener Queryrecord. Erst nach erfolgreichem Session-/Poolcleanup folgt `SolveFinished`. Recorder wird jeweils vor Observer aufgerufen. Ihre Fehler propagieren mit Originalursache; es gibt keine automatische Providerwiederholung.

Normale Ergebnisse unterscheiden Singleton, Konfidenz, fehlende Query und ausgeschöpftes Budget. Fehler unter `otqa.errors` tragen nach Laufbeginn den akzeptierten In-Memory-Partialkontext. Dieser ist kein Nachweis dauerhafter Dateipersistenz. `KeyboardInterrupt` und `SystemExit` werden nicht in gewöhnliche Callbackfehler umgewandelt.

Benutzerkennungen, Dateipfade, Lauf-IDs, Zeitmessungen und Qualitätswahrheit gehören zum Anwendungslauf. Die fachliche API kennt diese Angaben nicht.
