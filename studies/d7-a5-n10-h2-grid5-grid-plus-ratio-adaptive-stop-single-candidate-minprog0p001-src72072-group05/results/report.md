# d7-a5-n10-h2-grid5-grid-plus-ratio-adaptive-stop-single-candidate-minprog0p001-src72072-group05

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
adaptive, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 18 | 180 |
| Queries, korrekte Lösungen | 10 | 18 | 180 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 18 | 180 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 46.1652 | 461.652 |
| API-Sekunden, korrekte Lösungen | 10 | 46.1652 | 461.652 |
| Controller-Sekunden, sämtliche Versuche | 10 | 47.0078 | 470.078 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d7-m5-c000043, d7-m5-c000045

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000040 | 5 | 6 | 5.00563 | completed/correct | exact_single_candidate |
| d7-m5-c000041 | 4 | 9 | 7.01524 | completed/correct | exact_single_candidate |
| d7-m5-c000042 | 5 | 5 | 3.99137 | completed/correct | exact_single_candidate |
| d7-m5-c000043 | 5 | 28 | 139.88 | completed/correct | exact_single_candidate |
| d7-m5-c000044 | 4 | 4 | 2.89539 | completed/correct | exact_single_candidate |
| d7-m5-c000045 | 5 | 68 | 193.046 | completed/correct | exact_single_candidate |
| d7-m5-c000046 | 3 | 26 | 62.5794 | completed/correct | exact_single_candidate |
| d7-m5-c000047 | 5 | 20 | 34.4943 | completed/correct | exact_single_candidate |
| d7-m5-c000048 | 4 | 10 | 9.16211 | completed/correct | exact_single_candidate |
| d7-m5-c000049 | 5 | 4 | 3.58235 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `9e14aa399cc060c5e33d9a8199354ffbb2b129fb55fde61ed650d6d09b6894ad`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
