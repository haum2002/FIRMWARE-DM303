param(
    [string]$TemplateLogo = "backup/DM303 V4.0-read only/system/LOGO-1.bmp",
    [string]$SourceArtwork = "assets/logo/dm303-v401-beta-logo-source.bmp",
    [string]$DestinationLogo = "firmware-candidates/v4.0.1-beta/system/LOGO-1.bmp"
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

function Read-U16Le([byte[]]$Data, [int]$Offset) {
    return [BitConverter]::ToUInt16($Data, $Offset)
}

function Write-U16Le([byte[]]$Data, [int]$Offset, [int]$Value) {
    $Data[$Offset] = [byte]($Value -band 0xff)
    $Data[$Offset + 1] = [byte](($Value -shr 8) -band 0xff)
}

function To-Rgb565([System.Drawing.Color]$Color) {
    $red = [Math]::Min(31, [Math]::Max(0, [Math]::Round($Color.R * 31 / 255)))
    $green = [Math]::Min(63, [Math]::Max(0, [Math]::Round($Color.G * 63 / 255)))
    $blue = [Math]::Min(31, [Math]::Max(0, [Math]::Round($Color.B * 31 / 255)))
    return (($red -shl 11) -bor ($green -shl 5) -bor $blue)
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}

$templatePath = Resolve-Path -LiteralPath $TemplateLogo
$artworkPath = if (Test-Path -LiteralPath $SourceArtwork) { Resolve-Path -LiteralPath $SourceArtwork } else { $null }
$destinationPath = Join-Path (Get-Location) $DestinationLogo
$destinationDir = Split-Path -Parent $destinationPath
New-Item -ItemType Directory -Force -Path $destinationDir | Out-Null

[byte[]]$data = [IO.File]::ReadAllBytes($templatePath)
if ($data[0] -ne 0x42 -or $data[1] -ne 0x4d) {
    throw "Template is not a BMP file: $templatePath"
}

$pixelOffset = [BitConverter]::ToUInt32($data, 10)
$dibSize = [BitConverter]::ToUInt32($data, 14)
$width = [BitConverter]::ToInt32($data, 18)
$height = [BitConverter]::ToInt32($data, 22)
$bpp = [BitConverter]::ToUInt16($data, 28)
$compression = [BitConverter]::ToUInt32($data, 30)
$absHeight = [Math]::Abs($height)
if ($dibSize -ne 56 -or $width -ne 320 -or $absHeight -ne 240 -or $bpp -ne 16 -or $compression -ne 3) {
    throw "Unexpected LOGO-1.bmp template layout: width=$width height=$height bpp=$bpp compression=$compression dib=$dibSize"
}

$canvas = New-Object System.Drawing.Bitmap($width, $absHeight, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$graphics = [System.Drawing.Graphics]::FromImage($canvas)
$graphics.Clear([System.Drawing.Color]::Black)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::None
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::SingleBitPerPixelGridFit

$baseImage = $null
$artworkImage = $null
if ($artworkPath) {
    $artworkImage = [System.Drawing.Image]::FromFile($artworkPath)
    if ($artworkImage.Width -ne $width -or $artworkImage.Height -ne $absHeight) {
        throw "Source artwork must be 320x240 pixels: $artworkPath"
    }
    $graphics.DrawImage($artworkImage, 0, 0, $width, $absHeight)
}
else {
    $baseImage = [System.Drawing.Image]::FromFile($templatePath)
    $graphics.DrawImage($baseImage, 0, 0, $width, $absHeight)

    $blackBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Black)
    $graphics.FillRectangle($blackBrush, 0, 168, $width, 48)

    $fontCollection = New-Object System.Drawing.Text.PrivateFontCollection
    $fontPath = Join-Path (Get-Location) "assets/fonts/AbrilFatface-Regular.ttf"
    if (Test-Path -LiteralPath $fontPath) {
        $fontCollection.AddFontFile((Resolve-Path -LiteralPath $fontPath))
        $fontFamily = $fontCollection.Families[0]
    }
    else {
        $fontFamily = New-Object System.Drawing.FontFamily("Georgia")
    }
    $fontStyle = [System.Drawing.FontStyle]::Underline
    $font = [System.Drawing.Font]::new($fontFamily, 11.0, $fontStyle, [System.Drawing.GraphicsUnit]::Point)
    $textBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(230, 235, 220))
    $text = "BETA VERSION"
    $textSize = $graphics.MeasureString($text, $font)
    $textX = [Math]::Round(($width - $textSize.Width) / 2)
    $textY = 181
    $graphics.DrawString($text, $font, $textBrush, $textX, $textY)

    $textBrush.Dispose()
    $font.Dispose()
    $fontCollection.Dispose()
    $blackBrush.Dispose()
}
$graphics.Dispose()
if ($baseImage) {
    $baseImage.Dispose()
}
if ($artworkImage) {
    $artworkImage.Dispose()
}

$rowSize = [Math]::Floor((($width * 16 + 31) / 32)) * 4
$changedPixels = 0
for ($yPix = 0; $yPix -lt $absHeight; $yPix++) {
    $sourceY = if ($height -lt 0) { $yPix } else { $absHeight - 1 - $yPix }
    for ($xPix = 0; $xPix -lt $width; $xPix++) {
        $offset = $pixelOffset + $sourceY * $rowSize + $xPix * 2
        $before = Read-U16Le $data $offset
        $rgb565 = To-Rgb565($canvas.GetPixel($xPix, $yPix))
        if ($before -ne $rgb565) {
            Write-U16Le $data $offset $rgb565
            $changedPixels++
        }
    }
}
$canvas.Dispose()

[IO.File]::WriteAllBytes($destinationPath, $data)
$outputSha = Get-Sha256 $destinationPath
$sourceSha = if ($artworkPath) { Get-Sha256 $artworkPath } else { "not-present" }
$reportPath = Join-Path $destinationDir "BETA-LOGO-REPORT.md"
$report = @(
    "# DM303 V4.0.1 beta logo report",
    "",
    "Status: resource-level LOGO-1.bmp overlay for ``v4.0.1 beta``.",
    "",
    "## Safety scope",
    "",
    "- Source artwork archive is ``assets/logo/dm303-v401-beta-logo-source.bmp``.",
    "- Firmware BMP template is ``backup/DM303 V4.0-read only/system/LOGO-1.bmp``.",
    "- If source artwork exists, it is converted directly into the official 16-bit LOGO-1.bmp layout.",
    "- If source artwork is absent, the clean vendor logo pixels are kept from the original template and the website text is replaced with ``BETA VERSION``.",
    "- BMP header, dimensions, bit depth, compression mode, row layout, and file size are preserved.",
    "- Firmware code, bootloader, and updater are not touched by this tool.",
    "",
    "## Output",
    "",
    "- File: ``system/LOGO-1.bmp``",
    "- Source artwork SHA-256: ``$sourceSha``",
    "- Changed pixels vs template: ``$changedPixels``",
    "- Output SHA-256: ``$outputSha``"
)
[IO.File]::WriteAllText($reportPath, ($report -join "`n") + "`n", [Text.Encoding]::UTF8)

Write-Output "template=$templatePath"
Write-Output "source_artwork=$artworkPath"
Write-Output "output=$destinationPath"
Write-Output "source_artwork_sha256=$sourceSha"
Write-Output "changed_pixels=$changedPixels"
Write-Output "output_sha256=$outputSha"
Write-Output "report=$reportPath"
