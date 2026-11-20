# makefun-world-news-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/adjiadjo/makefun-world-news-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/adjiadjo/makefun-world-news-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

One image summarising the world's news of **Friday 20 November 2026**, entered in
make.fun's "Sum up 20 November's world news in one image" bounty ($250 in USDC).

The artwork is an original front-page-style illustration (`entry.png`, 1024×1024,
~102 KiB) with six sourced stories of the day:

1. **Kyiv under missile attack** — Russia's overnight barrage into 20 Nov, retaliation
   for Ukraine's Crimean Bridge strike (Kyiv Independent).
2. **Cyclone Akvan landfall today** — severe cyclonic storm crossing the Odisha–Andhra
   coast near Gopalpur around noon; ~50,000 evacuated; third Bay of Bengal cyclone in a
   month (IMD / Down To Earth).
3. **Albanese meets Xi at APEC** — Friday bilateral in Shenzhen, beef trade top of the
   agenda after the superpowers' "peace declaration" (ABC News / AAP / The New Daily).
4. **World Children's Day** — Save the Children: a record 589 million children (1 in 4)
   lived in conflict zones in 2025 (ReliefWeb).
5. **Iowa: Army blasts 5 tons** — controlled noon detonation of degraded lead azide at
   the Iowa Army Ammunition Plant, Middletown; evacuations and lead-dust precautions
   (U.S. Army advisory / AP).
6. **Wellington Test: Day 2** — New Zealand 243/5 overnight, Nicholls 113*, Phillips 94*,
   Bumrah 3-52 (AFP / RNZ).

Full source list with URLs: [SOURCES.md](SOURCES.md).

## Run it

```sh
python3 main.py            # sandbox: writes /output/entry.png
```

`main.py` is standard-library-only Python (3.13 in the sandbox): it copies the
committed `entry.png` to `$MAKEFUN_OUTPUT_DIR` (default `/output`) and verifies the
copy's SHA-256. No network, no dependencies, byte-identical on every run.

Local preview:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Reproducibility

`render.py` is the build-time renderer that drew the artwork from scratch with
Pillow (flat vector-style panels, fixed random seeds, no clocks, no network). It
needs Pillow and system fonts (Georgia/Arial on Windows; DejaVu fallback) and is
**not** part of the sandbox runtime. Regenerate with:

```sh
python render.py --out entry.png --preview preview-300.png
```

The committed `entry.png` is the judged artifact; the runtime never re-renders it,
so sandbox determinism does not depend on fonts or Pillow versions.

## License

MIT — see [LICENSE](LICENSE). The illustration is original work; no third-party
photographs, characters or artwork are copied.

---

<sub>Entered on [make.fun](https://make.fun/?ref=cryptomadn3s&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
