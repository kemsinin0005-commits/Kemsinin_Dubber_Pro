Add-Type -AssemblyName System.Drawing

$srcPath = "C:\Users\kemsi\.gemini\antigravity\brain\d24e91c9-2174-4814-bd96-1193d6e8dc36\.user_uploaded\media_1786610616355.jpg"
$baseResPath = "c:\Users\kemsi\Desktop\KEMSININ_DUBBER_PRO\android\app\src\main\res"

$sizes = @{
    "mipmap-mdpi"    = 48
    "mipmap-hdpi"    = 72
    "mipmap-xhdpi"   = 96
    "mipmap-xxhdpi"  = 144
    "mipmap-xxxhdpi" = 192
}

$srcImage = [System.Drawing.Bitmap]::FromFile($srcPath)

foreach ($folder in $sizes.Keys) {
    $dim = $sizes[$folder]
    $dirPath = Join-Path $baseResPath $folder
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
    }

    $destBmp = New-Object System.Drawing.Bitmap($dim, $dim)
    $g = [System.Drawing.Graphics]::FromImage($destBmp)
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $g.DrawImage($srcImage, 0, 0, $dim, $dim)
    $g.Dispose()

    $iconPath = Join-Path $dirPath "ic_launcher.png"
    $roundIconPath = Join-Path $dirPath "ic_launcher_round.png"

    $destBmp.Save($iconPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $destBmp.Save($roundIconPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $destBmp.Dispose()

    Write-Host "Created $iconPath ($dim x $dim)"
}

$srcImage.Dispose()
