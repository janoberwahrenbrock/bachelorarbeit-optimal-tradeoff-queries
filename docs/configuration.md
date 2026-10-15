# Konfiguration

Eine Ausführung besteht aus vier getrennten Entscheidungen: **fachliche Policy**, **Budget tatsächlicher Antworten**, **Ausführung** und **Aufzeichnung**. Die Alternativenmatrix und die Antworten sind zusätzliche Eingaben. Dieselbe Policy allein legt deshalb noch keinen vollständigen Queryverlauf fest.

Die Python-API verwendet unveränderliche Konfigurationsobjekte. Native JSON-Dateien bilden die gleichen fachlichen Entscheidungen ab und ergänzen die kontrollierte Dateilaufzeit. Die vollständigen Schemata liegen unter [`src/otqa/schemas`](../src/otqa/schemas/).

## Fachliche Policy

`AlgorithmPolicy` hat sechs erforderliche Argumente und keine impliziten fachlichen Defaults:

| Parameter | Zulässige Werte | Bedeutung |
| --- | --- | --- |
| `query_strategy` | `"fixed"`, `"reduction_per_query"` | Feste Planungstiefe oder adaptive erwartete Verringerung pro Query. |
| `depth` | Ganzzahl `1`, `2`, `3` | Bei `fixed` die verwendete Tiefe; adaptiv werden alle Horizonte von `1` bis `depth` ausgewertet. |
| `higher_depth_query_source` | `"grid"`, `"both"` | Oberhalb der letzten Planungsebene nur Grid oder Grid plus Ratioqueries. |
| `grid_size` | Ganzzahl mindestens `1` | Anzahl logarithmischer Gridwerte; bestimmt keine Obergrenze der insgesamt gestellten Fragen. |
| `planning_evaluation` | `"candidate_count"`, `"stop_aware"` | Kandidatenbewertung oder Bewertung mit der aktiven Stopregel; die festgelegten Singleton-Rechenpfade bleiben erhalten. |
| `stopping` | `SingleCandidateStop()` oder `VolumeConfidenceStop(threshold)` | Tatsächliches Ende bei einem Kandidaten beziehungsweise zusätzlich bei ausreichendem Volumenanteil. |

`threshold` ist eine endliche Zahl mit `0 < threshold <= 1`. Ein Wert von `.95` bedeutet einen Anteil von mindestens 95 Prozent, nicht die Zahl `95`. Die Grenze ist einschließlich. Auch bei `VolumeConfidenceStop(1.0)` bleibt die Stopregel semantisch eine Volumenregel; `SingleCandidateStop()` bezeichnet ausdrücklich genau einen verbleibenden Kandidaten.

Die Wahl der Bewertungsroute bleibt auch ohne Volumenschwelle ausdrücklich:
Adaptive Singletonplanung mit `stop_aware` behält ihren eigenen festgelegten
Rechenpfad einschließlich Kandidaten-/Recovery-/Akkumulationsschritten. Feste
Singletonplanung mit `stop_aware` delegiert auf den gewöhnlichen Fixed-Pfad.

Auf der letzten Planungsebene werden immer Ratioqueries verwendet, auch bei `higher_depth_query_source="grid"`. Grid-only ändert die zulässige Querymenge und kann deshalb andere Verläufe oder `no_query` erzeugen. Es ist keine reine Performanceoption.

Antwortwahrscheinlichkeiten werden fest geometrisch ohne Sampling berechnet. Gridgrenzen, Ratioepsilon und numerische Toleranzen gehören zum aktiven numerischen Profil; sie sind keine weiteren Policyargumente. Die Unterschiede der Strategien erklärt [Algorithmus](algorithm.md).

## SDK-Budget und Ausführung

| Objekt/Parameter | SDK-Default | Einschränkung und Wirkung |
| --- | --- | --- |
| `QueryBudget.max_queries` | `None` | Unbeschränkt oder Ganzzahl mindestens `1`. Zählt **alle akzeptierten Antworten einschließlich `initial_answers`**. |
| `SolverExecution.workers` | `1` | Ganzzahl mindestens `1`. Parallelisiert unabhängige Querybewertungen auf Rootebene. |
| `SolverExecution.multiprocessing_context` | `None` | Optional ein lokales `multiprocessing`-Kontextobjekt. `None` überlässt die Auswahl dem Python-Executor. |
| `SolverExecution.cache_policy_id` | `"bounded_v1"` | Einzige unterstützte Cachepolicy; Kapazitäten hängen nicht vom Querybudget ab. |

Ganzzahlige Steuerwerte akzeptieren weder Booleans noch Floatwerte wie `2.0`. Die API setzt weder die globale Multiprocessing-Startmethode noch Threadumgebungsvariablen. Wer mehrere Worker verwendet, sollte den Aufruf in einem ausführbaren Modul unter `if __name__ == "__main__":` starten und bei Bedarf einen passenden lokalen Kontext ausdrücklich übergeben. Ein Ein-Worker-Aufruf benötigt keinen Prozesspool.

Das Querybudget ist keine maximale Planungstiefe und kein Zeitlimit. Erreicht die Anfangshistorie bereits das Budget, wird zunächst dieser Zustand analysiert; danach greift die tatsächliche Stopregel oder die Budgetrückgabe. Es wird keine zusätzliche Query geplant, um das Ende festzustellen. Singleton und Konfidenz werden vor dem Budget geprüft.

```python
from otqa import AlgorithmPolicy, QueryBudget, SolverExecution, VolumeConfidenceStop

policy = AlgorithmPolicy(
    query_strategy="reduction_per_query",
    depth=3,
    higher_depth_query_source="both",
    grid_size=5,
    planning_evaluation="stop_aware",
    stopping=VolumeConfidenceStop(.99),
)
budget = QueryBudget(max_queries=30)
execution = SolverExecution(workers=1)
```

## Native Dateikonfiguration

Ein `ConfigDoc` benötigt `schema_version`, `configuration_id` und alle vier Bereiche `algorithm`, `budget`, `execution`, `recording`. Sämtliche unten gezeigten Felder sind erforderlich. Es gibt beim Einlesen keine automatische Ergänzung fehlender Werte; unbekannte Felder werden abgelehnt.

```json
{
  "schema_version": 1,
  "configuration_id": "adaptive-h3-confidence99",
  "algorithm": {
    "query_strategy": "reduction_per_query",
    "depth": 3,
    "higher_depth_query_source": "both",
    "grid_size": 5,
    "planning_evaluation": "stop_aware",
    "stopping": {"rule": "volume_confidence", "threshold": 0.99}
  },
  "budget": {"max_queries": null},
  "execution": {
    "workers": 8,
    "start_method": "forkserver",
    "native_threads": 1,
    "case_timeout_seconds": null,
    "cache_policy_id": "bounded_v1"
  },
  "recording": {
    "durability": "per_answer",
    "trace_level": "standard",
    "profile": false,
    "telemetry_failure_policy": "continue"
  }
}
```

Für Singletonstopp lautet das komplette Stopobjekt `{"rule": "single_candidate"}`; es enthält dann kein `threshold`.

### Zusätzliche Ausführungsfelder der Dateilaufzeit

| Feld | Zulässiger Wert | Vertrag |
| --- | --- | --- |
| `start_method` | `"forkserver"` | Expliziter nativer Laufzeitvertrag, unabhängig vom SDK-Default `None`. |
| `native_threads` | Ganzzahl mindestens `1` | Wird vor numerischen Imports als Threadrahmen gesetzt und geprüft; die konkrete Zahl stammt aus dieser Konfiguration, nicht aus einer im Ausführungsprofil festgeschriebenen Threadzahl. |
| `case_timeout_seconds` | `null` oder endliche positive Zahl | Supervisorgrenze für einen Versuch. Ein Timeout ist keine gelöste mathematische Rückgabe. |

Die Dateilaufzeit prüft Quelle, numerisches Profil, Bibliotheken, Backendfähigkeiten und tatsächlichen Ausführungsrahmen. Eine Konfigurationsdatei ersetzt kein gültiges Ausführungsprofil. Die SDK-Policy besitzt diese Umgebungsfelder bewusst nicht.

### Aufzeichnung

| Feld | Zulässige Werte | Wirkung |
| --- | --- | --- |
| `durability` | `"per_answer"` | Erforderliche synchrone native Aufzeichnung und Bestätigung der Antworten. |
| `trace_level` | `"standard"`, `"full"` | Umfang der gespeicherten Planungsevidenz; `full` serialisiert zusätzlich bereits vorhandene Fortsetzungen der ausgewählten Planung, soweit diese gehalten wurden. |
| `profile` | `false`, `true` | Optionales `cProfile` des öffentlichen Solveraufrufs im Caseparent, mit gespeicherten Rohberichten. |
| `telemetry_failure_policy` | `"continue"`, `"abort"` | Verhalten bei Fehlern der optionalen Anzeige; kein Freibrief, erforderliche Persistenzfehler zu ignorieren. |

`full` erzwingt keine zusätzliche Berechnung oder Retention. Es bedeutet nicht, dass jede verworfene hypothetische Berechnung dauerhaft gespeichert wird. Beim gewöhnlichen Fixed-Pfad können Fortsetzungskinder deshalb `null` bleiben, obwohl Rootaggregate vorhanden sind. Eine interne vollständige Berechnungserfassung hat einen eigenen begrenzten Diagnosevertrag. Ebenso profiliert `profile=true` die Worker nicht automatisch; inklusive Parentfunktionszeiten sind keine exklusive Phasenzerlegung.

Bei `continue` wird ein optionaler Anzeigefehler dokumentiert und die Anzeige abgeschaltet. Kann die erforderliche Fehlerdokumentation selbst nicht veröffentlicht werden, propagiert der Fehler. Recorder- und Persistenzfehler werden unabhängig von dieser Option nicht verschluckt.

Im direkten SDK-Aufruf gibt es kein `recording`-Argument. Dort werden `recorder` und `observer` ausdrücklich übergeben; ohne diese schreibt der mathematische Solver keine Laufdateien. Persistente Läufe beschreibt der [Benchmarkworkflow](benchmarks.md), die Callbackverträge die [Python-API](python_api.md).
