# Entwicklung

Das Paket verwendet ein src-Layout. Der fachliche Kern arbeitet mit unveränderlichen mathematischen Objekten. Dateidokumente, Prozesssteuerung und Auswertung liegen in getrennten Modulen.

## Lokale Umgebung

Die Entwicklung verwendet Python 3.13 oder 3.14. Eine kontrollierte Umgebung wird mit den projektintern gespeicherten, tatsächlich geprüften Abhängigkeitsständen eingerichtet. Ein Environmentlock beschreibt die Umgebung; das Paketdateiinventar beschreibt unabhängig davon den ausgelieferten Code.

```sh
uv venv --python 3.13
uv pip install --python .venv/bin/python -e . pytest==9.1.1 build==1.6.1 ruff==0.17.0
.venv/bin/python -m pytest
.venv/bin/python -m ruff check src tests
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
