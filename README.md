# makefun-world-news-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/adjiadjo/makefun-world-news-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/adjiadjo/makefun-world-news-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

One image summarising the world's news of **Friday 20 November 2026**, entered in
make.fun's "Sum up 20 November's world news in one image" bounty ($250 in USDC).

The artwork is an original editorial news page (`entry.png`, 1024×1024) with **18
stories** arranged as three lead headlines, five illustrated briefs in the left
column, and ten text-only briefs at right. The leads cover Russia's attack on
Ukraine, the Poland airspace incident, and new UK–EU agreements. Illustrated
briefs cover Cyclone Akvan, COP31, the Xi–Albanese meeting, UNICEF's Ukraine
child-casualty figures, and the Saudi–Houthi exchange. The ten additional briefs
span Myanmar, South Korea, markets, Italy, South Sudan, Gaza, New York,
UEFA, cricket, and Iraq. The exact wording and cited source URLs are in
[NEWS.md](NEWS.md); [SOURCES.md](SOURCES.md) explains the source mapping.

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

`render-v2.py` is the build-time renderer that draws the artwork from scratch with
Pillow (original two-ink vector-style illustrations; no clocks, no network). It
needs Pillow and system fonts (Georgia/Arial on Windows) and is
**not** part of the sandbox runtime. Regenerate with:

```sh
python render-v2.py --out entry.png --preview preview-300.png
```

The committed `entry.png` is the judged artifact; the runtime never re-renders it,
so sandbox determinism does not depend on fonts or Pillow versions.

## License

MIT — see [LICENSE](LICENSE). The illustration is original work; no third-party
photographs, characters or artwork are copied.

---

<sub>Entered on [make.fun](https://make.fun/?ref=cryptomadn3s&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
