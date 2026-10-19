# D5 / A5 / H2 — stop_aware-volume-confidence-095 / b05

20 ursprüngliche gepaarte Fälle, 20 einzige Primärversuche: 19 korrekt, 1 falsche Konfidenzentscheidungen, 0 Solverfehler; 83 Antworten. Alle20 bleiben im Nenner.

Volumen-Konfidenzschwelle 0.95, planning_evaluation stop_aware; Grid5/both, adaptive bisTiefe2, receding, minimum expected progress0.001. Modell-Konfidenz ist keine Garantie eines korrekten Gewinners. Auch ein als solved gespeicherter Konfidenzabbruch kann falsch sein. Keine Umwertung als NumericalError, kein Retry.

Diese20 Fälle sind genau eine von fünf disjunkten Partitionen derselben unveränderten100 Matrizen/Gewichte. Alle vier Bedingungen verwenden dieselben ursprünglichen Fall-IDs; der historische Baseline100-Lauf wurde nicht wiederholt. Die20 Batches bilden400 neue Messungen; das Vergleichsdokument ergänzt100 historische Referenzen, keine500 neuen Messungen.

| Fall | Qualität | Antworten | K | Modell-Konfidenz | API s | Fall s | Controller s |
|---|---|---:|---:|---:|---:|---:|---:|
| d5-m5-c000080 | correct | 2 | 4 | 0.9646524233432667 | 3.8973013689974323 | 4.205882551003015 | 4.387482935999287 |
| d5-m5-c000081 | correct | 2 | 2 | 0.9558365011975773 | 2.5491952589945868 | 2.8599108860071283 | 3.0314289320085663 |
| d5-m5-c000082 | correct | 4 | 2 | 0.9750529965561877 | 5.318741411989322 | 5.644096239004284 | 5.843432786990888 |
| d5-m5-c000083 | correct | 5 | 1 | 1.0 | 7.340333472006023 | 7.678154419991188 | 7.88560984202195 |
| d5-m5-c000084 | correct | 12 | 2 | 0.9887457885307241 | 22.03290331401513 | 22.421589392994065 | 22.720526002987754 |
| d5-m5-c000085 | correct | 2 | 3 | 0.9627049247032698 | 3.442281677009305 | 3.754399015015224 | 3.970034099998884 |
| d5-m5-c000086 | correct | 2 | 2 | 0.9533982323773593 | 1.959460278012557 | 2.270425457012607 | 2.44281636501546 |
| d5-m5-c000087 | correct | 1 | 3 | 0.9740272793735603 | 1.5360007160052191 | 1.836940584005788 | 2.0034988379920833 |
| d5-m5-c000088 | correct | 5 | 2 | 0.9941797035972908 | 4.041117292013951 | 4.379265487019438 | 4.631613193982048 |
| d5-m5-c000089 | correct | 2 | 2 | 0.9551257190151762 | 4.092135351995239 | 4.405673038010718 | 4.629984279017663 |
| d5-m5-c000090 | correct | 7 | 2 | 0.9777271373302671 | 6.9538081499922555 | 7.305078642006265 | 7.540872952988138 |
| d5-m5-c000091 | incorrect | 6 | 2 | 0.9529656722653669 | 6.272188756993273 | 6.624409522977658 | 6.8543298880103976 |
| d5-m5-c000092 | correct | 2 | 4 | 0.9551910832812601 | 8.417811316001462 | 8.733040660998086 | 8.921126745000947 |
| d5-m5-c000093 | correct | 1 | 2 | 0.9792216266711518 | 1.3704361150157638 | 1.6775514009932522 | 1.859096778993262 |
| d5-m5-c000094 | correct | 8 | 2 | 0.9772744141123022 | 7.772895831003552 | 8.145574045018293 | 8.414494750002632 |
| d5-m5-c000095 | correct | 4 | 4 | 0.9820206412882576 | 16.567348948010476 | 16.939570950024063 | 17.18205919099273 |
| d5-m5-c000096 | correct | 3 | 1 | 1.0 | 2.089902589999838 | 2.4160308949940372 | 2.610881603002781 |
| d5-m5-c000097 | correct | 3 | 2 | 0.9827000889447868 | 4.763330802001292 | 5.092360996990465 | 5.279414069984341 |
| d5-m5-c000098 | correct | 9 | 2 | 0.9571131328550083 | 9.116176576004364 | 9.49964894002187 | 9.763539239007514 |
| d5-m5-c000099 | correct | 3 | 3 | 0.9603182982856103 | 5.192869591002818 | 5.523057301004883 | 5.726917581981979 |

API-, Fall- und Controllerzeiten sind getrennte gespeicherte Messgrößen; unbekannte Werte bleiben unbekannt. Sie werden weder addiert noch als CPU-Zeit, Kalenderdauer oder ETA bezeichnet.

Originalresultate, Journale, Eingaben und Source/Wheel bleiben unverändert. Die öffentliche Plan-/State-/Manifest-/SCI-Ansicht enthält nur ausdrücklich ausgewählte wissenschaftliche Felder mit Originalhashes; private Betriebs-, Prozess-, Claim-, Auth-, Guard-, Release- und Spiegelakten bleiben private Prüfgates. Die gespeicherte Offlineprüfung kontrolliert Hashes, Bindungen und reproduziert Tabellen; sie berechnet keine Gewinner, Fraction-Antworten, Geometrie oder neue wissenschaftliche Abnahme. Messsource62d1…/720726…/Wheel24e4…; Publikationscommit separat.
