# Python-API

Die öffentliche synchrone API löst ein Problem aus einer geordneten Alternativenmatrix, einer Policy und einem Antwortgeber. Sie benötigt keine Projektdateien, Lauf-IDs, Anzeigelabels oder Qualitätsoracle. `import otqa` startet keine Prozesse, lädt keine numerischen Bibliotheken und verändert die Prozessumgebung nicht.

## Vollständiger Aufruf

```python
import otqa
from otqa.answers import SimulatedAnswers

problem = otqa.Problem(((1., 0.), (0., 1.), (.6, .6)))
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
    SimulatedAnswers((.9, .1)),
    budget=otqa.QueryBudget(max_queries=16),
    execution=otqa.SolverExecution(workers=1),
)
print(result.termination_reason, result.selected_candidate_index)
print(result.query_counts.answered_new)
```

Der Vertrag lautet:

```text
solve(
    problem,
    policy,
    answer_provider,
    *,
    budget=QueryBudget(),
    execution=SolverExecution(),
    initial_answers=(),
    continuation=None,
    recorder=None,
    observer=None,
) -> SolveResult
```

Die Typen `Problem`, `Query`, `Answer`, `AnsweredQuery`, `AlgorithmPolicy`, `SingleCandidateStop`, `VolumeConfidenceStop`, `QueryBudget`, `SolverExecution`, `SolverEvent` und `SolveResult` sind aus `otqa` importierbar. Weitere Ergebnis- und Ereignistypen liegen in `otqa.models`, Fehler in `otqa.errors`. Parametergrenzen und SDK-Defaults stehen in [Konfiguration](configuration.md).

## Problem und Query

`Problem(alternatives)` übernimmt eine eigene unveränderliche Tuplematrix. Zeilen sind Alternativen, Spalten Ziele, alle Werte endliche reelle Zahlen in `[0,1]`. Die Matrix muss rechteckig sein und mindestens eine Zeile und Spalte besitzen. Zeilenreihenfolge und Originalindizes bleiben erhalten; Werte werden nicht normalisiert.

Eine `Query(goal_index_a, goal_index_b, value)` bedeutet `w[a] ? value * w[b]`. Die Indizes sind verschieden und nichtnegativ; `value` ist endlich und nichtnegativ. Beim Solveraufruf werden Indizes gegen das konkrete Problem geprüft. Binary64werte einschließlich `-0.0` bleiben erhalten. Die Matrixform mit nur einem Ziel ist zulässig, führt im festgelegten Ratioverfahren jedoch zur dokumentierten leeren Kandidatenanalyse und zu `PlanningInvariantError`; der Solver fügt dafür keine andere Auswahlmethode hinzu.

## Antwortgeber

Der Provider ist ein synchrones Callable `Query -> Answer`. Es erhält nur die ausgewählte unveränderliche Query, keine Gewichtsschätzung oder vorgegebene Gewinneralternative. Es wird im Solverparent aufgerufen, nicht in den Bewertungsworkern. Rückgabewerte sind genau die Strings `"<"`, `">"`, `"="`; Leerzeichen oder andere Schreibweisen werden nicht automatisch korrigiert.

| Provider aus `otqa.answers` | Eingabe und Verhalten |
| --- | --- |
| `SimulatedAnswers(weights)` | Endliche nichtnegative Gewichte mit endlicher positiver Summe. Vergleicht unveränderte Gewichte per Multiplikation; keine vorherige Normalisierung und keine Division durch ein Nullgewicht. |
| `ReplayAnswers(answers)` | Geordnete `AnsweredQuery`-Folge. Akzeptiert nur die tatsächlich erwartete Queryidentität aus Indizes und `value.hex()`; Abweichung oder erschöpfte Folge führt zum Fehler. `consumed` zählt verbrauchte Antworten. |
| `InteractiveAnswers(read=input)` | Fragt über das übergebene Read-Callable und akzeptiert die Antwortliterale streng. |

Eigene Provider können beispielsweise auf eine Benutzeroberfläche oder eine externe Entscheidungsquelle zugreifen. Ein Providerfehler löst keine automatische Wiederholung aus.

## Anfangshistorie und Zähler

```python
from otqa import AnsweredQuery, Query

history = (AnsweredQuery(Query(0, 1, .91), ">"),)
```

`initial_answers=history` übernimmt die explizite Reihenfolge. Es werden Typen und Queryindizes geprüft und der daraus resultierende Zustand tatsächlich analysiert. Eine widersprüchliche Historie wird nicht still repariert. Für ein Replay müssen die danach geplanten Queries erneut passen; eine Antwortdatei ersetzt keine beliebige Query durch eine andere.

`QueryCounts` trennt vier Größen:

| Feld | Bedeutung |
| --- | --- |
| `initial_answers` | Länge der übernommenen Anfangshistorie. |
| `dispatched_new` | In diesem Aufruf an den Provider dispatchte Fragen. |
| `answered_new` | In diesem Aufruf akzeptierte Antworten. |
| `answered_total` | `initial_answers + answered_new`. Diese Größe zählt zum Querybudget. |

Es gilt `answered_new <= dispatched_new`. Bei einem Providerfehler kann eine dispatchte Frage ohne akzeptierte Antwort offen sein. Nach einer akzeptierten Antwort können außerdem die Folgeanalyse oder die Aufzeichnung scheitern; der Partialkontext unterscheidet deshalb Antworten, abgeschlossene Queryrecords und eine offene Query.

Bei Countdown beginnt `initial_answers` einen frischen vollständigen Block.
Die nächste Phase folgt aus einem expliziten `ExecutionCursor`, nicht aus der
Antwortzahl modulo Tiefe.

Eine echte algorithmische Fortsetzung übernimmt geordnete Antworten und Cursor
mit unveränderter Problem-/Policybindung:

```python
continuation = otqa.continuation_from_result(problem, policy, result)
continued = otqa.solve(problem, policy, SimulatedAnswers((.9, .1)),
                       continuation=continuation)
```

`SolveContinuation(problem, policy, answers, execution_cursor)` kann auch explizit
konstruiert werden. Strukturell gültige SDK-Eingaben sind Erklärungen des
Aufrufers, kein historischer Ereignisbeweis. Der Ergebnishelper prüft die Bindung
an das tatsächlich gelöste Problem und die verwendete Policy. Eine Continuation
und eine nichtleere zusätzliche Anfangshistorie schließen einander aus.
Unpassende Policy, Problem, Cursor oder Historienlänge werden abgewiesen.

Ein unbeantworteter Dispatch ist nicht fortsetzbar. Eine akzeptierte Antwort kann
auch vor abgeschlossener Folgeanalyse oder Queryrecordfertigstellung fortgesetzt
werden. Der SDK-Kontext ist dabei kein Dauerhaftigkeitsnachweis. Die native
Continuation verlangt zusätzlich einen geprüften unveränderlichen Journalpräfix
sowie passende Quell- und Umgebungsbindung; siehe [CLI](cli.md).

## Ergebnisse und Planungsevidenz

`SolveResult` ist unveränderlich und enthält:

- `solved`, `exactly_solved`, `termination_reason` sowie die ausgewählte Originalzeile und deren Volumen/Anteil;
- `final_state` mit Originalkandidaten, Kandidatenvolumen und unveränderten Anteilen;
- `answers` einschließlich Anfangshistorie und `queries` mit den neu abgeschlossenen `QueryRecord`-Werten;
- `query_counts` mit den vier getrennten Zählern;
- `execution_cursor` und `planning_cycles` mit tatsächlichen Versuchen, Fortschrittswerten, verworfenen Restplänen und gegebenenfalls voller Ersatzplanung.

Jeder neue Queryrecord bindet `query`, `answer`, `before`, `after`, `planning` und seinen `planning_cycle`. Die Planung enthält die gewählte Query, den Horizont, Score, Antwortwahrscheinlichkeiten und die tatsächlich aufbewahrte Horizont-/Fortsetzungsevidenz. `FixedScore` hält Kandidatenerwartung, bewerteten Loss und das tatsächlich berechnete lexikographische Profil. `FixedScore.expected_queries` kann im Stop-aware-Pfad zusätzlich als diagnostischer Wert vorliegen; Fixed verwendet ihn nicht als Ratenkriterium. `EfficiencyScore` enthält die erforderliche erwartete Queryzahl, Gewinn und Rate. Nicht berechnete flachere Werte werden nicht als Nullwerte erfunden.

Der gespeicherte Planungshorizont ist der für diese Query tatsächlich verwendete
Horizont. Bei Countdown kann er deshalb kleiner als `policy.depth` sein. Die
Queryrecords erlauben es, die Folge `2 → 1 → …` beziehungsweise `3 → 2 → 1 → …`
nachzuvollziehen, ohne einen gespeicherten Entscheidungsbaum vorauszusetzen.

Diese Rückgabe ist kein vollständiger Suchbaum. Der gewöhnliche Fixed-Pfad behält keine expliziten Childfortsetzungen für jede Rootquery. Adaptive Horizonte enthalten ihre Rootbewertungen und den besten Score je Horizont, aber nicht automatisch Kosten und Rate jeder verworfenen Rootoption. Eine vollständige interne Berechnungserfassung hat einen getrennten begrenzten Diagnosevertrag; `solve` bietet dafür keinen zusätzlichen öffentlichen Parameter.

| `termination_reason` | Ergebnis |
| --- | --- |
| `exact_single_candidate` | `solved=True`, `exactly_solved=True`, genau ein Kandidat. |
| `volume_confidence` | `solved=True`; weitere Kandidaten können verbleiben. |
| `no_query` | Regulär ungelöst: keine zulässige nächste Query vorhanden. |
| `insufficient_expected_progress` | Regulär ungelöst: kein vollständiger bewerteter Plan überschreitet die aktive Fortschrittsschwelle. |
| `max_questions` | Regulär ungelöst: Gesamtantwortbudget erreicht. |

Die tatsächliche Prüfungsreihenfolge ist Singleton, Konfidenz, Budget, nächste Planung. Bei gleichen maximalen Konfidenzanteilen gewinnt der kleinere ursprüngliche Zeilenindex. Der SDK kennt keine Simulationswahrheit: `solved=True` ist keine unabhängige Qualitätsprüfung gegen verborgene Zielgewichte.

## Recorder und Observer

Beide optionalen Callables erhalten `SolverEvent`-Werte synchron. Für jedes Ereignis läuft zuerst `recorder`, danach `observer`. Die normale Folge lautet:

```text
StateAnalyzed(initial)
  PlanningAttemptStarted
  PlanningAttemptCompleted
  ... gegebenenfalls einmaliger voller Ersatzversuch ...
  PlanningResolved
  QueryPlanned
  QueryDispatched
  AnswerReceived
  StateAnalyzed(after)
  QueryCompleted
  ... weitere Fragen ...
SolveFinished
```

Ein initial bereits terminaler Zustand erzeugt nur die initiale Zustandsanalyse und den erfolgreichen Abschluss. `SolveFinished` wird erst nach erfolgreichem Session-/Poolcleanup veröffentlicht. Ein späterer Callbackfehler kann deshalb den normalen Return verhindern, auch wenn die fachliche Rechnung bereits beendet war.

Der SDK schreibt selbst keine Dateien. Ein Recorder muss benötigte Persistenz implementieren; die Existenz eines In-Memory-Ereignisses beweist keinen dauerhaften Schreibvorgang. Die native Dateilaufzeit stellt dafür einen eigenen geprüften Recorder bereit.

## Fehler und Lebenszyklus

| Kategorie aus `otqa.errors` | Typischer Auslöser |
| --- | --- |
| `InputValidationError`, `InvalidAnswerError` | Ungültige Eingabe beziehungsweise ein ungültiges zurückgegebenes Antwortliteral. |
| `InfeasibleStateError` | Akzeptierte Antworten ergeben keinen zulässigen Gewichtsraum. |
| `NumericalError` | Ein erforderliches numerisches Ergebnis lässt sich nicht validiert bestimmen. |
| `PlanningInvariantError` | Verletzte fachliche Planungs-/Zustandsinvariante, etwa leere Kandidaten in einem machbaren tatsächlichen Zustand. |
| `AnswerProviderError` | Provider hat eine Exception ausgelöst; Originalursache ist verkettet. |
| `RecorderError`, `ObserverError` | Fehler im entsprechenden synchronen Callback. |
| `ExecutionContextError` | Fehler beim eigenen Worker-/Sessionlebenszyklus. |

`SolverError.context` beziehungsweise `partial_context` enthält nach Laufbeginn den akzeptierten unveränderlichen In-Memory-Partialkontext: letzten Zustand, Antworten, Queryrecords, Zähler, offene Query, algorithmischen Cursor und den gegebenenfalls begonnenen Planungszyklus. Bei früher Eingabevalidierung kann er fehlen. Er ist kein Nachweis dauerhafter Dateipersistenz. Aus einer gültigen akzeptierten Antwortgrenze kann die ausdrückliche SDK-Continuation gebildet werden.

Der Solver schließt seine eigenen Ressourcen auch auf Fehlerpfaden. Zusätzliche Cleanupfehler verdrängen die ursprüngliche Ursache nicht. `KeyboardInterrupt` und `SystemExit` bleiben Kontrollabbrüche und werden nicht in gewöhnliche Provider-/Callbackfehler umgewandelt. Eine Fortsetzung mit gespeicherten Artefakten gehört zum [Benchmarkworkflow](benchmarks.md), nicht zu einer versteckten automatischen Wiederholung des SDK.

Numerische Handles, Caches und Worker gehören jeweils der eigenen Session. Initialisierung unbenutzter Worker erzeugt noch keine numerische Session; diese entsteht beim ersten tatsächlichen Task. Mehrere getrennte SDK-Aufrufe teilen keine mutierbaren Solvercaches. Details und Grenzen beschreibt [Numerische Berechnung](numerical_behavior.md).
