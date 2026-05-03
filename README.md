# README

## Opis rada

Ovaj projekt predstavlja demonstracijsku aplikaciju izrađenu u programskom jeziku Python s ciljem prikaza osnovnih principa prepoznavanja audiozapisa. Aplikacija omogućuje spektralnu analizu cijele pjesme, analizu njezinih segmenata te usporedbu originalne snimke s korisničkom izvedbom.

## Funkcionalnosti

- učitavanje cijele pjesme
- odabir proizvoljnog broja segmenata
- automatski izračun spektra pomoću realnog FFT-a (RFFT)
- zajednički prikaz spektra cijele pjesme i segmenata na jednom grafu
- usporedba originalne pjesme i vlastite izvedbe (učitavanje ili snimanje mikrofonom)

## Cilj projekta

Cilj projekta je pokazati da su dominantne frekvencijske komponente odabranih segmenata sadržane u spektru cijele pjesme te demonstrirati osnovnu spektralnu sličnost između originalne snimke i korisničke izvedbe.

## Tehnologije

- Python
- Streamlit
- NumPy / SciPy
- Matplotlib
- SoundFile / SoundDevice

## Instalacija

```bash
pip install -r requirements.txt
```

## Pokretanje

```bash
streamlit run streamlit_app.py
```

Ako `streamlit` nije prepoznat:

```bash
python -m streamlit run streamlit_app.py
```

## Korištenje aplikacije

1. Učitaj cijelu pjesmu u jednom od podržanih formata (`wav`, `mp3`, `flac`, `ogg`, `m4a`).
2. Odaberi broj segmenata koje želiš analizirati.
3. Odaberi način segmentacije:
   - automatski (ravnomjerno raspoređeni segmenti)
   - ručno (start + trajanje svakog segmenta)
4. Pokreni izračun i prikaz spektra klikom na **Izračunaj i prikaži spektre**.
5. Analiziraj zajednički graf te postotak poklapanja dominantnih vrhova segmenata i cijele pjesme.
6. Po želji učitaj ili snimi vlastitu izvedbu te pokreni usporedbu s originalnom pjesmom.

## Napomena

Projekt je namijenjen edukacijskoj i demonstracijskoj uporabi. Implementacija ne predstavlja puni industrijski sustav audio otiska (fingerprinting) kakav koriste produkcijske platforme poput Shazama, nego pojednostavljeni model za potrebe analize i prikaza rezultata.
