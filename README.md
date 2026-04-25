# Viper-31 NetCDF → VirtualiZarr repro

Small scratch repro for the issue discussed in:

- <https://github.com/Viper-31/S3-Kerchunk-streamer/issues/4>

## What this does

- downloads the shared sample NetCDF from the Google Drive link in the issue comments
- inspects it with `xarray`
- tries `virtualizarr.open_virtual_dataset(...)`
- writes a JSON summary to `artifacts/summary.json`
- generates a simple Jupyter notebook in `notebooks/repro.ipynb`

## Quick start

```bash
pixi run download
pixi run repro
pixi run make-notebook
```

or all at once:

```bash
pixi run all
```

## Findings

Running the repro locally against the shared sample gives:

- sample size: **162,001,355 bytes** (~154.5 MiB)
- xarray dims: `station=192`, `time=5856`
- string-like coords detected: `station`, `code`
- VirtualiZarr result: **reproduced the same failure**

Exact error:

```text
AttributeError: 'bytes' object has no attribute 'item'
```

This occurs inside VirtualiZarr's HDF parser when it tries to read a fill value for byte-backed string data.

## Notes

- The sample file is **not committed** to git.
- It is downloaded to `data/2022-11_DPIRD_slice.nc` on demand.
- The shared sample is about **154.5 MB**.
