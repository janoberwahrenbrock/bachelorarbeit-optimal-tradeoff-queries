# Konfiguration

Eine Ausführung besteht aus vier getrennten Entscheidungen: **fachliche Policy**, **Budget tatsächlicher Antworten**, **Ausführung** und **Aufzeichnung**. Die Alternativenmatrix und die Antworten sind zusätzliche Eingaben. Dieselbe Policy allein legt deshalb noch keinen vollständigen Queryverlauf fest.

Die Python-API verwendet unveränderliche Konfigurationsobjekte. Native JSON-Dateien bilden die gleichen fachlichen Entscheidungen ab und ergänzen die kontrollierte Dateilaufzeit. Die vollständigen Schemata liegen unter [`src/otqa/schemas`](../src/otqa/schemas/).

## Fachliche Policy

`AlgorithmPolicy` hat sechs erforderliche Argumente. `horizon_execution` ist optional mit Default `"receding"`; das ausschließlich per Schlüsselwort übergebbare `min_expected_progress` hat den Default `0.001`.

| Parameter | Zulässige Werte | Bedeutung |
| --- | --- | --- |
| `query_strategy` | `"fixed"`, `"reduction_per_query"` | Feste Planungstiefe oder adaptive erwartete Verringerung pro Query. |
| `depth` | Ganzzahl `1`, `2`, `3` | Bei `fixed` die Tiefe der Neuplanung beziehungsweise die Blocklänge beim Countdown; adaptiv werden alle Horizonte von `1` bis `depth` ausgewertet. |
| `higher_depth_query_source` | `"grid"`, `"both"` | Oberhalb der letzten Planungsebene nur Grid oder Grid plus Ratioqueries. |
| `grid_size` | Ganzzahl mindestens `1` | Anzahl logarithmischer Gridwerte; bestimmt keine Obergrenze der insgesamt gestellten Fragen. |
| `planning_evaluation` | `"candidate_count"`, `"stop_aware"` | Kandidatenbewertung oder Bewertung mit der aktiven Stopregel; die festgelegten Singleton-Rechenpfade bleiben erhalten. |
| `stopping` | `SingleCandidateStop()` oder `VolumeConfidenceStop(threshold)` | Tatsächliches Ende bei einem Kandidaten beziehungsweise zusätzlich bei ausreichendem Volumenanteil. |
| `min_expected_progress` | Endliche reelle Zahl `>=0` oder `None`; Default `0.001` | Absoluter Mindestgewinn über den vollständigen Planungshorizont; strikter Vergleich. |
| `horizon_execution` | `"receding"` (Default), `"countdown"` | `receding` verwendet nach jeder tatsächlichen Antwort wieder die konfigurierte Tiefe. `countdown` ist ausschließlich für `query_strategy="fixed"` zulässig und zählt die Resttiefe innerhalb eines Blocks herunter. |

Bei fester Tiefe zwei verwendet Countdown regulär `2 → 1 → 2`, bei Tiefe drei
`3 → 2 → 1 → 3`. Ein unveränderlicher `ExecutionCursor` hält die nächste
Resttiefe und die Anzahl akzeptierter Antworten. Eine gültige Antwort auf Horizont
`h>1` setzt die Resttiefe auf `h-1`, auf Horizont eins wieder auf `depth`.
Planungsaufrufe und Dispatches allein verändern die Phase nicht.

Findet ein verkürzter Versuch keine Query oder keinen ausreichenden vollständigen
Plan, folgt im selben tatsächlichen Zustand genau ein Ersatzversuch mit voller
Tiefe. Erst dessen gültig beantwortete Query beginnt einen neuen Block. Fehlschlag
bei voller Tiefe beendet den Lauf regulär mit dem jeweiligen Grund; es gibt keinen
identischen zweiten Versuch. Tatsächliches Ziel und Budget haben vor jeder Planung
Vorrang. Numerik-, Provider- und Recorderfehler sind keine Fallbackauslöser.

Eine Anfangshistorie ist ein Warmstart und beginnt bei voller Tiefe. Nur eine
explizite gebundene Continuation erhält eine vorherige Restphase. Countdown ist
ausschließlich für `fixed` zulässig; adaptive Planung verwendet `receding`.

### Mindestfortschritt

| `min_expected_progress` | Bedeutung |
| --- | --- |
| Nicht angegeben im SDK | `0.001` |
| Endliche reelle Zahl `>=0` | Vollständiger Horizontgewinn muss strikt größer sein. |
| `None` im SDK / `null` in JSON | Fortschrittsprüfung ausdrücklich deaktiviert. |
| `0.0` | Strikt positiven berechneten Gewinn verlangen. |

Negative Werte, Bool, Strings, NaN und Unendlich sind ungültig. Der Gewinn ist
`float(C) - expected_terminal_candidates`, bei abbruchbewusster Bewertung
`float(C) - expected_terminal_loss`. Subtraktion erfolgt vor dem strikten
Vergleich. Genau gleich der Schwelle genügt nicht; es gibt kein `isclose`.
Die Schwelle ist absolut im verwendeten Lossmaß, kein Prozentwert und keine
Rate pro Frage. Sie gilt für den gesamten Plan, nicht separat pro Ast oder
vorbereitendem Schritt. Adaptive Auswahl filtert vollständige Pläne vor der
Ratenwahl; ein verworfener Ratensieger darf einen anderen zulässigen Plan nicht
verbergen. Fehlender ausreichender Fortschritt ergibt
`insufficient_expected_progress`, `solved=False`.

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

Neue native Ausführungen verlangen eine Konfiguration der Version zwei. Alle
gezeigten Felder, einschließlich `horizon_execution` und
`min_expected_progress`, sind ausdrücklich gespeichert. Historische v1-Dateien
bleiben lesbar, starten aber keinen neuen Lauf ohne ausdrückliche Konvertierung.
Unbekannte Felder werden abgelehnt.

```json
{
  "schema_version": 2,
  "configuration_id": "adaptive-h3-confidence99",
  "algorithm": {
    "query_strategy": "reduction_per_query",
    "depth": 3,
    "higher_depth_query_source": "both",
    "grid_size": 5,
    "planning_evaluation": "stop_aware",
    "stopping": {"rule": "volume_confidence", "threshold": 0.99},
    "horizon_execution": "receding",
    "min_expected_progress": 0.001
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

Für eine feste Countdown-Konfiguration ergänze im `algorithm`-Objekt ausdrücklich
`"horizon_execution": "countdown"`. Eine vollständige Vorlage liegt unter
[`examples/configurations/fixed2-countdown-singleton.json`](../examples/configurations/fixed2-countdown-singleton.json).
Der bestehende Fixed-Modus und sämtliche adaptiven Beispiele verwenden weiterhin
`receding`. Adaptiv plus `countdown` wird als ungültige Konfiguration abgelehnt.

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

## Historische Konfiguration ausdrücklich konvertieren

```sh
otqa --project-root "$PWD" config convert \
  --input inputs/old-config.json --output inputs/new-config.json
```

Ohne ausdrückliche Schwellenwahl bleibt die historische Deaktivierung als
`null` erhalten. `--min-expected-progress 0.001` wählt den neuen Default bewusst.
Alte experimentelle Countdownkonfigurationen verlangen zusätzlich
`--accept-countdown-block-semantics`, da die neuen Warmstart- und Neustartregeln
eine andere Ausführungssemantik haben. Die Konvertierung schreibt eine neue
Datei und überschreibt weder Eingaben noch alte Resultate.
