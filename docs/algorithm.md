# Algorithmus

Der Solver wählt anhand von Tradeoffantworten eine Alternative aus einer geordneten Alternativenmatrix. Zeilen sind Alternativen, Spalten Ziele; alle Einträge liegen in `[0,1]`. Für eine Zeile `a` und einen Gewichtsvektor `w` gilt die lineare Nutzenfunktion `U_a(w) = sum_j alternatives[a,j] * w[j]`. Der Planer erhält keine Simulationsgewichte und keine Gewinnerkennzeichnung.

## Gewichtsraum und tatsächliche Antworten

Der anfängliche Gewichtsraum ist der Simplex `w[j] >= 0`, `sum_j w[j] = 1`. Eine Query `(a,b,t)` fragt nach `w[a] ? t * w[b]`. Ihre Antwort ist genau eines der Literale `<`, `=`, `>`.

Die akzeptierte Historie schränkt den Simplex in ursprünglicher Reihenfolge ein. Gleichheit fügt eine explizite Gleichung hinzu. Für die geometrische Darstellung strikter Antworten werden die festgelegten geschlossenen Halbseiten verwendet. Der Antwortgeber selbst klassifiziert strikt anhand der unveränderten Multiplikation; er verwendet keine zusätzliche Antworttoleranz.

Die Optimalitätsregion einer Alternative ist der Teil des aktuellen Gewichtsraums, in dem ihr Nutzen mindestens so groß wie der jeder anderen Zeile ist. Alternativen werden bei der Kandidatenanalyse nicht umnummeriert.

## Kandidatendefinition

Die feste Definition heißt `ratio_relevant`. Aus den Kandidatenregionen werden die Intervalle der geordneten Zielverhältnisse bestimmt. Sobald Kandidaten mit positiver Intervallbreite in mindestens einem geordneten Zielpaar vorliegen, bilden genau diese die Kandidatenmenge; ein unbeschränktes oberes Verhältnis zählt ebenfalls als positive Breite. Die Breitenprüfung verwendet die festgelegte Toleranz. Falls kein Kandidat diese Relevanz besitzt, bleibt der machbare Fallback gemäß derselben Intervallanalyse erhalten.

Diese Definition ist nicht austauschbar mit „jede geschlossene LP-machbare Alternative“ oder „jede Alternative mit positivem Volumen“. Insbesondere werden Kandidatenauswahl, Volumenberechnung und tatsächliche Konfidenzentscheidung getrennt behandelt. Terminelle Fastpaths dürfen dieselbe Mitgliedschaft günstiger feststellen, ändern aber nicht die Definition.

Ein Ziel ist als Matrixform erlaubt, besitzt im Ratioverfahren jedoch keine geordneten Zielpaare. Die tatsächliche Kandidatenanalyse bleibt dann leer; der SDK meldet `PlanningInvariantError`. Es wird keine zusätzliche eindimensionale Auswahlmethode eingesetzt.

## Zulässige Fragen je Ebene

Bei verbleibender Planungstiefe `1` entstehen Ratioqueries aus den berechneten Intervallgrenzen mit dem festen Ratioepsilon. Bei verbleibender Tiefe größer `1` bestimmt `higher_depth_query_source` die Quelle:

| Quelle | Zulässige Queries oberhalb der letzten Ebene |
| --- | --- |
| `grid` | Logarithmisches Grid mit `grid_size` Werten. |
| `both` | Dieses Grid plus Ratioqueries. |

Das Grid reicht im aktiven Profil von `0.001` bis `100`. Quellzuordnung, Reihenfolge, Spiegelbereinigung und Filter bereits beantworteter Fragen gehören zur Methode. Die Ratioanalyse bleibt auch im Grid-only-Modus für die vorhandene Vorfilterung verfügbar, ohne dadurch zusätzliche Ratioqueries zu erzeugen.

Weniger zulässige Fragen bedeuten eine andere Suche. Grid-only oder ein anderes `grid_size` können Laufzeit, gewählte Fragen und erreichbare Endzustände verändern. Ebenso ist eine größere Tiefe keine Garantie für weniger tatsächlich gestellte Fragen: optimiert wird ein endlicher Erwartungshorizont, der nach der nächsten tatsächlichen Antwort erneut geplant wird.

## Geometrische Antwortwahrscheinlichkeiten

Die Planung verwendet die geometrischen Anteile der Antwortregionen im aktuellen Gewichtsraum. Die zugrunde liegende Verteilung ist gleichförmig bezüglich des verwendeten intrinsischen Volumenmaßes, bedingt auf die akzeptierten Antworten. Es werden keine Monte-Carlo-Punkte gezogen.

Reguläre nichtdegenerierte Queryschnittflächen haben Gleichheitswahrscheinlichkeit null. Ist eine Query im gesamten aktuellen affinen Raum konstant, kann stattdessen eine deterministische Antwort einschließlich `=` entstehen. Explizite Gleichheiten verändern den affinen Raum und damit das relevante Volumenmaß.

„Exakt geometrisch“ beschreibt die Berechnung ohne Sampling. Der reguläre Rechenweg verwendet Binary64, validierte LPs und Polytopegeometrie; begrenzte rationale Reparaturen sind eigene Fehlerpfade. Die numerischen Grenzen stehen in [Numerische Berechnung](numerical_behavior.md).

## Tatsächliches Ende und hypothetischer Loss

Die tatsächliche Prüfung nach jeder akzeptierten Antwort lautet:

1. Genau ein Kandidat: Ende mit `exact_single_candidate`.
2. Bei `VolumeConfidenceStop(threshold)`: maximaler Kandidatenvolumenanteil mindestens `threshold` ergibt `volume_confidence`.
3. Erreichtes Gesamtantwortbudget ergibt `max_questions`.
4. Andernfalls wird eine nächste Query geplant; fehlt diese, folgt `no_query`.

Konfidenzanteile werden nicht nachträglich über eine kleinere zurückgegebene Kandidatenmenge neu normalisiert. Ein exakter Gleichstand maximaler Anteile wird durch den ursprünglichen Zeilenindex entschieden. Konfidenz ist hier ein geometrischer Volumenanteil, kein statistisches Konfidenzintervall einer Stichprobe.

`planning_evaluation="candidate_count"` bewertet die tatsächliche erwartete terminale Kandidatenanzahl. Der tatsächliche Konfidenzstopp bleibt trotzdem aktiv, falls er als Stopregel konfiguriert wurde.

`planning_evaluation="stop_aware"` behandelt die konfigurierte Stopregel zusätzlich in hypothetischen Zuständen als absorbierend. Ein bereits akzeptierbarer Zustand erhält bewerteten Loss `1`, auch wenn noch mehrere Kandidaten existieren. Seine tatsächlich erwartete Kandidatenanzahl wird separat beibehalten. Bei Singletonstopp fügt diese Option keine andere Konfidenzschwelle hinzu.

## Feste Planung

`query_strategy="fixed"` verwendet bei jedem tatsächlichen Schritt erneut `depth`.

Ohne hypothetische Konfidenzabsorption wird die erwartete Kandidatenanzahl nach der festen Tiefe minimiert. Bei exakt gleichem besten Wert vergleicht der Planer flachere Erwartungswerte lexikographisch: erst `depth`, dann bei Bedarf `depth-1` und so weiter. Flachere Werte werden nur für die noch gebundenen besten Queries berechnet. Danach entscheidet die numerische Queryidentität `(goal_index_a, goal_index_b, value)`.

Mit `stop_aware` und einer Volumenkonfidenzregel minimiert Fixed stattdessen den erwarteten terminalen Loss. Bei gleichem Loss entscheidet direkt die Queryidentität. Dieser Pfad fügt nicht den gewöhnlichen flacheren lexikographischen Vergleich hinzu. Die tatsächliche Kandidatenerwartung bleibt im Ergebnis sichtbar. Fixed mit `SingleCandidateStop()` verwendet weiterhin den gewöhnlichen Kandidatenpfad.

## Adaptive erwartete Verringerung pro Query

`query_strategy="reduction_per_query"` betrachtet die Horizonte `1, ..., depth`. Für jeden zulässigen vollständigen Plan `pi` werden bestimmt:

```text
N       = aktuelle Kandidatenanzahl
L(pi)   = erwarteter terminaler Loss
Q(pi)   = erwartete Anzahl gestellter Fragen des Plans
gain    = N - L(pi)
rate    = gain / Q(pi)
```

Ohne Konfidenzabsorption ist `L(pi)` die erwartete Kandidatenanzahl. Die Auswahl maximiert `rate`. Exakte Gleichstände entscheidet die kleinere erwartete Queryzahl, danach der kleinere Horizont und danach die numerische Queryidentität. Die Rate ist ein Verhältnis von Erwartungen, nicht der Erwartungswert einzelner pfadweiser Raten.

Der Nenner zählt nicht stumpf den maximalen Horizont. Bereits terminale oder nicht fortsetzbare Pfade benötigen weniger Fragen. Für einen Rootplan gilt:

```text
Q(pi) = 1 + sum_answer P(answer) * Q(continuation_answer)
```

Endet beispielsweise ein Pfad mit Wahrscheinlichkeit `0.05` nach einer Frage und benötigen die übrigen Pfade drei Fragen, ist `Q = 0.05*1 + 0.95*3 = 2.9`. Die Wurzelfrage wird dabei genau einmal gezählt. Hypothetische Pfade mit Wahrscheinlichkeit null lösen keine zusätzliche Childberechnung aus.

### Horizont drei

Nach jeder positiven Rootantwort werden zulässige **vollständige H2-Kindpläne** aufgebaut. Gibt es eine vorgeschriebene Fortsetzung, darf das Kind weder freiwillig stoppen noch durch eine zusätzlich erfundene H1-Option ersetzt werden. Tatsächlich terminale oder nicht fortsetzbare Zustände haben dagegen ihre festgelegte Nullkostenoption.

Die H2-Optionen können unterschiedliche erwartete Kosten haben. Deshalb reicht es nicht, pro Kind dessen beste lokale Rate auszuwählen. Der Planer bildet Loss-/Kostenfrontiers vollständiger Kindpläne, entfernt exakt dominierte Optionen und wählt die global beste geordnete Kombination. Erwartete Loss- und Kostenwerte werden mit den Rootantwortwahrscheinlichkeiten gewichtet. Diese Kombination erhält den vollständigen zulässigen Optionsraum; eine heuristische Queryshortlist gehört nicht zur Methode.

Nach einer tatsächlichen Antwort wird erneut über alle erlaubten Root-Horizonte geplant. Ein ausgewählter H3-Plan ist somit eine Bewertung der aktuellen nächsten Frage und ihrer hypothetischen Fortsetzungen, keine Verpflichtung, anschließend drei Fragen ungeprüft abzuspulen.

## Beispiel: Konfidenzplanung verändert den Loss

Bei den Alternativen `(1,0)` und `(0,1)` und der Query `w0/w1 ? .91` hat der `>`-Zweig unter der gleichförmigen Verteilung auf dem Simplex mit zwei Gewichten (affine Dimension 1) Wahrscheinlichkeit `1/1.91`. Dort verbleiben zwei Kandidaten, aber Alternative 0 besitzt Anteil `(1+.91)/2 = .955`. Der `<`-Zweig ist ein Singleton.

Daraus folgt für den Ein-Frage-Plan:

| Bewertung | Erwartete tatsächliche Kandidatenanzahl | Bewerteter Loss |
| --- | --- | --- |
| `candidate_count` | `1 + 1/1.91` | `1 + 1/1.91` |
| `stop_aware`, Schwelle `.95` | `1 + 1/1.91` | `1` |
| `stop_aware`, Schwelle `.99` | `1 + 1/1.91` | `1 + 1/1.91` |

Ein anderer Loss kann absichtlich eine andere Queryauswahl ergeben. Das ist eine fachliche Konfigurationsänderung und keine reine Beschleunigung derselben Rechnung.

## Grenzen der Aussage

`no_query` und `max_questions` sind reguläre ungelöste Ergebnisse. Numerische Fehler, widersprüchliche Antworten oder verletzte Invarianten sind Fehler mit Partialkontext. Es gibt keine Garantie, dass eine endliche zulässige Querymenge jedes Problem zu einem Singleton führt, dass größere Horizonte immer bessere tatsächliche Verläufe ergeben oder dass jede degenerierte Geometrie numerisch lösbar ist.

Die Planung kann unabhängige Rootbewertungen parallel ausführen. Unterbäume bleiben seriell; Workeranzahl und Cachepolicy begrenzen die Ausführung und ändern keine erlaubte Querymenge, Tiefe oder Konfidenzschwelle. Der [API-Vertrag](python_api.md) beschreibt tatsächliche Antworten, Zähler und Fehler; [Konfiguration](configuration.md) trennt diese fachlichen Entscheidungen vom Laufzeitrahmen.
