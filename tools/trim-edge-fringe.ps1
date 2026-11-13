# Second pass: removes a 1-3 px light fringe left on an edge (a line much brighter than the picture just inside it).
param($ImgDir, $ListFile, [switch]$Apply)
Add-Type -AssemblyName System.Drawing
$jpg = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$ep = New-Object System.Drawing.Imaging.EncoderParameters 1
$ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), ([long]95)
function Mean($bm, $vertical, $i) {
  $len = if ($vertical) { $bm.Height } else { $bm.Width }
  $stepk = [math]::Max(1, [int]($len / 500)); $sum = 0; $cnt = 0
  for ($k = 0; $k -lt $len; $k += $stepk) {
    $c = if ($vertical) { $bm.GetPixel($i, $k) } else { $bm.GetPixel($k, $i) }
    $sum += ($c.R + $c.G + $c.B) / 3; $cnt++
  }
  return ($sum / $cnt)
}
function Fringe($bm, $vertical, $fromEnd) {
  $dim = if ($vertical) { $bm.Width } else { $bm.Height }
  $n = 0
  while ($n -lt 3) {
    $a = if ($fromEnd) { $dim - 1 - $n } else { $n }
    $b = if ($fromEnd) { $dim - 1 - ($n + 3) } else { $n + 3 }
    $ma = Mean $bm $vertical $a; $mb = Mean $bm $vertical $b
    if ($ma -ge 185 -and ($ma - $mb) -ge 45) { $n++ } else { break }
  }
  return $n
}
foreach ($f in (Get-Content $ListFile)) {
  $path = Join-Path $ImgDir $f
  if (-not (Test-Path $path)) { continue }
  $bytes = [IO.File]::ReadAllBytes($path); $ms = New-Object IO.MemoryStream (,$bytes)
  $src = New-Object System.Drawing.Bitmap $ms
  $l = Fringe $src $true $false; $r = Fringe $src $true $true; $t = Fringe $src $false $false; $b2 = Fringe $src $false $true
  if ($l + $r + $t + $b2 -eq 0) { $src.Dispose(); $ms.Dispose(); continue }
  "{0}: L{1} R{2} T{3} B{4}" -f $f, $l, $r, $t, $b2
  if ($Apply) {
    $out = $src.Clone((New-Object System.Drawing.Rectangle $l, $t, ($src.Width - $l - $r), ($src.Height - $t - $b2)), $src.PixelFormat)
    $src.Dispose(); $ms.Dispose()
    if ($f -match '\.png$') { $out.Save($path, [System.Drawing.Imaging.ImageFormat]::Png) } else { $out.Save($path, $jpg, $ep) }
    $out.Dispose()
  } else { $src.Dispose(); $ms.Dispose() }
}
