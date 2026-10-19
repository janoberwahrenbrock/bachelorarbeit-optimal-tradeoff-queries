# D5 / A5 / H2 — stop_aware-volume-confidence-099 / b03

20 ursprüngliche gepaarte Fälle, 20 einzige Primärversuche: 20 korrekt, 0 falsche Konfidenzentscheidungen, 0 Solverfehler; 145 Antworten. Alle20 bleiben im Nenner.

Volumen-Konfidenzschwelle 0.99, planning_evaluation stop_aware; Grid5/both, adaptive bisTiefe2, receding, minimum expected progress0.001. Modell-Konfidenz ist keine Garantie eines korrekten Gewinners. Auch ein als solved gespeicherter Konfidenzabbruch kann falsch sein. Keine Umwertung als NumericalError, kein Retry.

Diese20 Fälle sind genau eine von fünf disjunkten Partitionen derselben unveränderten100 Matrizen/Gewichte. Alle vier Bedingungen verwenden dieselben ursprünglichen Fall-IDs; der historische Baseline100-Lauf wurde nicht wiederholt. Die20 Batches bilden400 neue Messungen; das Vergleichsdokument ergänzt100 historische Referenzen, keine500 neuen Messungen.

| Fall | Qualität | Antworten | K | Modell-Konfidenz | API s | Fall s | Controller s |
|---|---|---:|---:|---:|---:|---:|---:|
| d5-m5-c000040 | correct | 10 | 2 | 0.9931839972414714 | 10.01359533399227 | 10.400865778996376 | 10.68520418999833 |
| d5-m5-c000041 | correct | 2 | 4 | 0.991710765293203 | 3.9125179929833394 | 4.237317034974694 | 4.4246499379805755 |
| d5-m5-c000042 | correct | 4 | 1 | 1.0 | 5.376936535991263 | 5.721711263991892 | 5.930373101000441 |
| d5-m5-c000043 | correct | 4 | 1 | 1.0 | 4.928108383988729 | 5.272738848987501 | 5.4748564480105415 |
| d5-m5-c000044 | correct | 5 | 1 | 1.0 | 5.41061508198618 | 5.8011028630135115 | 6.014077209983952 |
| d5-m5-c000045 | correct | 1 | 3 | 0.9978569067869129 | 1.7647839929850306 | 2.074907362984959 | 2.250389680993976 |
| d5-m5-c000046 | correct | 33 | 2 | 0.9971939662587778 | 77.09111947499332 | 77.65815911398386 | 78.26895793600124 |
| d5-m5-c000047 | correct | 6 | 3 | 0.991151562345191 | 11.425123631983297 | 11.8266778330144 | 12.059902455017436 |
| d5-m5-c000048 | correct | 11 | 2 | 0.9908320320849713 | 18.922475613013376 | 19.3264845010126 | 19.615958734997548 |
| d5-m5-c000049 | correct | 8 | 2 | 0.9978615672958375 | 6.12221004901221 | 6.484985560993664 | 6.750151798012666 |
| d5-m5-c000050 | correct | 2 | 4 | 0.9930906225954214 | 5.892106009006966 | 6.2292198649956845 | 6.418872555019334 |
| d5-m5-c000051 | correct | 9 | 2 | 0.9936492120211725 | 20.05436676600948 | 20.461534861999098 | 20.752423505997285 |
| d5-m5-c000052 | correct | 9 | 1 | 1.0 | 13.311475790018449 | 13.694078148022527 | 13.95155275601428 |
| d5-m5-c000053 | correct | 5 | 2 | 0.9958985616837648 | 6.965322687989101 | 7.345997992000775 | 7.565015410014894 |
| d5-m5-c000054 | correct | 6 | 1 | 1.0 | 10.946639284025878 | 11.368394418997923 | 11.6102468619938 |
| d5-m5-c000055 | correct | 2 | 4 | 0.998724665914812 | 4.740342728997348 | 5.078275471023517 | 5.273339753999608 |
| d5-m5-c000056 | correct | 4 | 2 | 0.9902069495534319 | 2.596548955014441 | 2.940806945989607 | 3.1467724539979827 |
| d5-m5-c000057 | correct | 0 | 4 | 0.9941219116910505 | 0.025087704008910805 | 0.33404948498355225 | 0.47201326899812557 |
| d5-m5-c000058 | correct | 20 | 2 | 0.994539636328731 | 36.50371109700063 | 37.0003408259945 | 37.42630974799977 |
| d5-m5-c000059 | correct | 4 | 1 | 1.0 | 4.671781529992586 | 5.017693890986266 | 5.259465648996411 |

API-, Fall- und Controllerzeiten sind getrennte gespeicherte Messgrößen; unbekannte Werte bleiben unbekannt. Sie werden weder addiert noch als CPU-Zeit, Kalenderdauer oder ETA bezeichnet.

Originalresultate, Journale, Eingaben und Source/Wheel bleiben unverändert. Die öffentliche Plan-/State-/Manifest-/SCI-Ansicht enthält nur ausdrücklich ausgewählte wissenschaftliche Felder mit Originalhashes; private Betriebs-, Prozess-, Claim-, Auth-, Guard-, Release- und Spiegelakten bleiben private Prüfgates. Die gespeicherte Offlineprüfung kontrolliert Hashes, Bindungen und reproduziert Tabellen; sie berechnet keine Gewinner, Fraction-Antworten, Geometrie oder neue wissenschaftliche Abnahme. Messsource62d1…/720726…/Wheel24e4…; Publikationscommit separat.
