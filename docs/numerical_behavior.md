# Numerische Berechnung

Reguläre LP- und Geometrieberechnungen verwenden endliche Binary64werte und die tatsächlichen SciPybackends. Queryidentitäten und mathematische Ergebnisse werden weder für Gleichstände gerundet noch anhand von Anzeigenamen sortiert. Mathematische Wirewerte erhalten einen separaten float.hex-Nachweis.

Das numerische Profil enthält die aktiven festen Query-, LP-, Geometrie- und Recoverywerte. Nutzerpolicy, Environmentprofil und Cachepolicy bleiben getrennt. Exakte geometrische Wahrscheinlichkeit bezeichnet hier Berechnung ohne Monte-Carlo-Sampling.

Die LPschicht validiert Eingaben und Ergebnisse vollständig. Ein verwendbarer nativer HiGHS-Pfad spart Vorbereitung und Modellaufbau; jede Rechnung bleibt ein Kaltsolve ohne Übernahme alter Basis oder Lösung. Fehlende Capabilities und ungewöhnliche Eingaben verwenden den vorgesehenen öffentlichen Fallback. Private Backendfähigkeiten werden tatsächlich geprüft.

Geometrie berücksichtigt explizite Gleichheiten, affine Dimensionen, validierte Innenpunkte und Eckpunkte. Eng begrenzte rationale Reparaturen gelten nur für ihre dokumentierten unterstützten Bereiche. Ein nicht unterstützter oder fehlgeschlagener numerischer Fall wird nicht durch Sampling, neue Toleranzen oder eine leere Erfolgsregion ersetzt.

Native Modelle und mutierbare Caches gehören zu genau einer Solver- beziehungsweise Workersession. Speicherbudgets sind vom tatsächlichen Querylimit unabhängig. Cachemiss oder Nichtaufnahme eines zu großen Eintrags führt zur normalen Rechnung. Gezählt gespeicherte Bytes sind kein allgemeines RSSversprechen.
