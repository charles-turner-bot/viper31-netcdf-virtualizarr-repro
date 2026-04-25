from pathlib import Path
import json
import traceback

from obspec_utils.registry import ObjectStoreRegistry
from obstore.store import LocalStore
import xarray as xr
import virtualizarr as vz
from virtualizarr.parsers import HDFParser

DATA = Path("data/2022-11_DPIRD_slice.nc")
OUT = Path("artifacts")
OUT.mkdir(exist_ok=True)

summary = {
    "file": str(DATA),
    "exists": DATA.exists(),
    "size_bytes": DATA.stat().st_size if DATA.exists() else None,
}

if not DATA.exists():
    raise SystemExit("sample file missing; run `pixi run download` first")

url = f"file://{DATA.resolve()}"
registry = ObjectStoreRegistry({"file://": LocalStore()})
loadable_variables = ["station", "code"]

# Quick inspection using xarray/h5netcdf first
try:
    ds = xr.open_dataset(DATA, engine="h5netcdf")
    summary["xarray_dims"] = {k: int(v) for k, v in ds.sizes.items()}
    summary["xarray_coords"] = list(ds.coords)
    summary["string_like_coords"] = [
        name for name, var in ds.coords.items() if getattr(var.dtype, "kind", "") in {"U", "S", "O"}
    ]
    ds.close()
except Exception as e:
    summary["xarray_open_error"] = repr(e)

summary["virtualizarr_url"] = url
summary["virtualizarr_loadable_variables"] = loadable_variables

try:
    vds = vz.open_virtual_dataset(
        url=url,
        registry=registry,
        parser=HDFParser(),
        loadable_variables=loadable_variables,
    )
    summary["virtualizarr_status"] = "success"
    summary["virtualizarr_variables"] = list(vds.variables)
    summary["virtualizarr_dims"] = {k: int(v) for k, v in vds.sizes.items()}
except Exception as e:
    summary["virtualizarr_status"] = "error"
    summary["virtualizarr_error_type"] = type(e).__name__
    summary["virtualizarr_error"] = str(e)
    summary["virtualizarr_traceback"] = traceback.format_exc()

(OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
