# Geprüfter Vergleich: Strategien und Gridgrößen

100 neue ungefilterte Probleme, zwölf Konfigurationen und 1.200 Primärläufe; jeder Lauf genau einmal. Die ersten drei Probleme bleiben reguläre Primärfälle.

| Strategie | Grid | korrekt /100 | Ø Queries korrekt gelöst | Median Queries korrekt | Ø SDK-Zeit korrekt (s) | ungelöste Endgründe |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| receding | 3 | 100 | 10.460 | 7.000 | 4.967 | {} |
| receding | 5 | 100 | 11.490 | 9.000 | 8.124 | {} |
| receding | 10 | 100 | 11.560 | 9.000 | 15.242 | {} |
| receding | 20 | 100 | 14.520 | 11.000 | 34.375 | {} |
| countdown | 3 | 100 | 9.390 | 6.000 | 2.479 | {} |
| countdown | 5 | 100 | 8.880 | 6.000 | 3.470 | {} |
| countdown | 10 | 100 | 8.920 | 6.000 | 6.309 | {} |
| countdown | 20 | 100 | 8.640 | 6.000 | 11.564 | {} |
| adaptive | 3 | 100 | 8.810 | 7.000 | 4.320 | {} |
| adaptive | 5 | 100 | 8.490 | 6.000 | 6.319 | {} |
| adaptive | 10 | 100 | 8.600 | 6.000 | 11.491 | {} |
| adaptive | 20 | 100 | 8.210 | 6.000 | 21.125 | {} |

Die Mittelwerte korrekt gelöster Fälle verwenden je Variante die ausgewiesene Zahl korrekter Fälle. Eine Rangfolge dieser Mittelwerte allein ist bei unterschiedlichen Lösungsquoten nicht fair; die gepaarten Vergleiche in `results.json` weisen deshalb alle Nenner und die gemeinsame korrekt gelöste Teilgruppe aus.

Schnelle ungelöste Fortschrittsstopps sind keine erfolgreichen Lösungen. Keine vorab bevorzugte Gridgröße wird festgelegt. Die Entscheidung muss Lösungsquote, Queryzahl und Rechenzeit gemeinsam berücksichtigen.

Quellenbindung, native Audit-/Exportbelege und Rohdatenreferenzen stehen in `results.json`. Keine geometrische Neuzertifizierung hypothetischer Bewertungen.
