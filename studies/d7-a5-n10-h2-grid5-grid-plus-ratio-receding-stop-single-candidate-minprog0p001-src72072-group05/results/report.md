# d7-a5-n10-h2-grid5-grid-plus-ratio-receding-stop-single-candidate-minprog0p001-src72072-group05

Vorläufige Auswertung; unabhängige Rohprüfung und finaler Hashvergleich stehen separat aus.

10 unabhängige Probleme, eine Konfiguration, eine Ausführung je Zelle; 10 tatsächliche Versuche.
receding, H2, Grid 5, Queryquelle both, Stopp single_candidate, Mindestfortschritt 0.001; 16 Worker, ein nativer Thread.

Korrekt: 10/10; regulär ungelöst: 0/10; fehlgeschlagen: 0/10; falsche Auswahl: 0/10; Auswahlqualität unbestätigt: 0/10.

| Kennzahl | Fälle/Versuche mit Wert | Mittel | Summe |
| --- | ---: | ---: | ---: |
| Queries, alle regulär abgeschlossenen Fälle | 10 | 24.8 | 248 |
| Queries, korrekte Lösungen | 10 | 24.8 | 248 |
| Queries, sämtliche Versuche mit gespeichertem Zähler | 10 | 24.8 | 248 |
| API-Sekunden, Primärfälle mit vollständigem Messwert | 10 | 82.02 | 820.2 |
| API-Sekunden, korrekte Lösungen | 10 | 82.02 | 820.2 |
| Controller-Sekunden, sämtliche Versuche | 10 | 82.8308 | 828.308 |
| Partielle API-Sekunden, sämtliche Teilversuche | 0 | – | – |

Eine API-Zeit je Fall ist die Laufzeitkennzahl. Controller- und Fallprozesskosten haben andere Messgrenzen und werden separat ausgewiesen. Fehlende Werte werden nicht als Null interpretiert.

Alle Fälle einschließlich Ausreißern bleiben enthalten. Der IQR-Hinweis ist rein beschreibend: d7-m5-c000045

| Problem | Anfangskandidaten | Queries | API s | Status/Qualität | Endgrund |
| --- | ---: | ---: | ---: | --- | --- |
| d7-m5-c000040 | 5 | 6 | 4.86209 | completed/correct | exact_single_candidate |
| d7-m5-c000041 | 4 | 14 | 18.59 | completed/correct | exact_single_candidate |
| d7-m5-c000042 | 5 | 15 | 15.977 | completed/correct | exact_single_candidate |
| d7-m5-c000043 | 5 | 34 | 216.436 | completed/correct | exact_single_candidate |
| d7-m5-c000044 | 4 | 9 | 9.69071 | completed/correct | exact_single_candidate |
| d7-m5-c000045 | 5 | 67 | 302.895 | completed/correct | exact_single_candidate |
| d7-m5-c000046 | 3 | 42 | 112.768 | completed/correct | exact_single_candidate |
| d7-m5-c000047 | 5 | 20 | 29.1819 | completed/correct | exact_single_candidate |
| d7-m5-c000048 | 4 | 35 | 102.443 | completed/correct | exact_single_candidate |
| d7-m5-c000049 | 5 | 6 | 7.35555 | completed/correct | exact_single_candidate |

Gemessene Quelle: `720726607ae451b319e59e01453b6ba69b9950ef42420e700ed6b4eaa5b34d0e`, Buildcommit `62d1d01339f91802e2916b63660a4e640d99c9cc`; numerisches Profil `otqa-exact-v3`.
Eingabekohorte: `9e14aa399cc060c5e33d9a8199354ffbb2b129fb55fde61ed650d6d09b6894ad`.

Die Quellen-, Eingabe-, Audit- und Resultatreferenzen stehen in results.json. Das Rohdatenpaket und die unabhängige Prüfung werden separat gebunden. Keine historischen Laufzeiten oder anderen Studienarchive werden für diese Auswertung benötigt.

Es gibt weder Wiederholungsmediane noch gepaarte Strategievergleiche innerhalb dieser Einzelstudie. Gespeicherte Kandidatenvolumen werden nicht geometrisch neu zertifiziert.
