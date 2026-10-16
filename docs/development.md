# Entwicklung

Das Paket verwendet ein src-Layout. Der fachliche Kern arbeitet mit unveränderlichen mathematischen Objekten. Dateidokumente, Prozesssteuerung und Auswertung liegen in getrennten Modulen.

## Lokale Umgebung

Die Entwicklung verwendet Python 3.13 oder 3.14. Eine kontrollierte Umgebung wird mit den projektintern gespeicherten, tatsächlich geprüften Abhängigkeitsständen eingerichtet. Ein Environmentlock beschreibt die Umgebung; das Paketdateiinventar beschreibt unabhängig davon den ausgelieferten Code.

```sh
uv venv --python 3.13
uv pip install --python .venv/bin/python -e . pytest==9.1.1 build==1.6.1 ruff==0.17.0
.venv/bin/python -m pytest
.venv/bin/python -m ruff check src tests tools build_support.py
.venv/bin/python -m build
```

Das gebaute Wheel wird zusätzlich in einer frischen Umgebung außerhalb des Quellcheckouts installiert und geprüft. Builds enthalten Paketcode und erforderliche Produktdateien. Tatsächliche Laufdaten, operative Profile und Umgebungen werden nicht verpackt.

## Änderungen und Abnahme

Jede fachliche Änderung braucht spezifische Tests für ihre sichtbare Berechnung oder Fehlergrenze. Tests und Dokumentation entstehen mit dem jeweiligen Modul. Analytische Tests und Formatprüfungen ersetzen keine kontrollierten vollständigen Laufzeitmessungen.

Konfigurationen ändern keine Parameter verdeckt: Strategie, Tiefe, Grid, Queryquelle, Stopregel und Planungsbewertung bleiben in den gespeicherten Eingaben sichtbar. Nicht bestandene beziehungsweise noch nicht durchgeführte Prüfungen bleiben als solche dokumentiert.

## Reproduzierbarer nativer Probelauf

Für dauerhafte Läufe kann eine eigene `.venv-runtime` das gebaute Wheel enthalten.
`requirements/runtime-macos-py313.txt` bindet die auf dem Mac tatsächlich geprüften
Produktionsabhängigkeiten. `requirements/runtime-linux-py314.txt` enthält die
getrennt geprüfte Linux-Umgebung. Eine andere Umgebung benötigt eigene Qualifizierung.

```sh
uv venv --python 3.13 .venv-runtime
uv pip install --python .venv-runtime/bin/python \
  -r requirements/runtime-macos-py313.txt dist/*.whl
.venv-runtime/bin/python tools/qualification/qualify.py --project-root "$PWD" \
  --output "$PWD/runs/my-native-qualification" --scope standalone
.venv-runtime/bin/python tools/validation/smoke_workflow.py --project-root "$PWD" \
  --execution-profile "$PWD/runs/my-native-qualification/profile.json"
```

Für Linux-Serien sind Python 3.14, die Linux-Abhängigkeiten und das Scope
`series_linux_recovery` erforderlich. `standalone` allein reicht dort für
`benchmark plan`, `run` und `resume` nicht aus. Als Alternative zum Mac-Block auf
einem frischen Linux-Ausführungshost:

```sh
uv venv --python 3.14 .venv-runtime
uv pip install --python .venv-runtime/bin/python \
  -r requirements/runtime-linux-py314.txt dist/*.whl
.venv-runtime/bin/python tools/qualification/qualify.py --project-root "$PWD" \
  --output "$PWD/runs/my-native-qualification" --scope series_linux_recovery
.venv-runtime/bin/python tools/validation/smoke_workflow.py --project-root "$PWD" \
  --execution-profile "$PWD/runs/my-native-qualification/profile.json"
```

Mac- und Linux-Befehle sind Alternativen für ihren jeweiligen Host. Verwende für
jede neue Qualifizierung einen neuen Ausgabepfad. Linux-Einzelläufe mit `solve`
können auch mit einem `standalone`-Profil ausgeführt werden.

Der neue Smoke-Test verwendet die öffentlichen CLI-Befehle für Generierung, Suite, Planung, Ausführung,
Status, Audit, Export, Resume und Seal. Er speichert neue Eingaben unter `inputs/`
und Quittungen/Rohresultate unter `runs/`. Bestehende Verzeichnisse werden nicht
überschrieben. Vier der acht Jobs aktivieren Parent-cProfile; der Test ist deshalb
ausdrücklich ein Funktionsnachweis und kein Laufzeitvergleich.

Die tatsächliche interaktive Terminalroute kann zusätzlich auf macOS oder Linux
mit demselben qualifizierten Wheelinterpreter geprüft werden:

```sh
.venv-runtime/bin/python tools/validation/interactive_tty.py \
  --project-root "$PWD" \
  --execution-profile "$PWD/runs/my-native-qualification/profile.json" \
  --output-id interactive-tty-01
```

Dieser Test verwendet eine echte neue Terminalsession mit kontrollierter
Foregroundgruppe und führt drei kleine native Läufe aus: ungültige Eingabe mit
derselben Frage und anschließender gültiger Antwort, Terminal-EOF und Strg-C.
Er verwendet ausdrücklich feste Tiefe eins, eine erlaubte Antwort, einen Worker
und einen 15-Sekunden-Casewatchdog. Das ist eine Funktionsprüfung dieser
Bediengrenze. Sämtliche neuen Eingaben, nativen Laufartefakte, Rohtranskripte und
die Quittung bleiben unter dem markierten Projekt in `inputs/` und `runs/`.
Ein neuer Durchlauf benötigt eine neue `--output-id`; keine frühere Prüfung wird
überschrieben. Die drei zusätzlichen Terminalproben verändern die Zählung der
separaten 34-/39-Betriebsqualifizierung nicht.

Bei einem Fehler der Terminalbeobachtung stoppt das Werkzeug nach dem aktuellen
Fall. Es schließt den PTY-Master und versucht begrenzt, das exakt eigene, noch
nicht gereapte Foregroundkind über die tatsächliche Terminal-Interrupttaste
beenden zu lassen. Es sendet keine Signale an bloß aufgezeichnete PIDs oder
unbewiesene Casegruppen. Unklare Start- oder Cleanupzustände bleiben als
`blocked_unknown` in `failure-cleanup.json` sichtbar; ein weiterer Solver wird
nach einer fehlgeschlagenen Beobachtung nie gestartet.

## Execution-contract changes

Version `0.2.0` integrates Countdown, full-depth fallback and the default
`min_expected_progress=0.001` contract. The schema registry is indexed by document
kind and version. Regenerate packaged schema resources with the dependency-free
registry writer after changing schema definitions; installed qualification checks
the actual registry/resource IDs rather than a historical fixed count.

Run targeted mathematical, phase, continuation and durability tests first, then
the entire suite and lint. Qualify the final built payload on each host and build
version before runtime comparisons. Any later package or schema change invalidates
source-bound qualification and requires a new wheel and fresh qualification output.
Historical v1 archives retain their original bytes, digests and disabled progress
threshold; conversion creates a separate current input rather than rewriting data.

## Abnahmestand der Integration vom 16. Oktober 2026

Die Integration ist auf `main` übernommen. Quellenbindung, vollständige
Testzahlen und abgeschlossene Freigabegates stehen zentral im
[Implementierungsstatus](implementation-status.md). Die
[anschließende Hauptstudie](../studies/strategy-grid100-progress001-20261016T030055Z/README.md) veröffentlicht ihre
eigenständigen Mess- und Prüfnachweise. Fehlgeschlagene Entwicklungsabnahmen
und verworfene Kandidaten bleiben getrennt im lokalen Abnahmenachweis
erhalten. Jede Änderung des Paketpayloads benötigt neue quellgebundene
Kontrollen und Laufzeitgates.

Abgeschlossene Studien erhalten eine ausdrücklich geprüfte Veröffentlichung
unter `studies/` und einen passenden Release mit Rohdaten. Das
[Veröffentlichungsverfahren](publication.md) beschreibt die Ablage und
Paketprüfung; neue Arbeitsdaten werden weiter ausschließlich projektintern
unter `inputs/` und `runs/` erzeugt.
