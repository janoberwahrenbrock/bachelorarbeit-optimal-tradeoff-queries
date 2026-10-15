# Third-party components

The installed project depends on NumPy, SciPy and jsonschema. Their distributions retain their respective licenses and notices; this repository does not bundle those distributions.

Numerical computation uses the LP and geometry backends provided by SciPy, including HiGHS and Qhull. The guarded continuous-result validator follows SciPy's `_check_result` checks for the supported continuous case, with the original checker retained as the fallback. The applicable SciPy copyright, BSD conditions and disclaimer are retained in [LICENSES/SciPy-BSD-3-Clause.txt](LICENSES/SciPy-BSD-3-Clause.txt) and included in distribution metadata. Third-party dependency distributions retain notices for their own bundled backends.

The project license will be selected before release. This document does not grant a license for the project itself.
