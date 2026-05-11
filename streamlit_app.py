import io
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import soundfile as sf
import streamlit as st
from scipy.signal import resample_poly

TARGET_SR = 44100


def load_audio_from_upload(uploaded_file, target_sr: int = TARGET_SR) -> Tuple[np.ndarray, int]:
    raw = uploaded_file.read()
    bio = io.BytesIO(raw)
    data, sr = sf.read(bio)
    if data.ndim > 1:
        data = data.mean(axis=1)
    if sr != target_sr:
        data = resample_poly(data, target_sr, sr)
        sr = target_sr
    data = data.astype(np.float64)
    data = data / (np.max(np.abs(data)) + 1e-12)
    return data, sr


def record_audio(seconds: float, sr: int = TARGET_SR) -> np.ndarray:
    rec = sd.rec(int(seconds * sr), samplerate=sr, channels=1, dtype="float64")
    sd.wait()
    audio = rec[:, 0]
    audio = audio / (np.max(np.abs(audio)) + 1e-12)
    return audio


def rfft_spectrum(signal: np.ndarray, sr: int, max_freq: float = 5000.0) -> Tuple[np.ndarray, np.ndarray]:
    windowed = signal * np.hanning(len(signal))
    spec = np.fft.rfft(windowed)
    freqs = np.fft.rfftfreq(len(windowed), d=1.0 / sr)
    mag = np.abs(spec)
    keep = freqs <= max_freq
    freqs = freqs[keep]
    mag = mag[keep]
    mag = mag / (mag.max() + 1e-12)
    return freqs, mag


def get_top_peaks(freqs: np.ndarray, mag: np.ndarray, n_peaks: int = 12, min_freq: float = 40.0) -> List[Tuple[float, float]]:
    valid = freqs >= min_freq
    f = freqs[valid]
    m = mag[valid]
    if len(m) == 0:
        return []
    idx = np.argpartition(m, -min(n_peaks, len(m)))[-min(n_peaks, len(m)) :]
    idx = idx[np.argsort(m[idx])[::-1]]
    return [(float(f[i]), float(m[i])) for i in idx]


def peak_containment_score(song_freqs: np.ndarray, song_mag: np.ndarray, seg_freqs: np.ndarray, seg_mag: np.ndarray, tolerance_hz: float = 5.0) -> float:
    song_peaks = np.array([p[0] for p in get_top_peaks(song_freqs, song_mag)])
    seg_peaks = np.array([p[0] for p in get_top_peaks(seg_freqs, seg_mag)])
    if len(song_peaks) == 0 or len(seg_peaks) == 0:
        return 0.0
    matches = 0
    for f in seg_peaks:
        if np.any(np.abs(song_peaks - f) <= tolerance_hz):
            matches += 1
    return matches / len(seg_peaks)


st.set_page_config(page_title="Shazam demonstracija", layout="wide")
st.title("Shazam Demonstracija")
st.write("Učitaj pjesmu i segmente, izračunaj RFFT spektre i usporedi original s izvedbom.")
if "perf_audio" not in st.session_state:
    st.session_state["perf_audio"] = None
if "spectrum_segments" not in st.session_state:
    st.session_state["spectrum_segments"] = None
if "comparison_result" not in st.session_state:
    st.session_state["comparison_result"] = None


def compute_segment_spectrum_cache(
    song_audio: np.ndarray, sr: int, segments: List[Tuple[float, float]]
) -> dict:
    song_freqs, song_mag = rfft_spectrum(song_audio, sr)
    curves: List[Tuple[np.ndarray, np.ndarray, int]] = []
    scores: List[Tuple[int, float]] = []
    for i, (start, dur) in enumerate(segments, start=1):
        a = int(start * sr)
        b = int((start + dur) * sr)
        seg = song_audio[a:b]
        if len(seg) < 2048:
            continue
        seg_freqs, seg_mag = rfft_spectrum(seg, sr)
        curves.append((seg_freqs, seg_mag, i))
        score = peak_containment_score(song_freqs, song_mag, seg_freqs, seg_mag)
        scores.append((i, score))
    return {"song_freqs": song_freqs, "song_mag": song_mag, "curves": curves, "scores": scores}


def render_segment_spectrum_figure(cache: dict, figsize: Tuple[float, float] = (13, 7)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(cache["song_freqs"], cache["song_mag"], linewidth=1.4, label="Cijela pjesma")
    for seg_freqs, seg_mag, i in cache["curves"]:
        ax.plot(seg_freqs, seg_mag, linewidth=1.2, label=f"Segment {i}")
    ax.set_xlabel("Frekvencija (Hz)")
    ax.set_ylabel("Normalizirana magnituda")
    ax.set_title("RFFT: cijela pjesma i segmenti")
    ax.grid(alpha=0.3)
    ax.legend()
    return fig


def render_compare_figure(
    song_freqs: np.ndarray,
    song_mag: np.ndarray,
    perf_freqs: np.ndarray,
    perf_mag: np.ndarray,
    figsize: Tuple[float, float] = (6.4, 5),
):
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(song_freqs, song_mag, label="Original", linewidth=1.4)
    ax.plot(perf_freqs, perf_mag, label="Izvedba", linewidth=1.2)
    ax.set_xlabel("Frekvencija (Hz)")
    ax.set_ylabel("Normalizirana magnituda")
    ax.set_title("Original vs izvedba (RFFT)")
    ax.grid(alpha=0.3)
    ax.legend()
    return fig

st.subheader("Shazam demonstracija: cijela pjesma i segmenti")
song_file = st.file_uploader("Učitaj cijelu pjesmu", type=["wav", "mp3", "flac", "ogg", "m4a"])
n_segments = st.number_input("Broj segmenata", min_value=1, max_value=12, value=6, step=1)
mode = st.radio("Način odabira segmenata", ["Automatski", "Ručno"])

if song_file is not None:
    song_audio, sr = load_audio_from_upload(song_file, TARGET_SR)
    duration = len(song_audio) / sr
    st.info(f"Trajanje pjesme: {duration:.2f} s")

    segments = []
    if mode == "Automatski":
        seg_len = duration / (int(n_segments) + 1)
        for i in range(int(n_segments)):
            start = i * seg_len
            dur = min(seg_len, duration - start)
            segments.append((start, dur))
        st.caption("Segmenti su ravnomjerno raspoređeni kroz pjesmu.")
    else:
        st.write("Unesi start i trajanje svakog segmenta:")
        for i in range(int(n_segments)):
            c1, c2 = st.columns(2)
            with c1:
                start = st.number_input(
                    f"Segment {i + 1} start (s)",
                    min_value=0.0,
                    max_value=max(0.0, float(duration)),
                    value=float(min(i * 2.0, max(0.0, duration - 1.0))),
                    key=f"start_{i}",
                )
            with c2:
                max_dur = max(0.1, float(duration - start))
                dur = st.number_input(
                    f"Segment {i + 1} trajanje (s)",
                    min_value=0.1,
                    max_value=max_dur,
                    value=float(min(2.0, max_dur)),
                    key=f"dur_{i}",
                )
            segments.append((float(start), float(dur)))

    if st.button("Izračunaj i prikaži spektre"):
        st.session_state["spectrum_segments"] = compute_segment_spectrum_cache(song_audio, sr, segments)

    st.markdown("---")
    st.subheader("Usporedba originala i tvoje izvedbe")
    perf_mode = st.radio("Izvedba", ["Učitaj snimku izvedbe", "Snimi odmah mikrofonom"], horizontal=True)

    perf_audio = None
    if perf_mode == "Učitaj snimku izvedbe":
        perf_file = st.file_uploader("Učitaj izvedbu", type=["wav", "mp3", "flac", "ogg", "m4a"], key="perf_upload")
        if perf_file is not None:
            perf_audio, _ = load_audio_from_upload(perf_file, TARGET_SR)
            st.session_state["perf_audio"] = perf_audio
    else:
        perf_sec = st.slider("Trajanje snimanja izvedbe (sek)", 3.0, 60.0, 20.0, 1.0)
        if st.button("Snimi izvedbu"):
            with st.spinner("Snimam izvedbu..."):
                perf_audio = record_audio(perf_sec, TARGET_SR)
                st.session_state["perf_audio"] = perf_audio
                st.success("Snimka gotova.")

    if st.button("Usporedi original i izvedbu"):
        perf_audio = st.session_state.get("perf_audio")
        if perf_audio is None:
            st.error("Prvo učitaj ili snimi izvedbu.")
        else:
            n = min(len(song_audio), len(perf_audio))
            if n < sr:
                st.warning("Izvedba je vrlo kratka; rezultat može biti nepouzdan.")

            song_freqs, song_mag = rfft_spectrum(song_audio[:n], sr)
            perf_freqs, perf_mag = rfft_spectrum(perf_audio[:n], sr)

            cosine = float(np.dot(song_mag, perf_mag) / ((np.linalg.norm(song_mag) * np.linalg.norm(perf_mag)) + 1e-12))
            overlap = peak_containment_score(song_freqs, song_mag, perf_freqs, perf_mag)
            score = 0.7 * cosine + 0.3 * overlap

            st.session_state["comparison_result"] = {
                "song_freqs": song_freqs,
                "song_mag": song_mag,
                "perf_freqs": perf_freqs,
                "perf_mag": perf_mag,
                "cosine": cosine,
                "overlap": overlap,
                "score": score,
            }

    seg_cache = st.session_state.get("spectrum_segments")
    cmp_res = st.session_state.get("comparison_result")

    if cmp_res is not None:
        c1, c2, c3 = st.columns(3)
        c1.metric("Cosine sličnost", f"{cmp_res['cosine']:.3f}")
        c2.metric("Preklapanje vrhova", f"{cmp_res['overlap'] * 100:.1f}%")
        c3.metric("Ukupna ocjena", f"{cmp_res['score'] * 100:.1f}/100")

        st.subheader("Spektri (istovremeni prikaz)")
        if seg_cache is not None:
            st.caption("Lijevo: cijela pjesma i segmenti. Desno: original i tvoja izvedba (isti vremenski odsječak koliko dopuštaju snimke).")
            col_a, col_b = st.columns(2, gap="medium")
            with col_a:
                fig_left = render_segment_spectrum_figure(seg_cache, figsize=(6.4, 5))
                st.pyplot(fig_left, use_container_width=True)
                plt.close(fig_left)
            with col_b:
                fig_cmp = render_compare_figure(
                    cmp_res["song_freqs"],
                    cmp_res["song_mag"],
                    cmp_res["perf_freqs"],
                    cmp_res["perf_mag"],
                    figsize=(6.4, 5),
                )
                st.pyplot(fig_cmp, use_container_width=True)
                plt.close(fig_cmp)
        else:
            st.info(
                "Nema spremljenog spektra s segmentima. Klikni „Izračunaj i prikaži spektre“ iznad, pa ponovno „Usporedi…“ da vidiš oba grafa jedno pokraj drugog."
            )
            fig_cmp = render_compare_figure(
                cmp_res["song_freqs"],
                cmp_res["song_mag"],
                cmp_res["perf_freqs"],
                cmp_res["perf_mag"],
                figsize=(13, 6),
            )
            st.pyplot(fig_cmp, use_container_width=True)
            plt.close(fig_cmp)
    elif seg_cache is not None:
        st.subheader("Spektar cijele pjesme i segmenti")
        fig_seg = render_segment_spectrum_figure(seg_cache)
        st.pyplot(fig_seg, use_container_width=True)
        plt.close(fig_seg)

    if seg_cache is not None:
        st.write("**Sadržanost segmenta u pjesmi (dominantni vrhovi spektra):**")
        for i, score in seg_cache["scores"]:
            st.write(f"- Segment {i}: {score * 100:.1f}% poklapanja")
