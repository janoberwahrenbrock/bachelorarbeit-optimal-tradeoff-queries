# d7-a5-n1-h3-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-case000056

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

1 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 1 tatsächliche Versuche.
adaptive, H3, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 1/1; regulär ungelöst: 0/1; fehlgeschlagen: 0/1; falsche Auswahl: 0/1; Auswahlqualität unbestätigt: 0/1.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 1 | 9 | 9 |
| Queries, korrekte Lösungen | 1 | 9 | 9 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 1 | 9 | 9 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 1 | 1209.48 | 1209.48 |
| API-Sekunden, korrekte Lösungen | 1 | 1209.48 | 1209.48 |
| Controller-Sekunden, sämtliche Versuche | 1 | 1210.18 | 1210.18 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: keine

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000056 | 4 | 9 | 1209.48 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `d4781bf647e223082193f2b40579910b3c4ca1fd6022b2b96d95d1260cf892e3`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
