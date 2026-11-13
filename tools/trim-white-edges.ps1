# Finds (and with -Apply removes) thin white strips baked into the edges of images.
# A side is trimmed only when the strip is thin and is followed by real picture content,
# so plots and renders with genuine white margins are left alone.
param($ImgDir, $ListFile, [switch]$Apply)
Add-Type -AssemblyName System.Drawing
$jpg = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$ep = New-Object System.Drawing.Imaging.EncoderParameters 1
$ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), ([long]95)
function LineStats($bm, $vertical, $i) {
  $len = if ($vertical) { $bm.Height } else { $bm.Width }
  $stepk = [math]::Max(1, [int]($len / 500)); $sum = 0; $cnt = 0; $bright = 0
  for ($k = 0; $k -lt $len; $k += $stepk) {
    $c = if ($vertical) { $bm.GetPixel($i, $k) } else { $bm.GetPixel($k, $i) }
    $sum += ($c.R + $c.G + $c.B) / 3; $cnt++
    if ($c.R -ge 228 -and $c.G -ge 228 -and $c.B -ge 228) { $bright++ }
  }
  return @(($sum / $cnt), ($bright / $cnt))
}
function Strip($bm, $vertical, $fromEnd) {
  $dim = if ($vertical) { $bm.Width } else { $bm.Height }
  $cap = [int]($dim * 0.15); $n = 0
  while ($n -le $cap) {
    $idx = if ($fromEnd) { $dim - 1 - $n } else { $n }
    $s = LineStats $bm $vertical $idx
    if ($s[0] -ge 238 -and $s[1] -ge 0.93) { $n++ } else { break }
  }
  if ($n -eq 0 -or $n -gt $cap) { return 0 }           # none, or a real white margin
  $idx = if ($fromEnd) { $dim - 1 - ($n + 3) } else { $n + 3 }
  $after = LineStats $bm $vertical $idx
  if ($after[1] -gt 0.5) { return 0 }                   # what follows is still mostly white: not a photo edge
  return ($n + 2)                                       # +2 for the blended transition line
}
foreach ($f in (Get-Content $ListFile)) {
  $path = Join-Path $ImgDir $f
  if (-not (Test-Path $path)) { "MISSING $f"; continue }
  $bytes = [IO.File]::ReadAllBytes($path); $ms = New-Object IO.MemoryStream (,$bytes)
  $src = New-Object System.Drawing.Bitmap $ms
  $l = Strip $src $true $false; $r = Strip $src $true $true; $t = Strip $src $false $false; $b2 = Strip $src $false $true
  if ($l + $r + $t + $b2 -eq 0) { $src.Dispose(); $ms.Dispose(); continue }
  "{0} {1}x{2}: L{3} R{4} T{5} B{6}" -f $f, $src.Width, $src.Height, $l, $r, $t, $b2
  if ($Apply) {
    $cw = $src.Width - $l - $r; $ch = $src.Height - $t - $b2
    $out = $src.Clone((New-Object System.Drawing.Rectangle $l, $t, $cw, $ch), $src.PixelFormat)
    $src.Dispose(); $ms.Dispose()
    if ($f -match '\.png$') { $out.Save($path, [System.Drawing.Imaging.ImageFormat]::Png) } else { $out.Save($path, $jpg, $ep) }
    $out.Dispose()
  } else { $src.Dispose(); $ms.Dispose() }
}
