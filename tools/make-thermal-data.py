import csv, sys, json, bisect
src, out = sys.argv[1], sys.argv[2]
def rd(n):
    with open(f'{src}/{n}', newline='') as f:
        r = list(csv.reader(f))[1:]
    return [[float(x) for x in row] for row in r if row]
lap = rd('lapsim_results_end_full_braking.csv')
t = [r[0] for r in lap]; p = [max(r[2], 0.0) for r in lap]   # regen ignored, as in the MATLAB script
dur = t[-1]
DT = 0.02
n = int(dur / DT) + 1
def interp(x):
    if x <= t[0]: return p[0]
    if x >= t[-1]: return p[-1]
    i = bisect.bisect_right(t, x)
    f = (x - t[i-1]) / (t[i] - t[i-1])
    return p[i-1] + f * (p[i] - p[i-1])
power = [round(interp(i * DT), 2) for i in range(n)]
dc = rd('P50B_DCIR.csv'); vv = rd('P50B_voltage_vs_SoC.csv')
assert all(abs(dc[i][0] - (1 + 0.5 * i)) < 1e-9 for i in range(len(dc)))
assert all(abs(vv[i][0] - 0.5 * i) < 1e-9 for i in range(len(vv)))
data = {
  'lapDuration': round(dur, 4), 'powerDt': DT, 'lapPowerKW': power,
  'dcirSocStart': 1, 'dcirSocStep': 0.5, 'dcirMilliOhm': [r[1] for r in dc],
  'vocSocStart': 0, 'vocSocStep': 0.5, 'vocVolts': [r[1] for r in vv],
}
js = ('// Input data for the interactive thermal model (generated from the CSVs used by SingleCellLumped.m).\n'
      '// lapPowerKW: lapsim pack power for one endurance lap, resampled every powerDt seconds, regen clipped to 0.\n'
      '// dcirMilliOhm / vocVolts: Molicel P50B DCIR (23 C) and open-circuit voltage vs. state of charge.\n'
      'window.THERMAL_DATA = ' + json.dumps(data, separators=(',', ':')) + ';\n')
open(out, 'w', newline='\n').write(js)
print(n, 'power samples; lap', dur, 's; mean kW', sum(power)/n, 'max', max(power), '; bytes', len(js))
