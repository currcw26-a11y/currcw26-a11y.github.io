# Resizes + compresses drone photos for the website, and strips all hidden metadata
# (GPS location, camera info, etc.) in the process. Originals are never touched.
Add-Type -AssemblyName System.Drawing

$root = Split-Path -Parent $PSScriptRoot
$locationsDir = Join-Path $root "photos\locations"
$webFullDir   = Join-Path $root "photos\web\full"
$webThumbDir  = Join-Path $root "photos\web\thumb"

function Get-Slug([string]$name) {
    $slug = $name.ToLower()
    $slug = $slug -replace "[^a-z0-9]+", "-"
    $slug = $slug.Trim("-")
    return $slug
}

function Save-Resized([System.Drawing.Image]$img, [int]$maxDim, [int]$quality, [string]$outPath) {
    $w = $img.Width
    $h = $img.Height
    $ratio = [Math]::Min([double]$maxDim / $w, [double]$maxDim / $h)
    if ($ratio -lt 1.0) {
        $newW = [int]($w * $ratio)
        $newH = [int]($h * $ratio)
    } else {
        $newW = $w
        $newH = $h
    }
    $bmp = New-Object System.Drawing.Bitmap $newW, $newH
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $g.DrawImage($img, 0, 0, $newW, $newH)
    $g.Dispose()

    $jpegCodec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/jpeg" }
    $encParams = New-Object System.Drawing.Imaging.EncoderParameters 1
    $encParams.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality, [int64]$quality)
    # New bitmap has no copied EXIF/GPS properties -- metadata is stripped by construction.
    $bmp.Save($outPath, $jpegCodec, $encParams)
    $bmp.Dispose()
}

New-Item -ItemType Directory -Force -Path $webFullDir | Out-Null
New-Item -ItemType Directory -Force -Path $webThumbDir | Out-Null

$slugMap = @{}
$locations = Get-ChildItem -Path $locationsDir -Directory
$total = 0
foreach ($locDir in $locations) {
    $slug = Get-Slug $locDir.Name
    $slugMap[$locDir.Name] = $slug
    $fullOut = Join-Path $webFullDir $slug
    $thumbOut = Join-Path $webThumbDir $slug
    New-Item -ItemType Directory -Force -Path $fullOut | Out-Null
    New-Item -ItemType Directory -Force -Path $thumbOut | Out-Null

    $photos = Get-ChildItem -Path $locDir.FullName -File | Where-Object { $_.Extension -match '\.(jpg|jpeg|png)$' }
    foreach ($photo in $photos) {
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($photo.Name) + ".jpg"
        $img = [System.Drawing.Image]::FromFile($photo.FullName)
        try {
            Save-Resized $img 2000 82 (Join-Path $fullOut $baseName)
            Save-Resized $img 700 75 (Join-Path $thumbOut $baseName)
        } finally {
            $img.Dispose()
        }
        $total++
    }
    Write-Host ("{0,-30} {1,3} photos -> {2}" -f $locDir.Name, $photos.Count, $slug)
}

$slugMap | ConvertTo-Json | Out-File -Encoding utf8 (Join-Path $root "scripts\slug-map.json")
Write-Host ""
Write-Host "Total processed: $total photos (resized + metadata stripped)"
