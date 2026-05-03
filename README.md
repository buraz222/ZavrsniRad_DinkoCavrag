# Shazam Demo (Python + Streamlit)

Interaktivna Python aplikacija za demonstraciju osnovne ideje audio prepoznavanja:

- ucitavanje cijele pjesme
- odabir proizvoljnog broja segmenata
- automatski izracun spektra pomocu realnog FFT-a (RFFT)
- zajednicki prikaz spektra cijele pjesme i segmenata na jednom grafu
- usporedba originalne pjesme i vlastite izvedbe (upload ili snimanje mikrofonom)

## Cilj projekta

Pokazati da su dominantne frekvencijske komponente segmenata sadrzane u spektru cijele pjesme te demonstrirati osnovnu spektralnu slicnost izmedu originala i izvedbe.

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

## Koristenje aplikacije

1. Ucitaj cijelu pjesmu (`wav`, `mp3`, `flac`, `ogg`, `m4a`).
2. Odaberi koliko segmenata zelis analizirati.
3. Odaberi nacin segmentacije:
   - automatski (ravnomjerno rasporedeni segmenti)
   - rucno (start + trajanje svakog segmenta)
4. Klikni **Izracunaj i prikazi spektre**.
5. Pogledaj zajednicki graf i postotak poklapanja dominantnih peakova.
6. Opcionalno:
   - ucitaj svoju izvedbu ili je snimi mikrofonom
   - pokreni usporedbu originala i izvedbe

## Napomena

Ovo je demonstracijski projekt za edukacijsku uporabu i ne implementira puni industrijski audio fingerprinting kao produkcijske Shazam-like platforme.
