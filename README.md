# STRAtegie WochenEnde ArbeitsKreis SOLVER

Der solver wird über `make` angesteuert, am einfachsten ist es einfach die `config.yaml` zu editieren um die Timeslots und Räume festzulegen und dann das Planungssheet runterzulanden (Es muss `Planungssheet.ods` heißen).  
Der plan kann dann mit `make plan` erstellt werden und spuckt ein paar output formate aus.

Wenn einfach nur `make` bzw `make help` ausgeführt wird, wird ein kleines hilfe menü angezeigt.

## Required deps

- python
- python-venv
- python-pip
- make
