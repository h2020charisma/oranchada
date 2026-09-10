# Upgrade to ramanchada2 1.4.0 — review notes

Branch: `upgrade/ramanchada2-1.4.0` (from `main` @ `225b393`)
Scope agreed: **compatibility + latent-bug fixes only** — no new 1.4.0 features. Dependency pinned `ramanchada2~=1.4.0`; add-on version `1.0.1 -> 1.1.0`.

## What broke and what changed

1. **Hard break — moved classes.** `ramanchada2/protocols/calibration.py` became a package whose `__init__.py` is empty, so every flat `from ramanchada2.protocols.calibration import ...` raised `ImportError`. Fixed in 5 files to the canonical paths (`...calibration.calibration_model`, `...calibration.ycalibration`):
   - `widgets_easy/xaxis_calibration.py`, `calibration_apply.py`, `calibration_load.py` -> `CalibrationModel`
   - `widgets_easy/yaxis_calibration.py` -> `YCalibrationComponent, YCalibrationCertificate, CertificatesDict`
   - `widgets_pro/srm_certificate.py` -> `YCalibrationCertificate`
2. **Latent bug fixed.** `derive_model()` used `calmodel.neon_wl[laser_wl]` — an attribute that exists in neither 1.2.0 nor 1.4.0 (the widget raised `AttributeError` at runtime before this branch). Now `rc2const.NEON_WL[int(laser_wl)]`, with the `int()` coercion matching the proven `spectrastream` pattern (the GUI spin box yields a float).
3. **Deprecated API kept.** `derive_model_curve`/`derive_model_zero` emit `DeprecationWarning` ("use derive_model_x") but still work in 1.4.0; `derive_model_x` cannot express the widget's per-stage `should_fit`/`profile`, so the two-step flow is kept — now with explicit `match_method="qargmin2d"`, `interpolator_method="poly"` (the new defaults, pinned intentionally).
4. **available_models.** The hardcoded combo list was replaced with the library list from `ramanchada2.spectrum.peaks.fit_peaks` (gained *Skewed Gaussian*, *Skewed Voigt*); `si_peak_profile` is now `Setting('Pearson4')` by name because index 5 of the imported list is no longer Pearson4. Verified in 1.4.0: `derive_model_zero(profile=...)` default is already `Pearson4`.
5. **Behavior changes accepted** (part of the upgrade, not reverted): X-calibration defaults `qargmin2d` + `poly` may shift numerical results slightly; Y-calibration default `model_method="certificate"` replaces raw pchip interpolation; `Spectrum.x/.y` are read-only frozen arrays (verified: repo never mutates rc2 arrays in place); `Spectrum.__init__` no longer auto-sorts (all construction sites pass sorted arrays); text-file loading drops NaN rows; `config_certs.json` reworked (the Y widget populates its combos dynamically from `CertificatesDict`, so this self-heals). New transitive dep: `spe2py~=2.0`.

## Cross-check vs spectrastream (proven app, locked to ramanchada2 1.4.0)

Agrees: import paths, two-step curve+zero flow, `qargmin2d`/`poly`, `Pearson4` Si profile, `CertificatesDict` usage. Adopted from it: `int(laser_wl)` coercion.
Deliberately **not** adopted (outside agreed scope — follow-up candidates):
- spectrastream calls the **private** `_derive_model_curve`/`_derive_model_zero` to avoid `DeprecationWarning` under pytest `filterwarnings=error`; not needed here.
- `spe.y_noise` -> `spe.y_noise_MAD()` (both exist in 1.4.0; verified `y_noise` is still a property).
- Cropping Si to ~±100 cm-1 + `dropna()` before zeroing (spectrastream treats this as the difference between a working fit and a hang).
- Running `apply_calibration_x` on the SRM **before** constructing `YCalibrationComponent` (the certificate is a function of calibrated Raman shift); the widget has no x-cal input — documented assumption.
- Consider setting `calmodel.nonmonotonic = "drop"` and passing `extrapolate=` explicitly.
- A future migration to the single-shot `derive_model_x` remains blocked on per-stage `should_fit`/`profile`.

## Verification (scratch venv, oranchada 1.1.0 editable, ramanchada2 1.4.0 + spe2py 2.0.0, QT_QPA_PLATFORM=offscreen)

- **Install:** `pip install -e .` resolves ramanchada2 1.4.0.
- **Import walk:** all 49 non-test modules import clean; the five previously-broken calibration modules explicitly verified.
- **Functional (7/7 PASS):**
  - `XAxisCalibrationWidget.derive_model()` (int + float laser wl) derives a model with components; `.calmodel` pickle round-trip preserves components — exercises the `neon_wl` fix.
  - `CertificatesDict.get_laser_wl/get_certificates/get(785, ...)`.
  - `YCalibrationCertificate(params="<string>", equation="<string>")` constructs and `cert.Y()` finite (fields confirmed `str`-typed in 1.4.0 — the string construction in `srm_certificate.py` is correct).
  - `YCalibrationComponent(785, reference_spe_xcalibrated=..., certificate=...).process()` returns a Spectrum.
  - `xcal_fine` + `xcal_fine_RBF` with `rc2const.neon_rs_785_nist_dict` (mirrors `widgets_pro/xaxis_fine_calibration.py`).
  - `from_local_file` incl. NaN-row drop; `find_peak_multipeak` (hht-chain and prominence styles).
- **API shapes verified against installed 1.4.0:** `derive_model_curve` accepts `match_method`/`interpolator_method` (defaults `qargmin2d`/`poly`); `available_models` includes `Pearson4`; `YCalibrationComponent` signature matches the widget call.
- **Not possible:** GUI spot-check in `orange-canvas` (headless verification only; offscreen imports pass, but drag-and-drop workflows were not exercised — recommend a manual pass of the X/Y calibration, Load/Apply model, Find/Fit peaks widgets before release).
- **Known-stale tests:** `src/orangecontrib/oranchada/tests/process_spectra_test.py` fails collection on its own legacy `from widgets_pro...` import (pre-existing, per AGENTS.md the tests are stale/not discoverable; not fixed on this branch).

## Commits

1. `Upgrade to ramanchada2 1.4.0: fix moved calibration imports + pin dependency`
2. `Fix latent neon_wl bug and pin x-calibration methods in X-axis calibration widget`
3. (this file)
