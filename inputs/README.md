# Gespeicherte Eingaben

Neue Datensätze liegen unter `datasets/<id>/`, Suites unter `suites/<id>/`.
Eigene vollständige Konfigurationen und Auswahldateien können ebenfalls hier
gespeichert werden. Kleine Ausgangsbeispiele stehen unter `examples/`.

Erzeuge Daten einmal und verwende ihre gespeicherten Werte für alle verglichenen
Konfigurationen. Ein Serienplan materialisiert und bindet die tatsächlich
verwendeten Eingaben; bestehende Generierungsausgaben werden nicht überschrieben.

Das [Benchmarkverfahren](../docs/benchmarks.md) und der
[Quickstart](../docs/quickstart.md) zeigen die Befehle. Tatsächliche Eingaben
werden nicht automatisch auf GitHub veröffentlicht oder in Wheel/Sdist verpackt.
