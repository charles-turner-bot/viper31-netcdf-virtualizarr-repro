# Viper-31 NetCDF → VirtualiZarr repro

Small scratch repro for the issue discussed in:

- <https://github.com/Viper-31/S3-Kerchunk-streamer/issues/4>

## What this does

- downloads the shared sample NetCDF from the Google Drive link in the issue comments
- inspects it with `xarray`
- tries `virtualizarr.open_virtual_dataset(...)`
- captures a working workaround that still produces virtual refs via VirtualiZarr
- writes JSON summaries to `artifacts/summary.json` and `artifacts/workaround-summary.json`
- generates a simple Jupyter notebook in `notebooks/repro.ipynb`

## Quick start

```bash
pixi run download
pixi run repro
pixi run workaround
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

## Workaround found

A practical workaround does work for this file:

1. virtualize the dataset with `station` and `code` dropped via `HDFParser(drop_variables=[...])`
2. load those two string coordinates normally with `xarray`
3. reattach them as regular coordinates on the virtual dataset
4. export kerchunk refs from the mixed dataset with `vds.virtualize.to_kerchunk(...)`
5. reopen the resulting refs with `xarray(..., engine="kerchunk")`

That produces a usable virtual reference dataset for this sample. The script is in `scripts/workaround.py` and writes:

- `artifacts/workaround-kerchunk.json`
- `artifacts/workaround-summary.json`

Interesting extra detail: even after patching the immediate `fillvalue.item()` crash, the raw HDF parser still runs into a second problem because these string variables come through `h5py` as `dtype=object`, which Zarr v3 cannot resolve automatically.

## Notes

- The sample file is **not committed** to git.
- It is downloaded to `data/2022-11_DPIRD_slice.nc` on demand.
- The shared sample is about **154.5 MB**.
