# Änderungsverzeichnis

## 0.2.0

- Regulärer Fixed-Countdown mit explizitem Antwortcursor und einmaliger voller Ersatzplanung nach fehlender Query oder unzureichendem Restplan.
- `min_expected_progress` als Schlüsselwortparameter, Default `0.001`, strikter vollständiger Horizontgewinn; `None` deaktiviert. Neuer ungelöster Endgrund `insufficient_expected_progress`.
- Adaptive zulässige Planwahl bis Tiefe drei und zertifizierte Frontierdominanz bei unveränderter finaler Scorearithmetik.
- Gebundene SDK- und native Fortsetzung; Anfangshistorien sind Warmstarts mit voller Tiefe.
- Eigene Prozessworker laden benötigte Module beim Start; numerische Sessions und Handles bleiben bis zur ersten tatsächlichen Aufgabe unangelegt. Importfehler bleiben dem betroffenen tatsächlichen Auftrag zugeordnet.
- Versionierte Laufdokumente, sequentieller Phasenaudit, ausdrückliche Konfigurationskonvertierung und mehrversionige Exporte/Archive. Historische Bytes und Digests bleiben unverändert.
- Eindeutige Ereignisschemaauswahl und gemeinsamer privater Journal-Fold vermeiden wiederholte Formatprüfungen; Schemaressourcen, Originalnachweise und fachliche Prüfungen bleiben erhalten.
- Aktualisierte Schnittstellen, Beispiele und Produktdokumentation. Tatsächliche sourcegebundene Prüfungen stehen im Implementierungsstatus.

## 0.1.0

- Eigenständiges Pythonpaket mit modularer Geometrie, fester und adaptiver Planung bis Tiefe drei und gemeinsamer SDK-/CLI-Solverschleife.
- Dauerhafte Einzelläufe und Benchmarkserien mit gespeicherten Eingaben, Wiederaufnahme, Audit, JSON-/CSV-Auswertung und überprüfbaren Archiven.
- Native Betriebsqualifizierung, Tests und Dokumentation für macOS und Linux.
- Quellarchive übernehmen den tatsächlichen Gitstatus vor der eigenen temporären Verpackung. Vorhandene Nutzeränderungen bleiben als Änderungen erkennbar; Änderungen des Paketcodes während des Builds werden abgewiesen.
