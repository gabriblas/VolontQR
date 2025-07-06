# VolontQR

Questa repo contiene il codice sorgente per il generatore di codici QR usato da VolontMusic e la relativa interfaccia grafica. I codici QR vengono generati in parallelo piuttosto velocemente e il file risultante è abbastanza ottimizzato: anche migliaia di codici QR richiedono poco tempo per essere generati e occupano solitamente pochi MB.

Il codice è stato sviluppato secondo il principio "Everything Just Works Until You Do Something Slightly Different": altrimenti detto, la funzionalità principale c'è, ma è pieno di bug e tutto crolla e brucia se usato in maniera leggermente inconvenzionale. Tuttavia, sentitevi liberi di aprire issues e suggerimenti!

## Run e build

In primo luogo, clonare questa repo e navigare nella nuova directory:

```bash
git clone https://github.com/gabriblas/VolontQR
cd VolontQR
```

Per eseguire il codice direttamente da Python, consiglio di creare un virtual o conda environment. 
```bash
pip3 install -r requirements.txt
python3 main.py
```

È anche possibile effettuare il packaging degli script in un unico eseguibile tramite i tool della libreria NiceGUI. Per compilare l'eseguibile (dopo aver installato le dipendenze come sopra):

```bash
python3 build.py
```

Verranno create due cartelle `build` e `dist`. Il file eseguibile è in quest'ultima. Per creare una nuova build, le due cartelle devono essere eliminate manualmente.