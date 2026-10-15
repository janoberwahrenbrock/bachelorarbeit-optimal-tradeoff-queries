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
