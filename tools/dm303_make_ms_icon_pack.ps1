param(
    [string]$TemplateDat = "backup/DM303 V4.0-read only/system/icon-SP.dat",
    [string]$OutputDat = "firmware-candidates/v4.0.1-beta/system/icon-SP.dat",
    [string]$LocalizationDat = "localization/ms_MY/icon-SP.dat"
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$labels = @(
    "VOLTAN",
    "ARUS",
    "CRANKING",
    "FREKUENSI",
    "TETAPAN",
    "BANTUAN",
    "OSILOSKOP",
    "INJEKTOR",
    "RELAY",
    "KAPASITANS",
    "NYALAAN",
    "RINTANGAN",
    "ISY. KELUAR",
    "DATA K/LIN",
    "DATA CAN",
    "TENTANG",
    "LITAR AUTO"
)

function Read-U16Le([byte[]]$Data, [int]$Offset) {
    return [BitConverter]::ToUInt16($Data, $Offset)
}

function Write-U16Le([byte[]]$Data, [int]$Offset, [int]$Value) {
    $Data[$Offset] = [byte]($Value -band 0xff)
    $Data[$Offset + 1] = [byte](($Value -shr 8) -band 0xff)
}

function Rgb565-ToColor([int]$Value) {
    $red = (($Value -shr 11) -band 0x1f) * 255 / 31
    $green = (($Value -shr 5) -band 0x3f) * 255 / 63
    $blue = ($Value -band 0x1f) * 255 / 31
    return [System.Drawing.Color]::FromArgb([int][Math]::Round($red), [int][Math]::Round($green), [int][Math]::Round($blue))
}

function Color-ToRgb565([System.Drawing.Color]$Color) {
    $red = [Math]::Min(31, [Math]::Max(0, [Math]::Round($Color.R * 31 / 255)))
    $green = [Math]::Min(63, [Math]::Max(0, [Math]::Round($Color.G * 63 / 255)))
    $blue = [Math]::Min(31, [Math]::Max(0, [Math]::Round($Color.B * 31 / 255)))
    return (($red -shl 11) -bor ($green -shl 5) -bor $blue)
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}

function New-FittingFont([System.Drawing.Graphics]$Graphics, [string]$Text) {
    $family = New-Object System.Drawing.FontFamily("Arial")
    foreach ($size in @(9.0, 8.5, 8.0, 7.5, 7.0, 6.5, 6.0)) {
        $font = [System.Drawing.Font]::new($family, $size, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Point)
        $measure = $Graphics.MeasureString($Text, $font)
        if ($measure.Width -le 88 -and $measure.Height -le 20) {
            $family.Dispose()
            return $font
        }
        $font.Dispose()
    }
    $fallback = [System.Drawing.Font]::new($family, 6.0, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Point)
    $family.Dispose()
    return $fallback
}

$templatePath = Resolve-Path -LiteralPath $TemplateDat
[byte[]]$dat = [IO.File]::ReadAllBytes($templatePath)
$frameCount = $labels.Count
$frameStride = 4608
$bmpSize = 4488
if ($dat.Length -ne ($frameCount * $frameStride)) {
    throw "Unexpected template icon-SP.dat length: $($dat.Length)"
}

for ($frame = 0; $frame -lt $frameCount; $frame++) {
    $frameStart = $frame * $frameStride
    if ($dat[$frameStart] -ne 0x42 -or $dat[$frameStart + 1] -ne 0x4d) {
        throw "Frame $frame does not start with BMP signature"
    }
    $declaredSize = [BitConverter]::ToUInt32($dat, $frameStart + 2)
    $pixelOffset = [BitConverter]::ToUInt32($dat, $frameStart + 10)
    $dibSize = [BitConverter]::ToUInt32($dat, $frameStart + 14)
    $width = [BitConverter]::ToInt32($dat, $frameStart + 18)
    $height = [BitConverter]::ToInt32($dat, $frameStart + 22)
    $bpp = [BitConverter]::ToUInt16($dat, $frameStart + 28)
    $compression = [BitConverter]::ToUInt32($dat, $frameStart + 30)
    $absHeight = [Math]::Abs($height)
    if ($declaredSize -ne $bmpSize -or $dibSize -ne 56 -or $width -ne 92 -or $absHeight -ne 24 -or $bpp -ne 16 -or $compression -ne 3) {
        throw "Unexpected frame layout at index $frame"
    }

    $rowSize = [Math]::Floor((($width * 16 + 31) / 32)) * 4
    $background = Rgb565-ToColor (Read-U16Le $dat ($frameStart + $pixelOffset))
    $foreground = [System.Drawing.Color]::FromArgb(238, 243, 238)

    $canvas = [System.Drawing.Bitmap]::new($width, $absHeight, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $graphics = [System.Drawing.Graphics]::FromImage($canvas)
    $graphics.Clear($background)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::None
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
    $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::SingleBitPerPixelGridFit

    $text = $labels[$frame]
    $font = New-FittingFont $graphics $text
    $brush = [System.Drawing.SolidBrush]::new($foreground)
    $size = $graphics.MeasureString($text, $font)
    $textX = [Math]::Max(0, [Math]::Round(($width - $size.Width) / 2))
    $textY = [Math]::Max(0, [Math]::Round(($absHeight - $size.Height) / 2) - 1)
    $graphics.DrawString($text, $font, $brush, $textX, $textY)

    $brush.Dispose()
    $font.Dispose()
    $graphics.Dispose()

    for ($y = 0; $y -lt $absHeight; $y++) {
        $sourceY = if ($height -lt 0) { $y } else { $absHeight - 1 - $y }
        for ($x = 0; $x -lt $width; $x++) {
            $offset = $frameStart + $pixelOffset + $sourceY * $rowSize + $x * 2
            Write-U16Le $dat $offset (Color-ToRgb565 ($canvas.GetPixel($x, $y)))
        }
    }
    $canvas.Dispose()
}

$outputPath = Join-Path (Get-Location) $OutputDat
$localizationPath = Join-Path (Get-Location) $LocalizationDat
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $outputPath) | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $localizationPath) | Out-Null
[IO.File]::WriteAllBytes($outputPath, $dat)
[IO.File]::WriteAllBytes($localizationPath, $dat)

$reportPath = Join-Path (Split-Path -Parent $outputPath) "MS-ICON-PACK.md"
$hash = Get-Sha256 $outputPath
$templateHash = Get-Sha256 $templatePath
$report = @(
    "# DM303 Bahasa Melayu icon-SP.dat report",
    "",
    "Status: Malay graphical label pack for the reused SP language slot.",
    "",
    "## Safety scope",
    "",
    "- Template: ``backup/DM303 V4.0-read only/system/icon-SP.dat``.",
    "- Output size is preserved at ``$($dat.Length)`` bytes.",
    "- Frame count is preserved at ``$frameCount`` frames.",
    "- Each frame keeps the official ``92x24`` 16-bit BI_BITFIELDS BMP layout and original padding.",
    "- The pack intentionally does not add an 18th frame because official non-Chinese packs contain 17 frames.",
    "- Firmware code, bootloader, updater, and menu dispatch tables are not touched by this resource tool.",
    "",
    "## Labels",
    ""
)
for ($i = 0; $i -lt $labels.Count; $i++) {
    $report += "- ``$i``: ``$($labels[$i])``"
}
$report += @(
    "",
    "## Output",
    "",
    "- Template SHA-256: ``$templateHash``",
    "- Output SHA-256: ``$hash``"
)
[IO.File]::WriteAllText($reportPath, ($report -join "`n") + "`n", [Text.Encoding]::UTF8)

Write-Output "template=$templatePath"
Write-Output "output=$outputPath"
Write-Output "localization=$localizationPath"
Write-Output "frames=$frameCount"
Write-Output "sha256=$hash"
Write-Output "report=$reportPath"
