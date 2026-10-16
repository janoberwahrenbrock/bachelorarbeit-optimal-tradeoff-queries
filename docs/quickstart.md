# Erster gespeicherter Benchmark

Dieser Ablauf erzeugt zwei neue Probleme mit je drei Zielen und drei Alternativen.
Feste und adaptive Tiefe zwei werden auf denselben Problemen ausgeführt. Die
Konfigurationen verwenden Grid5 plus Ratios, Singletonabbruch, acht Worker und
einen nativen Thread. Es entstehen vier getrennte Jobs. Eine anfangs bereits
eindeutige Alternative kann ohne Query zum Ergebnis führen.

Alle Befehle laufen im frischen Repositoryroot mit `otqa-project.json`.
Verwende Python 3.13 auf macOS beziehungsweise Python 3.14 auf Linux. Für bereits
vorhandene Ausgaben wähle neue Kennungen und Pfade; die Laufzeit überschreibt
keine alten Datensätze, Serien oder Qualifizierungen.

## Wheel bauen und auf dem Host qualifizieren

```sh
python3 -m venv .venv-build
.venv-build/bin/python -m pip install build==1.6.1
.venv-build/bin/python -m build
python3 -m venv .venv-runtime
```

Die folgenden beiden Installationsblöcke sind Alternativen. Verwende genau den
Block für deinen Host und eine neue Laufzeitumgebung. Der Wheelpfad bezeichnet
die aktuelle Projektversion 0.2.0; bei einer anderen Version wähle ausdrücklich
das tatsächlich gebaute Wheel.

**macOS mit Python 3.13:**

```sh
.venv-runtime/bin/python -m pip install \
  -r requirements/runtime-macos-py313.txt \
  dist/bachelorarbeit_optimal_tradeoff_queries-0.2.0-py3-none-any.whl
.venv-runtime/bin/python tools/qualification/qualify.py --project-root "$PWD" \
  --output "$PWD/runs/quickstart-qualification" --scope standalone
```

**Linux mit Python 3.14:**

```sh
.venv-runtime/bin/python -m pip install \
  -r requirements/runtime-linux-py314.txt \
  dist/bachelorarbeit_optimal_tradeoff_queries-0.2.0-py3-none-any.whl
.venv-runtime/bin/python tools/qualification/qualify.py --project-root "$PWD" \
  --output "$PWD/runs/quickstart-qualification" --scope series_linux_recovery
```

Die Qualifizierung muss vollständig erfolgreich sein und die neue
`profile.json` erzeugen. Ein fehlgeschlagener Versuch bleibt erhalten; für einen
neuen Versuch wird ein neuer Ausgabepfad verwendet. Eine Entwicklungsinstallation
mit `pip install -e .` genügt nicht für diese Betriebsqualifizierung.

## Eingaben und Suite speichern

```sh
.venv-runtime/bin/otqa dataset generate --dataset-id quickstart --master-seed 5721 \
  --objectives 3 --alternatives 3 --cases-per-shape 2 \
  --output inputs/datasets/quickstart
```

Speichere die folgende neue Datei als `inputs/quickstart-selection.json`:

```json
[
  {
    "configuration_id": "fixed2-singleton",
    "case_ids": ["d3-m3-c000000", "d3-m3-c000001"]
  },
  {
    "configuration_id": "adaptive2-singleton",
    "case_ids": ["d3-m3-c000000", "d3-m3-c000001"]
  }
]
```

Die vollständigen mitgelieferten Konfigurationen bleiben dabei unverändert:

```sh
.venv-runtime/bin/otqa suite create --source-root . --suite-id quickstart \
  --dataset inputs/datasets/quickstart/dataset.json \
  --config examples/configurations/fixed2-singleton.json examples/configurations/adaptive2-singleton.json \
  --selection-file inputs/quickstart-selection.json --repetitions 1 \
  --output inputs/suites/quickstart/suite.json
.venv-runtime/bin/otqa benchmark plan --source-root . \
  --suite inputs/suites/quickstart/suite.json \
  --execution-profile runs/quickstart-qualification/profile.json \
  --output runs/quickstart
```

Generierung, Suiteanlage und Planung lösen noch kein Problem. Der Plan friert
Eingaben, Konfigurationen, Quelle, Profil und die vier Jobs auf diesem Host ein.

## Ausführen und Ergebnisse prüfen

```sh
.venv-runtime/bin/otqa benchmark run --plan runs/quickstart/plan.json
.venv-runtime/bin/otqa benchmark status --series runs/quickstart
.venv-runtime/bin/otqa benchmark audit --series runs/quickstart
.venv-runtime/bin/otqa benchmark export --series runs/quickstart \
  --format json --output runs/quickstart/exports/jobs.json
```

Die Serie löst jeweils nur einen Fall; dessen acht Worker bewerten unabhängige
Rootqueries. Für einen vollständigen Vergleich sollten keine anderen Solver
auf demselben Host gleichzeitig laufen. Die Ergebnisse, Journale, Zeiten und
Queryzahlen liegen unter `runs/quickstart/jobs/`. `status` und die Exportzeilen
zeigen auch ungelöste, fehlerhafte und unterbrochene Fälle. Ein reguläres
`no_query` ist keine gelöste Auswahl. Exitcodes erklärt [die CLI](cli.md#exit-status-and-timing).

Nach einem unterbrochenen Lauf kann derselbe Plan fortgesetzt werden:

```sh
.venv-runtime/bin/otqa benchmark resume --series runs/quickstart
```

Abgeschlossene und terminal fehlgeschlagene Jobs werden dabei übersprungen.
Unterbrochene Jobs erhalten einen neuen Versuch erst nach geklärtem Ende der
alten Prozessgruppe. Unklare Starts blockieren; alte Versuche bleiben sichtbar.

Wenn Serie und Prozessgruppen beendet sind, kann ein portables Archiv erzeugt
werden:

```sh
.venv-runtime/bin/otqa benchmark seal --series runs/quickstart
```

Der Befehl gibt die neue Archivkennung und ihren Inventarbeleg zurück. Hinweise
zur Offlineprüfung stehen unter [Archive](seal.md). Weitere Varianten und die
getrennten Aussagegrenzen von Funktion, Qualität und Laufzeit beschreiben
[Konfiguration](configuration.md), [Benchmarks](benchmarks.md),
[Numerik](numerical_behavior.md) und [Laufzeitprüfung](performance.md).
