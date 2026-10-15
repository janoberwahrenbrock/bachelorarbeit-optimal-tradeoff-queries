# Numerische Berechnung

Die Methode berechnet Antwortwahrscheinlichkeiten geometrisch ohne Monte-Carlo-Sampling. Reguläre Rechnungen verwenden endliche IEEE-754-Binary64werte, SciPy/HiGHS und Qhull. Der Ausdruck „exaktes Volumen“ bedeutet hier keine universelle symbolische oder beliebig genaue Arithmetik. Eine konkrete Rechnung muss die vorgesehenen Validierungen und Fallbacks bestehen; anderenfalls bleibt der Fehler sichtbar.

## Eingaben und aktive Profile

Matrix- und Querywerte werden beim fachlichen Eingang als endliche Binary64werte übernommen. Originalreihenfolge, Indizes und Vorzeichen von Null bleiben erhalten. Es gibt keine Normalisierung der Matrix und keine Rundung für Querygleichstände. Anzeige- oder Dateikennungen ersetzen keine mathematische Identität. Die native Wireprojektion ergänzt relevante Fließkommazahlen durch ihren `float.hex()`-Nachweis; Zähler bleiben Ganzzahlen.

Die Profile sind getrennt:

| Profil | Zweck |
| --- | --- |
| Numerisches Profil `otqa-exact-v1` | Aktive feste Query-, LP-, Geometrie- und Recoverywerte. |
| Cachepolicy `bounded_v1` | Sessionbesitz und unabhängige Entry-/Payloadbytegrenzen. |
| Ausführungsprofil der Dateilaufzeit | Qualifizierte Plattform-, Python-, Bibliotheks- und Backendkombination; konkrete Ausführungssettings werden gesondert gebunden. |
| Nutzerpolicy | Strategie, Horizonte, Queryquelle und Stopregel. |

Die Resolver in `otqa.numerics.profile` liefern eigene strukturierte Kopien der aktiven Werte. Sie sind ein Wartungs-/Provenienzvertrag, kein zusätzlicher frei änderbarer Policyparameter. Das numerische Profil enthält nur aktive Werte, keine Einstellungen für ausgeschaltete Samplingvarianten.

Wichtige feste Werte sind:

| Bereich | Aktiver Wert |
| --- | --- |
| Logarithmisches Grid | Grenzen `0.001` bis `100`; Anzahl aus `grid_size`. |
| Ratioqueryepsilon | `0.001`. |
| HiGHS primale/duale Machbarkeitstoleranz | Je `1e-10`. |
| Geometrietoleranz | `1e-10`. |
| Ratio-Kandidatenbreitentoleranz | `1e-12`. |
| Konservativer Supportabstand | Skalierter Abstand mit Faktor `100` und Untergrenze `1e-8`. |
| Rationale LP-Recovery | Höchstens `5` Variablen und `20_000` vollständige aktive Punkt-/Strahlkombinationen. |
| Rationale Geometrie-Recovery | Explizite affine Dimension höchstens `2`; Intrinsikfaktor mit Decimalpräzision `80`. |

Der Resolver ist die maßgebliche vollständige Liste. Änderungen an einem aktiven Wert sind Änderungen der numerischen Methode und müssen gesondert geprüft werden.

## LPs und native Vorbereitung

Alle erforderlichen kontinuierlichen LPs behalten Eingabeprüfung, Ergebnisstatus und primale Machbarkeitsvalidierung. Die Backendgrenze unterscheidet insbesondere optimal, unzulässig und unbeschränkt. Ein unbekannter numerischer Status wird nicht als leere Region interpretiert.

Für gewöhnliche unterstützte Eingaben kann der Adapter vorhandene HiGHSobjekte und vorbereitete Modellstrukturen wiederverwenden. Vor **jeder** Rechnung werden Modell-/Solverzustände nach dem festgelegten Ablauf neu geladen beziehungsweise geleert. Es werden keine alte Basis und keine alte Lösung als numerischer Warmstart verwendet. Die Wiederverwendung spart Aufbauarbeit, nicht mathematische Anforderungen.

Der Adapter prüft seine tatsächlichen Fähigkeiten und besitzt Prozess-/Threadzuordnung. Ungewöhnliche Eingabetypen, fehlende private Fähigkeiten oder ein Adapterfehler behalten den vorgesehenen öffentlichen SciPy-Fallback. Ein schneller validierter kontinuierlicher Ergebnischecker wird nur bei passendem überprüftem Quell-/Aufrufvertrag verwendet; sonst greift der Originalchecker. Keine Variante darf primale Validierungen weglassen.

Der festgelegte Fehlerpfad versucht bei erforderlichen erfolglosen LPs die Rechnung ohne Presolve und gegebenenfalls weitere HiGHSmethoden. Nur ein klassifiziertes oder erfolgreiches Ergebnis beendet diesen Pfad. Nach einem weiterhin unbekannten LP-Ergebnis kann die begrenzte rationale Recovery greifen. Ablehnung ihrer Voraussetzungen oder fehlende Darstellbarkeit führen nicht zu einem erfundenen Erfolgswert.

## Eckpunkte, affine Räume und Volumen

Explizite Gleichheiten werden zur affinen Reduktion verwendet. Die Volumenrechnung verwendet die intrinsische Dimension dieses expliziten affinen Raums:

- Eine explizite Gleichheit kann beispielsweise eine Fläche auf ein Intervall reduzieren; dann ist dessen intrinsische Länge relevant.
- Ein explizit definierter Punkt besitzt nach der festen Volumenkonvention Volumen null.
- Nur durch Ungleichungen degenerierte Regionen erhalten nicht automatisch das Maß einer neu erratenen kleineren Dimension.

Die reguläre Eckpunktberechnung prüft einen relativen Innenpunkt. Ist ein zurückgegebener Innenpunkt unbrauchbar, normiert der festgelegte Reparaturversuch vollständige Ungleichungszeilen durch positive Normen. Dies erhält die Ungleichungen; es werden keine Zeilen entfernt und keine Toleranzen passend zum gewünschten Ergebnis vergrößert.

Qhullvarianten, Containmentprüfung, begrenztes Snapping und ordnungserhaltende Eckpunktbereinigung folgen dem aktiven Profil. Auch ein Qhull-Fallback ist weiterhin numerische Geometrie. Falsche, unvollständige oder fehlgeschlagene Geometrie wird nicht als gültiger Supportcacheeintrag behalten.

Antwortregionen werden relativ zum aktuellen Parentraum gemessen und nach dem vorgesehenen Ablauf partitioniert. Eine konstante Query kann über LP-Support eine deterministische Antwort liefern, ohne neue Eckpunkte zu benötigen. Eine nichtkonstante Schnittfläche besitzt im regulären affinen Volumenmaß Gleichheitswahrscheinlichkeit null.

## Wiederverwendeter geometrischer Support

Vollständige, bereits validierte Eckpunkte können das Minimum und Maximum einer Querylinearform liefern. Nahe null liegende oder nichtendliche geometrische Grenzen bleiben unsicher. Dann wird die betroffene Grenze durch das ursprüngliche LP bestimmt; ist nur eine Grenze sicher, darf nur dieses eine LP entfallen.

Die Sicherheitsmarge skaliert mit Geometrie- und Objektivgröße. Dadurch ist ein kleiner Abstand außerhalb der eigentlichen Antworttoleranz nicht automatisch ein sicherer geometrischer Supportbeweis. Kalte Caches, andere Toleranzschlüssel, geänderte Constraints und eviktierte Eckpunkte verwenden den normalen LP-Pfad.

## Begrenzte rationale Reparaturen

Die rationale LP-Recovery arbeitet auf den **exakten Binary64eingaben** mittels `Fraction`, nicht auf einer Interpretation der eingegebenen Dezimalzeichenfolge. Sie benötigt explizite homogene Nichtnegativitätsconstraints und eine vollständig innerhalb der Grenzen aufzählbare Punkt-/Rezessionsgeometrie. Bei überschrittenem Limit wird keine unvollständige Enumeration als Zertifikat ausgegeben. Nichtendliche oder nicht positiv darstellbare Ergebnisse werden abgelehnt.

Die rationale Geometrie-Recovery benötigt explizite Simplex-/Nichtnegativitätsbedingungen und einen nach exakter Gleichheitselimination höchstens zweidimensionalen affinen Raum. Ein Problem mit vielen Zielen kann darunter fallen, wenn genügend **explizite** Gleichheiten vorliegen. Ein allgemeiner höherdimensionaler oder nur durch Ungleichungen dünner Raum erhält dadurch keine universelle Reparaturgarantie.

Diese Pfade behandeln festgelegte mehrdeutige Null-/Fehlerfälle. Rationale Antwortpartitionen prüfen gemeinsam, ob die Childmaße den Parent exakt aufteilen. Eine positive Wahrscheinlichkeit darf bei der anschließenden Binary64darstellung nicht unbemerkt zu null unterlaufen. Die Reparatur eines leeren positiven Kandidatenzweigs verlangt einen tatsächlichen strikten Singletonbeweis; sie wählt keinen beliebigen Parentkandidaten und erzwingt keine Tieauflösung.

Bei nicht unterstützter oder nicht zertifizierbarer Geometrie bleibt der numerische Fehler sichtbar. Weder Sampling noch eine willkürlich gelockerte Toleranz dienen als Ersatz.

## Volumenanteile und Konfidenz

Kandidatenvolumen und Kandidatenauswahl werden getrennt berechnet. Die Anteile verwenden die festgelegte Normalisierung über alle dabei geprüften Kandidaten vor der Relevanzfilterung. Zurückgegebene Kandidatenanteile werden anschließend nicht erneut auf Summe eins gebracht. Auch identische oder sich in Gleichstandsfällen überlappende Optimalitätsregionen ändern diese feste Konvention nicht.

Eine Konfidenzschwelle wird mit den vorhandenen Anteilen einschließlich geprüft. Sie ist ein Akzeptanzkriterium unter diesem geometrischen Modell, kein Stichproben-Konfidenzintervall und kein unabhängiger Nachweis des verborgenen Simulationsgewinners. Ein Konfidenzstopp kann mehrere tatsächliche Kandidaten zurücklassen.

## Sessionbesitz und Speichergrenzen

Jeder öffentliche Solveraufruf besitzt eine eigene Plannersession mit eigenen mathematischen States, Caches und Backendhandles. Ein Prozessworker registriert zunächst nur seine gebundenen Eingaben. Seine numerische Session und Finalisierung entstehen erst mit dem ersten tatsächlichen Task. Unbenutzte Worker erzeugen deshalb keine eager numerische Session. Innere Unterbäume bleiben seriell; es gibt keine verschachtelten Workerpool-Aufrufe.

PreparedStates besitzen unveränderliche geordnete Constraint- und Analysepayloads. Beim Prozessübergang werden keine nativen LPmodelle, Cacheinhalte oder Geometrysessionhandles serialisiert. Der Worker bindet den übertragenen Zustand an seine lokalen Ressourcen. Queryhistorien behalten für Cacheidentitäten ihre Reihenfolge und Fließkommabits einschließlich `-0.0`.

Die aktive Policy setzt folgende unabhängige Grenzen:

| Speicher | Grenze pro Solver-/Workersession |
| --- | --- |
| Prepared States / vollständige Rootentscheidungen | Je `16` Einträge. |
| Volumen | `32_768` Einträge. |
| Vollständige Eckpunkte | `32_768` Einträge und `64 MiB` gezählte Arraypayloads. |
| Affine Zerlegungen | `4_096` Einträge und `8 MiB` gezählte Payloads. |
| Native HiGHSmodelle | `32` Einträge und `4 MiB` gezählte Vorbereitungspayloads. |
| Native Optionsobjekte | `32` Einträge. |

Zu große Einträge werden normal berechnet und gegebenenfalls nicht gespeichert. Eviktion oder Cachemiss verändern weder Querymenge noch Ergebnisdefinition. Die Kapazitäten hängen nicht von `max_queries` ab. Ein neuer unabhängiger SDK-Aufruf übernimmt keine mutierbaren Caches eines vorherigen Aufrufs; dieser Besitzvertrag kann Aufbaukosten gegenüber einer prozessglobalen Wiederverwendung verursachen.

`close()` wartet auf eigene Worker und gibt die eigenen Backend-/Geometrie-/State-/Planungscaches frei. Andere Sessionen werden dabei nicht geleert. Getrackte Payloadbytes sind kein allgemeines RSSversprechen: Pythonobjekte, Schlüssel, temporäre Arrays, SciPy und native Solverallokationen besitzen zusätzliche Kosten.

## Reproduzierbarkeit und Grenzen

Mathematische Identitäten, Reihenfolgen, exakte Gleichstandsregeln und Cacheunabhängigkeit sind Teil des Vertrags. Trotzdem ist Bitgleichheit über beliebige neue SciPy-/Qhullversionen, Plattformen oder schlecht konditionierte Eingaben keine allgemeine Zusage. Die Dateilaufzeit bindet deshalb tatsächliche Quelle, Umgebung und numerisches Profil und qualifiziert unterstützte Kombinationen.

Zwei separat qualifizierte Umgebungen können für dieselben gespeicherten Matrix- und Oraclewerte unterschiedliche Queryfolgen und Queryzahlen erzeugen. Ihre Zertifikate bestätigen jeweils den angegebenen Betriebsumfang der eigenen Umgebung. Sie bescheinigen keine Bitgleichheit zwischen den Umgebungen. Kleine Unterschiede numerischer Supportgrenzen, Volumina oder nahezu gleicher Scores können eine andere Query auswählen; nach deren Antwort wird erneut geplant. Welche Grenze einen konkreten Unterschied ausgelöst hat, muss anhand der gespeicherten Planung und Zahlenbelege geprüft werden.

Eine gleiche korrekte Endauswahl bedeutet deshalb noch keine gleiche Trajektorie. Für einen Alt-Neu-Vergleich werden beide Implementierungen auf demselben Host mit derselben tatsächlichen Python-/NumPy-/SciPyumgebung und identischen Worker-, Thread-, Input- und Aufzeichnungsbedingungen geprüft. Ergebnisse aus verschiedenen qualifizierten Profilen bleiben getrennte Beobachtungen. Das [Laufzeitverfahren](performance.md) beschreibt die weiteren Vergleichsgrenzen.

Einzelne degenerierte oder hochdimensionale Zustände können explizit scheitern, auch wenn verwandte Fälle lösbar sind. Diese Fehler dürfen nicht als schnelle gelöste Fälle in eine Auswertung eingehen. Numerische Konformität und funktionale Tests sind außerdem kein allgemeiner Laufzeitnachweis; Timingvergleiche benötigen einen eigenen gleichen Ausführungs- und Aufzeichnungsscope.
