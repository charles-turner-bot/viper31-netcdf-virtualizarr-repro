import json
from pathlib import Path

nb = {
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "# Viper-31 NetCDF → VirtualiZarr repro\n",
        "\n",
        "This notebook reproduces the issue from `Viper-31/S3-Kerchunk-streamer` issue #4 against the shared sample file.\n"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "from pathlib import Path\n",
        "from obspec_utils.registry import ObjectStoreRegistry\n",
        "from obstore.store import LocalStore\n",
        "from virtualizarr.parsers import HDFParser\n",
        "import xarray as xr\n",
        "import virtualizarr as vz\n",
        "DATA = Path('../data/2022-11_DPIRD_slice.nc').resolve()\n",
        "URL = f'file://{DATA}'\n",
        "REGISTRY = ObjectStoreRegistry({'file://': LocalStore()})\n",
        "LOADABLE = ['station', 'code']\n",
        "DATA.exists(), DATA.stat().st_size if DATA.exists() else None\n"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "ds = xr.open_dataset(DATA, engine='h5netcdf')\n",
        "ds\n"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "[name for name, var in ds.coords.items() if getattr(var.dtype, 'kind', '') in {'U', 'S', 'O'}]\n"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "vds = vz.open_virtual_dataset(\n",
        "    url=URL,\n",
        "    registry=REGISTRY,\n",
        "    parser=HDFParser(),\n",
        "    loadable_variables=LOADABLE,\n",
        ")\n",
        "vds\n"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "summary = Path('../artifacts/summary.json')\n",
        "print(summary.read_text()) if summary.exists() else print('Run `pixi run repro` first')\n"
      ]
    }
  ],
  "metadata": {
    "kernelspec": {
      "display_name": "Python 3",
      "language": "python",
      "name": "python3"
    },
    "language_info": {
      "name": "python",
      "version": "3.12"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 5
}

out = Path('notebooks/repro.ipynb')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(nb, indent=2) + '\n')
print(f'wrote {out}')
