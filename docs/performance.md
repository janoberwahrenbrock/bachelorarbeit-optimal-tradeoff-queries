# Laufzeitprüfung

Eine Formatprüfung oder korrekte Endauswahl beweist keine unveränderte Laufzeit. Performanceabnahme braucht gespeicherte Fälle, deklarierte Konfiguration, tatsächliche Quellen-/Environmentbindung und passende Rohmessungen.

Die vollständige SDKzeit enthält Solverinitialisierung, benötigte Worker, Provider- und Callbackzeit, Bereinigung und normalen Return. Das vollständige äußere CLIgate enthält zusätzlich Vorbereitung, Prozessstart, erforderliche Terminalpersistenz und Cleanup. Native Teilzeiten besitzen eigene Grenzen und ersetzen die vollständige Zeit nicht.

Vergleichspaare verwenden gleiche Matrix, Antworten beziehungsweise Oracle, fachliche Parameter, Budget, Worker-/Threadzahl und Aufzeichnungsleistung. Kalte Prozesse, warme sequentielle SDK-Aufrufe und erster Import sind getrennte Messscopes. Profilierung und vollständige Diagnosecapture bleiben bei ungeprofilten Gates deaktiviert.

Der Messplan legt vorab Reihenfolge, Wiederholungen, Konfigurationsumfang, Budgets und Auswertung fest. Fehlgeschlagene, unterbrochene und ungelöste Läufe bleiben sichtbar. Eine Teilplanung liefert keine vollständige Problemlösungszeit. Bestätigte Regressionen werden untersucht; ein statistisch unklarer Unterschied wird nicht als Geschwindigkeitsfreigabe ausgegeben.

Native Betriebsqualifizierung prüft die tatsächlich ausgeführte Installation, numerische Konformität und Lifecycle-/Persistenzgrenzen. Daraus folgt keine allgemeine Performancefreigabe für andere Modi oder Umgebungen.
