$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$python = Join-Path $root "venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Virtual environment Python not found at $python"
}

& $python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name BackgroundRemover `
    --hidden-import rembg_worker `
    gif_background_remover.py

$distRoot = Join-Path $root "dist\BackgroundRemover"
$sitePackages = Join-Path $root "venv\Lib\site-packages"
$rembgSource = Join-Path $sitePackages "rembg"
$rembgDest = Join-Path $distRoot "rembg"
$onnxruntimeSource = Join-Path $sitePackages "onnxruntime"
$onnxruntimeDest = Join-Path $distRoot "onnxruntime"

if (-not (Test-Path $rembgSource)) {
    throw "rembg package not found at $rembgSource"
}

if (-not (Test-Path $onnxruntimeSource)) {
    throw "onnxruntime package not found at $onnxruntimeSource"
}

if (Test-Path $rembgDest) {
    Remove-Item -LiteralPath $rembgDest -Recurse -Force
}

Copy-Item -LiteralPath $rembgSource -Destination $rembgDest -Recurse

if (Test-Path $onnxruntimeDest) {
    Remove-Item -LiteralPath $onnxruntimeDest -Recurse -Force
}

Copy-Item -LiteralPath $onnxruntimeSource -Destination $onnxruntimeDest -Recurse
