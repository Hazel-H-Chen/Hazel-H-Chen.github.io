# Makes 4:3 thumbnails of a plot by centring it on a white canvas with a small margin (nothing is cropped).
param($Src, $OutDir, $Stem)
Add-Type -AssemblyName System.Drawing
$enc = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$ep = New-Object System.Drawing.Imaging.EncoderParameters 1
$ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), ([long]92)
$img = New-Object System.Drawing.Bitmap $Src
"source {0}x{1}" -f $img.Width, $img.Height
foreach ($w in 400, 800) {
  $h = [int]($w * 3 / 4); $pad = [int]($w * 0.04)
  $scale = [math]::Min(($w - 2*$pad) / $img.Width, ($h - 2*$pad) / $img.Height)
  $dw = [int]($img.Width * $scale); $dh = [int]($img.Height * $scale)
  $bmp = New-Object System.Drawing.Bitmap $w, $h
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.Clear([System.Drawing.Color]::White)
  $g.InterpolationMode = 'HighQualityBicubic'; $g.PixelOffsetMode = 'HighQuality'
  $attr = New-Object System.Drawing.Imaging.ImageAttributes; $attr.SetWrapMode('TileFlipXY')
  $g.DrawImage($img, (New-Object System.Drawing.Rectangle ([int](($w-$dw)/2)), ([int](($h-$dh)/2)), $dw, $dh), 0, 0, $img.Width, $img.Height, 'Pixel', $attr)
  $dst = Join-Path $OutDir "$Stem-$w.jpg"
  $bmp.Save($dst, $enc, $ep); $g.Dispose(); $bmp.Dispose(); $attr.Dispose()
  "wrote $Stem-$w.jpg"
}
$img.Dispose()
