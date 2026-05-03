# Shazam demonstracija (Python + Streamlit)

Interaktivna Python aplikacija za demonstraciju osnovne ideje audio prepoznavanja:

- učitavanje cijele pjesme
- odabir proizvoljnog broja segmenata
- automatski izračun spektra pomoću realnog FFT-a (RFFT)
- zajednički prikaz spektra cijele pjesme i segmenata na jednom grafu
- usporedba originalne pjesme i vlastite izvedbe (upload ili snimanje mikrofonom)

## Cilj projekta

Pokazati da su dominantne frekvencijske komponente segmenata sadržane u spektru cijele pjesme te demonstrirati osnovnu spektralnu sličnost između originala i izvedbe.

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

1. Učitaj cijelu pjesmu (`wav`, `mp3`, `flac`, `ogg`, `m4a`).
2. Odaberi koliko segmenata želiš analizirati.
3. Odaberi način segmentacije:
   - automatski (ravnomjerno raspoređeni segmenti)
   - ručno (start + trajanje svakog segmenta)
4. Klikni **Izračunaj i prikaži spektre**.
5. Pogledaj zajednički graf i postotak poklapanja dominantnih vrhova.
6. Opcionalno:
   - učitaj svoju izvedbu ili je snimi mikrofonom
   - pokreni usporedbu originala i izvedbe

## Napomena

Ovo je demonstracijski projekt za edukacijsku uporabu i ne implementira puni industrijski audio fingerprinting kao produkcijske Shazam-like platforme.
