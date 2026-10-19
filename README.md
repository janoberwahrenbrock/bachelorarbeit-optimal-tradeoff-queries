# Bachelorarbeit: Optimal Tradeoff Queries

Implementierung und veröffentlichte Studien zur Bachelorarbeit über die Identifikation optimaler Handlungsalternativen durch Tradeoff-Queries. Das Pythonpaket und das Kommandozeilenprogramm heißen `otqa`.

- [Studien und Rohdaten nach Abschnitten der Bachelorarbeit](studies/README.md)
- [Zuordnung der Studien zu den Kapiteln als CSV](studies/thesis-map.csv) und [als JSON](studies/catalog.json)
- [Code der tatsächlich ausgeführten Studien](https://github.com/janoberwahrenbrock/bachelorarbeit-optimal-tradeoff-queries/tree/62d1d01339f91802e2916b63660a4e640d99c9cc)

## Code und Studienstand

Main enthält den verwendeten Recovery-Code und die **104 aktuellen Studien**. **96 Studien** bilden die Datengrundlage der empirischen Abschnitte 6.2–6.7 der Bachelorarbeit; acht zusätzliche Grid-Vergleiche sind im Katalog gekennzeichnet. Wiederverwendete Probleme und Referenzausführungen werden dort ausdrücklich zugeordnet.

Die wissenschaftliche Quellenbindung bleibt fest:

| Merkmal | Wert |
| --- | --- |
| Gemessener Codecommit | `62d1d01339f91802e2916b63660a4e640d99c9cc` |
| Produktionsquellhash SHA256 | `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e` |
| Numerisches Profil | `otqa-exact-v3` |

Spätere Zusammenführungs- und Dokumentationscommits sind vom gemessenen Codecommit zu unterscheiden. Eingaben, Einzelresultate, Konfigurationen und Quellenbelege liegen in den jeweiligen Studienordnern. Die vollständigen Rohdatenpakete und ihre Prüfsummen stehen in den dort verlinkten GitHub-Releases. GitHubs automatisch erzeugte „Source code“-Archive gehören zum jeweiligen Tag-Commit; für die Reproduktion der Messungen sind der oben verlinkte Codecommit und die eigentlichen Studienpakete maßgeblich.

Der Solver unterstützt feste und adaptive Planung bis Tiefe drei, geometrische Antwortwahrscheinlichkeiten ohne Sampling, Singleton- und Volumenkonfidenzabbruch sowie die Berücksichtigung des Abbruchs in der Planung. Die adaptive Strategie maximiert die erwartete Kandidatenverringerung pro erwarteter Query. Feste Planung unterstützt Neuplanung und Countdown mit einmaliger voller Ersatzplanung. Der Mindestfortschritt beträgt standardmäßig `0.001`.

Regulär ungelöste Fälle, falsche Konfidenzauswahlen und technische Solverfehler bleiben getrennte Ergebnisse. Laufzeitarten und tatsächliche Ausführungsbedingungen sind in den Studienberichten dokumentiert. Der [Implementierungsstatus](docs/implementation-status.md) und die [Laufzeitprüfung](docs/performance.md) beschreiben die Grenzen der technischen Nachweise.

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

Der [Quickstart](docs/quickstart.md) führt von der Installation über zwei neue Probleme bis zu gespeicherten Ergebnissen, Export und Archiv.

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
- [Quickstart](docs/quickstart.md), [Benchmarkverfahren](docs/benchmarks.md), [CLI](docs/cli.md), [gespeicherte Artefakte](docs/artifacts.md) und [portable Archive](docs/seal.md)
- [Numerik](docs/numerical_behavior.md), [Laufzeitprüfung](docs/performance.md) und [Entwicklung](docs/development.md)
- [Vollständige Konfigurationsbeispiele](examples/README.md)
- [Veröffentlichte Studien](studies/README.md) und [Veröffentlichungsverfahren](docs/publication.md)

## Projekt und Laufdaten

`otqa-project.json` kennzeichnet den Projektroot mit einer stabilen Projekt-ID.

Neue Einzelläufe und Benchmarkserien werden im Projekt unter `runs/<run-id>/` beziehungsweise `runs/<series-id>/` gespeichert. Die Laufdaten sollen Eingaben, Konfigurationen, Fortschritt, einzelne Versuche, Rohresultate und Auswertungen nachvollziehbar erhalten.

Datasetgenerierung und Suiteanlage speichern neue Eingaben unter `inputs/`. Ein Serienplan friert die gespeicherten Inputs ein. Wiederaufnahme erhält alte Versuche und startet einen neuen Versuch erst nach geklärtem Prozessende. Audit und Export unterscheiden vollständige, ungelöste, fehlerhafte und unterbrochene Ergebnisse.

Ausgewählte abgeschlossene Studien werden ausdrücklich unter `studies/<study-id>/` veröffentlicht. Dort liegen die gemeinsame Studienbeschreibung, gespeicherte Eingaben und kompakte Ergebnisse; vollständige Rohdaten werden als zugeordnete GitHub-Release-Downloads bereitgestellt. Arbeitsdaten unter `runs/` und `inputs/` werden dadurch weder verändert noch automatisch vollständig versioniert.
