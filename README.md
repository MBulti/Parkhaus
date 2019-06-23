# Parkhaus

Steuerungssoftware für das Parkhaus.
Der Server übernimmt die Berechnung, während der Client den Aufruf der einzelnen Funktionen wahrnimmt.
Für das Frontend nutzen wir HTML. Für das Backend wird Python verwendet.

# Installation

Damit das Projekt läuft, muss Flask installiert werden. Hier nutzen wir den Paket Manager von Python3 (pip3)

- Flask installation:
sudo pip3 install Flask

- Webserver starten:
um das Projekt mit Debugger zu starten (auf Port achten)
python3 Webserver.py 

# Anforderungen

Es ist eine Steuerungssoftware für die Zufahrtssteuerung eines Parkhauses
zu entwickeln:

Gegeben ist ein Parkhaus mit einer Kapazität von 180 Plätzen.
Für die Steuerung sind folgende Parameter zu beachten:

Von den 180 Plätzen sind 40 Plätze für Dauerkartenbesitzer reserviert. 
Eine Zufahrt für Kurzparker ist gegen Ausgabe eines Tickets immer
dann möglich, wenn mehr als 4 freie Plätze zur Verfügung stehen.
Die Ausfahrt eines Fahrzeuges erhöht die Anzahl der freien Plätze.
Dauerparker können über die 40 Plätze hinaus auf freie Plätze 
aus dem allgemeinen Kontingent eingelassen werden. 
Bei der Einfahrt muss deshalb zwischen den beiden Arten von
Nutzern unterschieden werden
Am Parkscheinautomaten soll die Anzahl der freien Plätze für
Kurzparker angezeigt werden, unterschreitet diese die Anzahl von 4
Plätzen, wird belegt angezeigt. Dauerparker können dennoch
einfahren, sofern noch Plätze aus dem reservierten Kontingent frei
sind.
Eine Ausfahrt soll immer möglich sein.
Die Parker sind zur Ermittlung der Kosten mit Kennzeichen, Einfahrt-
und Ausfahrtdatum in einer DB zu speichern.
Die Ermittlung der Belegung kann, muss aber nicht zwingend über
die DB ermittelt werden (Unter Verwendung der DB wäre das
System wiedereinschaltsicher).
Bei Ausfahrt wird die Parkgebühr am Automaten angezeigt, der
Einfachheit halber erfolgt die Bezahlung für Kurzparker durch einen
Button zur Bestätigung der Zahlung.
Dauerkartenbesitzer fahren nach Betätigung eines anderen Buttons
aus, wobei die Ausfahrtzeit in der DB vermerkt wird. Die Abrechnung
erfolgt später und ist nicht Gegenstand dieses Projektes
Entwerfen Sie die Software je nach Gruppenzugehörigkeit als 
Client / Server- Anwendung mit einem Webclient für die Zufahrtskontrolle.
