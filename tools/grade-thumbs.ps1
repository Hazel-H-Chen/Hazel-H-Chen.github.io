# Exposure-normalises a set of thumbnails: stretches each so its darkest 1% and brightest 1% land on the same targets.
param($InDir, $OutDir, $Names)
Add-Type -AssemblyName System.Drawing
$enc = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$ep = New-Object System.Drawing.Imaging.EncoderParameters 1
$ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), ([long]92)
foreach ($n in $Names.Split(',')) {
  $src = New-Object System.Drawing.Bitmap (Join-Path $InDir $n)
  $hist = New-Object 'int[]' 256; $cnt = 0
  for ($y = 0; $y -lt $src.Height; $y += 3) { for ($x = 0; $x -lt $src.Width; $x += 3) {
    $c = $src.GetPixel($x, $y); $hist[[int](0.299*$c.R + 0.587*$c.G + 0.114*$c.B)]++; $cnt++ } }
  $acc = 0; $lo = 0; $hi = 255
  for ($i = 0; $i -lt 256; $i++) { $acc += $hist[$i]; if ($acc -ge $cnt * 0.01) { $lo = $i; break } }
  $acc = 0
  for ($i = 255; $i -ge 0; $i--) { $acc += $hist[$i]; if ($acc -ge $cnt * 0.01) { $hi = $i; break } }
  $tLo = 14.0; $tHi = 240.0
  $s = ($tHi - $tLo) / [math]::Max(1, $hi - $lo); $s = [math]::Min(1.6, [math]::Max(0.8, $s))
  $o = ($tLo - $lo * $s) / 255.0
  $cm = New-Object System.Drawing.Imaging.ColorMatrix
  $cm.Matrix00 = $s; $cm.Matrix11 = $s; $cm.Matrix22 = $s; $cm.Matrix33 = 1; $cm.Matrix44 = 1
  $cm.Matrix40 = $o; $cm.Matrix41 = $o; $cm.Matrix42 = $o
  $attr = New-Object System.Drawing.Imaging.ImageAttributes; $attr.SetColorMatrix($cm)
  $bmp = New-Object System.Drawing.Bitmap $src.Width, $src.Height
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.DrawImage($src, (New-Object System.Drawing.Rectangle 0,0,$src.Width,$src.Height), 0,0,$src.Width,$src.Height, 'Pixel', $attr)
  $bmp.Save((Join-Path $OutDir $n), $enc, $ep); $g.Dispose(); $bmp.Dispose(); $src.Dispose()
  "{0}: lo {1} hi {2} -> gain {3:N2}" -f $n, $lo, $hi, $s
}
