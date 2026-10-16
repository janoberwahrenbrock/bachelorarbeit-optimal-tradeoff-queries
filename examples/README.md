# Konfigurationsbeispiele

Die vollständigen v2-JSON-Dateien unter `configurations/` können für neue native
Läufe verwendet werden. Jede speichert Modus und Fortschrittsschwelle ausdrücklich.

| Datei | Strategie und Ziel |
| --- | --- |
| `fixed2-singleton.json` | Neuplanung mit Tiefe zwei, Einzelkandidat, Schwelle `0.001` |
| `fixed2-countdown-singleton.json` | Countdown mit voller Ersatzplanung, Einzelkandidat, Schwelle `0.001` |
| `fixed2-progress-disabled.json` | Neuplanung mit ausdrücklich deaktivierter Fortschrittsprüfung (`null`) |
| `adaptive2-singleton.json` | Adaptive Horizonte eins und zwei, Einzelkandidat, Schwelle `0.001` |
| `adaptive3-confidence99.json` | Adaptive Horizonte eins bis drei, abbruchbewusste Bewertung und 99-Prozent-Volumenstopp |

Alle Beispiele verwenden dieselben geometrischen Wahrscheinlichkeiten ohne
Sampling, Grid plus Ratios oberhalb der letzten Ebene und Ratios auf der letzten
Ebene. Die acht Worker und ein nativer Thread sind ausdrücklich konfiguriert.
Ein gültiges, zur tatsächlich installierten Quelle passendes Ausführungsprofil
bleibt Voraussetzung nativer Läufe. Details stehen in [Konfiguration](../docs/configuration.md)
und [Quickstart](../docs/quickstart.md).

Historische v1-Konfigurationen werden mit `otqa config convert` ausdrücklich in
neue Dateien überführt. Für alte Countdowndateien muss dabei die neue Block- und
Warmstartsemantik bestätigt werden. Historische Studien werden nicht verändert.
