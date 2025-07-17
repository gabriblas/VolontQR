# VolontQR 🚀

[![License](https://img.shields.io/github/license/gabriblas/volontQR?color=orange)](https://github.com/gabriblas/VolontQR/blob/main/LICENSE)
[![Version](https://img.shields.io/github/v/release/gabriblas/volontQR?color=blue)](https://github.com/gabriblas/VolontQR/releases/latest)
[![Issues](https://img.shields.io/github/issues/gabriblas/volontQR?color=blue)](https://github.com/gabriblas/volontQR/issues)
![Blame](https://img.shields.io/badge/code_quality-so_bad_it's_good-green)

Questa repo contiene il codice sorgente per il generatore di codici QR usato da VolontMusic e la relativa interfaccia grafica. Questo strumento consente di creare un grande numero di biglietti, ognuno con un codice QR differente in base ad una lista di link (usato principalmente per permettere il voto dal pubblico in sala per contest musicali live). I codici QR vengono generati in parallelo piuttosto velocemente e il file risultante è abbastanza ottimizzato e compatto.

Il codice è stato sviluppato secondo il principio "Everything Just Works Until You Do Something Slightly Different": altrimenti detto, la funzionalità principale c'è, ma è pieno di bug e tutto crolla e brucia se usato in maniera leggermente inconvenzionale. Tuttavia, sentitevi liberi di aprire issues e inviare suggerimenti!

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

È anche possibile effettuare il packaging degli script in un unico eseguibile tramite i tool della libreria [NiceGUI](https://nicegui.io/) (che a sua volta utilizza [pyInstaller](https://pyinstaller.org/) e [pywebview](https://pywebview.flowrl.com/)). Per compilare l'eseguibile (dopo aver installato le dipendenze come sopra):

```bash
python3 build.py
```

Verranno create due cartelle `build` e `dist`. Il file eseguibile è in quest'ultima. Per creare una nuova build, le due cartelle devono essere eliminate manualmente.

## Releases

Per convenienza dello staff VolontMusic, file precompilati per Windows sono disponibili nella sezione release. In generale, tuttavia, scaricare eseguibili a caso da internet è [una](https://en.wikipedia.org/wiki/Computer_virus) [pessima](https://en.wikipedia.org/wiki/XZ_Utils_backdoor) [idea](https://www.cs.cmu.edu/~rdriley/487/papers/Thompson_1984_ReflectionsonTrustingTrust.pdf) e lo sconsiglio vivamente. Piuttosto, consiglio di clonare questa repo e leggere i contenuti dei file (sono poche centinaia di linee!).
