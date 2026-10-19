# d7-a5-n1-h3-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072-case000024

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

1 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 1 tatsächliche Versuche.
receding, H3, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 1/1; regulär ungelöst: 0/1; fehlgeschlagen: 0/1; falsche Auswahl: 0/1; Auswahlqualität unbestätigt: 0/1.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 1 | 45 | 45 |
| Queries, korrekte Lösungen | 1 | 45 | 45 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 1 | 45 | 45 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 1 | 35235.1 | 35235.1 |
| API-Sekunden, korrekte Lösungen | 1 | 35235.1 | 35235.1 |
| Controller-Sekunden, sämtliche Versuche | 1 | 35236.2 | 35236.2 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: keine

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000024 | 4 | 45 | 35235.1 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `33018111a825d77fed4345bbeeaa1654091a84a2442a6555cc93c169e7a7156f`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Die native Tabelle umfasst ausschließlich den neuen Versuch auf 179. Die zusätzlich gebundene historische Beobachtung der früheren 170-Versuche bleibt separat und wird nicht als zusätzliche Qualitätsinstanz gezählt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.

Technische Verlagerung desselben logischen Falls: Die früheren Versuche auf 170 bleiben erhalten. Ihre vollständigen API- und Controllerkosten sind unbekannt; aus den gespeicherten Teilwerten entsteht keine Gesamtlaufzeit.

| Alter Versuch | Gesicherte Antworten im Snapshot | Partielle API s | Vollständige API s | Controller s |
| --- | ---: | ---: | --- | --- |
| attempt0001 | 2 | 255.080691 | unbekannt | unbekannt |
| attempt0002 | 0 | unbekannt | unbekannt | unbekannt |

Diese alten Antwortpräfixe wurden dem neuen Versuch nicht vorgegeben. Spätere Aktivitäten nach dem letzten gesicherten 170-Snapshot sind nicht bestätigt. Der Verlagerungslauf ersetzt denselben Fall in der Auswertung und erweitert den Umfang nicht auf acht Probleme.
