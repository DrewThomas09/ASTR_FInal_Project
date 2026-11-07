"""Offline FITS loader test, no NASA network needed.

Builds a short synthetic Kepler-like binary table under the exact expected path.
This verifies archive file naming, quality flags and normalization, not astronomy.
"""
import hashlib
import numpy as np
import pytest

astropy = pytest.importorskip("astropy")
from astropy.io import fits
from real_kepler_lightcurve import fetch_kepler_quarter


def fake_quarter(path,quarter=8,rows=1100):
    n=rows
    rng=np.random.default_rng(22)
    t=np.arange(n,dtype=float)*(29.4244/60/24)+350.
    f=20000.+rng.normal(0,30,n)
    q=np.zeros(n,dtype=np.int32)
    q[::29]=1
    columns=fits.ColDefs([
       fits.Column(name="TIME",format="D",array=t),
       fits.Column(name="PDCSAP_FLUX",format="E",array=f.astype("f4")),
       fits.Column(name="SAP_QUALITY",format="J",array=q)])
    head=fits.PrimaryHDU()
    head.header["QUARTER"]=quarter
    fits.HDUList([head,fits.BinTableHDU.from_columns(columns)]).writeto(path)
    return n-int((q!=0).sum())


def test_known_kic_quarter_loaded_without_network(monkeypatch,tmp_path):
    monkeypatch.chdir(tmp_path)
    from pathlib import Path
    path=Path("data/kepler_fits/kplr008692861-2011073133259_llc.fits")
    path.parent.mkdir(parents=True)
    n_expected=fake_quarter(path)
    t,flux,metadata=fetch_kepler_quarter("KIC 8692861",8)
    assert len(t)==n_expected
    assert len(flux)==n_expected
    assert np.isfinite(flux).all()
    assert np.isclose(np.median(flux),1.0)
    assert metadata["sha256"]==hashlib.sha256(path.read_bytes()).hexdigest()
    assert metadata["kic_id"]=="008692861"
    assert "quarter" in metadata["file"] or metadata["file"].endswith("_llc.fits")


def test_wrong_quarter_header_rejected(monkeypatch,tmp_path):
    monkeypatch.chdir(tmp_path)
    from pathlib import Path
    path=Path("data/kepler_fits/kplr008692861-2011073133259_llc.fits")
    path.parent.mkdir(parents=True)
    fake_quarter(path,quarter=7)
    with pytest.raises(ValueError,match="quarter"):
        fetch_kepler_quarter("KIC 8692861",8)
