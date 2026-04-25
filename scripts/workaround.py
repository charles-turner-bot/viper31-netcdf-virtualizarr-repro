from __future__ import annotations

from pathlib import Path
import json

from obspec_utils.registry import ObjectStoreRegistry
from obstore.store import LocalStore
import xarray as xr
import virtualizarr as vz
from virtualizarr.parsers import HDFParser

DATA = Path("data/2022-11_DPIRD_slice.nc")
OUT = Path("artifacts")
OUT.mkdir(exist_ok=True)
REFS_PATH = OUT / "workaround-kerchunk.json"
SUMMARY_PATH = OUT / "workaround-summary.json"

STRING_COORDS = ["station", "code"]
CHECK_VAR = "airTemperature"

if not DATA.exists():
    raise SystemExit("sample file missing; run `pixi run download` first")

url = f"file://{DATA.resolve()}"
registry = ObjectStoreRegistry({"file://": LocalStore()})

summary: dict[str, object] = {
    "file": str(DATA),
    "string_coords_dropped_during_virtualization": STRING_COORDS,
}

# Work around the current HDF parser bug by dropping the byte-backed string
# coordinate variables during manifest construction, then reattaching them as
# regular loaded coordinates before exporting kerchunk refs.
vds = vz.open_virtual_dataset(
    url=url,
    registry=registry,
    parser=HDFParser(drop_variables=STRING_COORDS),
)
summary["virtualized_coords_before_reattach"] = list(vds.coords)
summary["virtualized_data_vars"] = list(vds.data_vars)

with xr.open_dataset(DATA, engine="h5netcdf") as ds:
    station = ds["station"].values
    code = ds["code"].values
    expected = ds.isel(station=slice(0, 2), time=slice(0, 3)).load()

vds = vds.assign_coords(
    station=station,
    code=("station", code),
)
summary["coords_after_reattach"] = list(vds.coords)
summary["station_dtype_after_reattach"] = str(vds["station"].dtype)
summary["code_dtype_after_reattach"] = str(vds["code"].dtype)

refs = vds.vz.to_kerchunk(format="dict")
REFS_PATH.write_text(json.dumps(refs, indent=2) + "\n")
summary["kerchunk_refs_path"] = str(REFS_PATH)
summary["kerchunk_ref_count"] = len(refs.get("refs", {}))

roundtrip = xr.open_dataset(refs, engine="kerchunk")
observed = roundtrip.isel(station=slice(0, 2), time=slice(0, 3)).load()

data_var_names = list(expected.data_vars)
xr.testing.assert_identical(observed[data_var_names], expected[data_var_names])
xr.testing.assert_identical(observed[["station", "code"]], expected[["station", "code"]])

summary["roundtrip_check"] = "passed"
summary["checked_subset"] = {"station": 2, "time": 3}
summary["checked_variable"] = CHECK_VAR
summary["sample_station_values"] = station[:3].tolist()
summary["sample_code_values"] = code[:3].tolist()

SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
