# Regenerates img/thumbs/* for the home page. Trims white strips baked into the edges of the source photos, then resizes.
param($ImgDir)
Add-Type -AssemblyName System.Drawing
$out = Join-Path $ImgDir 'thumbs'
New-Item -ItemType Directory -Force $out | Out-Null
$enc = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$ep = New-Object System.Drawing.Imaging.EncoderParameters 1
$ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), ([long]90)
$trimList = 'tb_enclosure_fab.jpg','hvc_prototype.jpg','hvi_v1_flyback.jpg','pdb_assembled.jpg','fuse_ansys_contour.jpg','pocketsens_pcb_photo.jpg','lightcore_assembled.jpg','viewfinder_photo.jpg'
$names = $trimList + 'Segment_MB_3drender.png'   # thermal thumbnail is made separately with pad-plot-thumb.ps1
function IsWhiteLine($bm, $vertical, $i) {
  $len = if ($vertical) { $bm.Height } else { $bm.Width }
  $sum = 0; $cnt = 0; $bright = 0
  for ($k = 0; $k -lt $len; $k += 2) {
    $c = if ($vertical) { $bm.GetPixel($i, $k) } else { $bm.GetPixel($k, $i) }
    $v = ($c.R + $c.G + $c.B) / 3; $sum += $v; $cnt++
    if ($c.R -ge 228 -and $c.G -ge 228 -and $c.B -ge 228) { $bright++ }
  }
  return (($sum / $cnt) -ge 238 -and ($bright / $cnt) -ge 0.93)
}
foreach ($n in $names) {
  $src = New-Object System.Drawing.Bitmap (Join-Path $ImgDir $n)
  $sw = $src.Width; $sh = $src.Height
  $l = 0; $r = 0; $t = 0; $bt = 0
  if ($trimList -contains $n) {
    $capX = [int]($sw * 0.15); $capY = [int]($sh * 0.15)
    while ($l -lt $capX -and (IsWhiteLine $src $true $l)) { $l++ }
    while ($r -lt $capX -and (IsWhiteLine $src $true ($sw - 1 - $r))) { $r++ }
    while ($t -lt $capY -and (IsWhiteLine $src $false $t)) { $t++ }
    while ($bt -lt $capY -and (IsWhiteLine $src $false ($sh - 1 - $bt))) { $bt++ }
    # the line after a white strip is a blend of white and photo: drop 2 more
    if ($l) { $l += 2 }; if ($r) { $r += 2 }; if ($t) { $t += 2 }; if ($bt) { $bt += 2 }
  }
  $cw = $sw - $l - $r; $ch = $sh - $t - $bt
  $widths = @(400, 800 | Where-Object { $_ -le $cw })
  if ($cw -lt 800 -and $cw -ne 400) { $widths += $cw }
  $made = @()
  foreach ($w in $widths) {
    $h = [int][math]::Round($ch * $w / $cw)
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.Clear([System.Drawing.Color]::White)
    $g.InterpolationMode = 'HighQualityBicubic'; $g.PixelOffsetMode = 'HighQuality'; $g.CompositingQuality = 'HighQuality'
    $attr = New-Object System.Drawing.Imaging.ImageAttributes
    $attr.SetWrapMode('TileFlipXY')
    $g.DrawImage($src, (New-Object System.Drawing.Rectangle 0,0,$w,$h), $l, $t, $cw, $ch, 'Pixel', $attr)
    $dst = Join-Path $out (([IO.Path]::GetFileNameWithoutExtension($n)) + "-$w.jpg")
    $bmp.Save($dst, $enc, $ep); $g.Dispose(); $bmp.Dispose(); $attr.Dispose()
    $made += $w
  }
  "{0}: trimmed L{1} R{2} T{3} B{4} -> widths {5}" -f $n, $l, $r, $t, $bt, ($made -join ',')
  $src.Dispose()
}
