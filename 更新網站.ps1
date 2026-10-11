param([switch]$Preview)
$ErrorActionPreference = 'Stop'
$bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (-not (Test-Path -LiteralPath $bundledPython)) { throw '找不到附帶 Python。請在 Codex 中執行更新，或使用 Python 3.10 以上及 OpenCC 執行 tools/library.py build。' }
Push-Location $PSScriptRoot
try {
    & $bundledPython -X utf8 tools/library.py build
    if ($LASTEXITCODE -ne 0) { throw '建置失敗，請檢查文章檔。' }
    if ($Preview) {
        Write-Host '在瀏覽器開啟 http://127.0.0.1:8765；按 Ctrl+C 停止預覽。'
        & $bundledPython -m http.server 8765 --bind 127.0.0.1 --directory dist
    }
} finally { Pop-Location }
