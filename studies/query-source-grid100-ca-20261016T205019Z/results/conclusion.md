# Grid gegenüber Grid + Ratio

100 identische ungefilterte Probleme, acht neue Grid-Konfigurationen in einer einzigen Phase. Vergleich mit den fest zugeordneten acht bisherigen Grid-plus-Ratio-Konfigurationen; keine Wiederholung der bisherigen Both-Läufe und keine Wiederverwendung alter Grid-Zellen.

Der Umfang Countdown/adaptiv wurde nach Sichtung der ersten drei Fälle der angehaltenen Grid-Vorserie festgelegt. Die Vorserie einschließlich ihrer dreißig abgeschlossenen Countdown-/Adaptiv-Zellen bleibt ein getrennter historischer Anhang. Der vollständige Both-Rohbestand enthält weiterhin 1.200 Zellen; genau 800 passende Zellen bilden diesen Vergleich.

| Queryquelle | Strategie | Grid | korrekt /100 | Ø Queries korrekt | Median Queries korrekt | Ø SDK-Zeit korrekt (s) | übrige Endgründe |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| grid | countdown | 3 | 100 | 10.020 | 8.000 | 2.217 | {} |
| grid | countdown | 5 | 100 | 8.940 | 6.000 | 3.124 | {} |
| grid | countdown | 10 | 100 | 8.900 | 6.000 | 5.648 | {} |
| grid | countdown | 20 | 100 | 8.750 | 6.000 | 10.671 | {} |
| grid | adaptive | 3 | 100 | 8.930 | 7.000 | 3.464 | {} |
| grid | adaptive | 5 | 100 | 8.810 | 6.000 | 5.499 | {} |
| grid | adaptive | 10 | 100 | 8.490 | 6.000 | 10.213 | {} |
| grid | adaptive | 20 | 100 | 8.130 | 6.000 | 19.216 | {} |
| both | countdown | 3 | 100 | 9.390 | 6.000 | 2.479 | {} |
| both | countdown | 5 | 100 | 8.880 | 6.000 | 3.470 | {} |
| both | countdown | 10 | 100 | 8.920 | 6.000 | 6.309 | {} |
| both | countdown | 20 | 100 | 8.640 | 6.000 | 11.564 | {} |
| both | adaptive | 3 | 100 | 8.810 | 7.000 | 4.320 | {} |
| both | adaptive | 5 | 100 | 8.490 | 6.000 | 6.319 | {} |
| both | adaptive | 10 | 100 | 8.600 | 6.000 | 11.491 | {} |
| both | adaptive | 20 | 100 | 8.210 | 6.000 | 21.125 | {} |

## Gepaarte Queryunterschiede

Differenz = Grid minus bisheriges Grid + Ratio, ausschließlich auf gemeinsam korrekt gelösten Fällen. Qualität wird für alle 100 Fälle je Bedingung ausgewiesen.

| Strategie | Grid | gemeinsam korrekt /100 | weniger | gleich | mehr | Ø Differenz Queries |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| countdown | 3 | 100 | 16 | 49 | 35 | 0.630 |
| countdown | 5 | 100 | 17 | 51 | 32 | 0.060 |
| countdown | 10 | 100 | 16 | 61 | 23 | -0.020 |
| countdown | 20 | 100 | 8 | 77 | 15 | 0.110 |
| adaptive | 3 | 100 | 4 | 82 | 14 | 0.120 |
| adaptive | 5 | 100 | 6 | 81 | 13 | 0.320 |
| adaptive | 10 | 100 | 9 | 84 | 7 | -0.110 |
| adaptive | 20 | 100 | 9 | 85 | 6 | -0.080 |

Die Zähler und Nenner, alle ungelösten und fehlerhaften Abschlüsse, Ausreißer, vollständigen Pfade und sämtliche Versuchskosten stehen in `results.json`. SDK-, Fallprozess- und Controllerzeiten überlappen und werden nicht addiert.

Die Zeitmessungen stammen aus getrennten, nicht randomisierten Sitzungen. Auf zusätzliche zeitnahe Kontrollläufe wurde auf Nutzerwunsch verzichtet. Die Betriebswerkzeuge wurden gegenüber der vorherigen Studie geändert; Unterschiede sind beobachtete Laufzeiten und kein isolierter kausaler Nachweis für die Queryquelle.

Keine geometrische Neuzertifizierung. Keine universelle Überlegenheit einer Quelle wird vorausgesetzt. Die Beurteilung berücksichtigt Lösungsquote, gepaarte Queryzahlen und Rechenzeit gemeinsam.
