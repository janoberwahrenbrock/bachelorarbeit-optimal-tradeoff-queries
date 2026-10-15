# Bachelorarbeit: Optimal Tradeoff Queries

Pythonprojekt zur Untersuchung des Optimal Tradeoff Query Algorithmus mit reproduzierbaren Benchmarkläufen. Das installierbare Paket und das Kommandozeilenprogramm heißen `otqa`.

## Projektstand

Der Solver unterstützt feste und adaptive Planung bis Tiefe drei, geometrische Antwortwahrscheinlichkeiten ohne Sampling, Singleton- und Volumenkonfidenzabbruch sowie die Berücksichtigung des Abbruchs in der Planung. Die adaptive Strategie maximiert die erwartete Kandidatenverringerung pro erwarteter Query.

Die integrierte Implementierung wird derzeit abgenommen. Den tatsächlich geprüften Umfang und offene Punkte beschreibt [der Implementierungsstatus](docs/implementation-status.md). Ein bestandener Betriebstest ist keine allgemeine Aussage über die Laufzeit aller Konfigurationen.

## Einstieg

Benötigt werden Python 3.13 oder 3.14 und eine eigene virtuelle Umgebung. Eine Entwicklungsinstallation erhält man mit:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install pip==26.2.1
.venv/bin/python -m pip install -e . --group dev
.venv/bin/python -m pytest
.venv/bin/otqa --help
```

Für dauerhafte CLI- und Benchmarkläufe wird das gebaute Wheel installiert und auf dem Ausführungshost nativ qualifiziert. [Installation und Entwicklung](docs/development.md) und [CLI](docs/cli.md) beschreiben die Schritte.

Die dateiunabhängige Python-API benötigt keine Profildatei:

```python
from otqa import AlgorithmPolicy, Problem, SingleCandidateStop, solve
from otqa.answers import SimulatedAnswers

problem = Problem(((0.9, 0.2), (0.3, 0.8), (0.6, 0.5)))
policy = AlgorithmPolicy("reduction_per_query", 2, "both", 5,
                         "candidate_count", SingleCandidateStop())
result = solve(problem, policy, SimulatedAnswers((0.7, 0.3)))
print(result.termination_reason, result.query_counts.answered_total)
```

## Dokumentation

- [Architektur](docs/architecture.md), [Algorithmus](docs/algorithm.md), [Parameter](docs/configuration.md) und [Python-API](docs/python_api.md)
- [Benchmarkverfahren](docs/benchmarks.md), [CLI](docs/cli.md), [gespeicherte Artefakte](docs/artifacts.md) und [portable Archive](docs/seal.md)
- [Numerik](docs/numerical_behavior.md), [Laufzeitprüfung](docs/performance.md) und [Entwicklung](docs/development.md)
- [Vollständige Konfigurationsbeispiele](examples/README.md)

## Projekt und Laufdaten

`otqa-project.json` kennzeichnet den Projektroot mit einer stabilen Projekt-ID.

Neue Einzelläufe und Benchmarkserien werden im Projekt unter `runs/<run-id>/` beziehungsweise `runs/<series-id>/` gespeichert. Die Laufdaten sollen Eingaben, Konfigurationen, Fortschritt, einzelne Versuche, Rohresultate und Auswertungen nachvollziehbar erhalten.

Datasetgenerierung und Suiteanlage speichern neue Eingaben unter `inputs/`. Ein Serienplan friert die gespeicherten Inputs ein. Wiederaufnahme erhält alte Versuche und startet einen neuen Versuch erst nach geklärtem Prozessende. Audit und Export unterscheiden vollständige, ungelöste, fehlerhafte und unterbrochene Ergebnisse.
