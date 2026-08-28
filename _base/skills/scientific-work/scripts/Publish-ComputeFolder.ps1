<#
.SYNOPSIS
    Copy a local computation folder into the synced vault: sources, result tables, figures, and
    stripped model files. Leaves behind the debris and the regenerable bulk.

.DESCRIPTION
    Simulation work accumulates in a local scratch folder and stays there until it is forgotten.
    This publishes it to Google Drive so it survives the machine, in the shape that is actually
    worth keeping:

      kept     - .java .py .m .c .h .md  (the model IS the script)
                 .csv .json .txt         (result tables and run summaries)
                 .png .svg .pdf          (figures)
                 .mph                    (stripped through Compress-MphModel.ps1)
      dropped  - .class .status .recovery *_Model.mph  (batch debris)
                 .log                    (unless -KeepLogs)
                 dense field exports matching -ExcludeBulk, which a re-run reproduces

    A MANIFEST.md is written into the destination listing what was published, with sizes and the
    source path, so the vault copy says where it came from and how to re-run it.

.PARAMETER Source
    The local computation folder.

.PARAMETER Dest
    Destination inside the vault.

.PARAMETER ExcludeBulk
    Wildcards for large regenerable exports. Default drops `field_*_field.csv`, the dense E/H
    grids this vault's mode-analysis scripts write.

.PARAMETER MaxCsvMB
    Any .csv above this size is treated as a dense field export rather than a result table and is
    left behind. A name pattern is not enough - the same dumps arrive under new names every time
    a script is written - but size is a reliable tell: a table someone reads is kilobytes, a
    sampled field is megabytes. Default 1 MB; raise it when a genuinely large table matters.

.PARAMETER ExcludeDir
    Directory name wildcards to skip entirely. Defaults cover folders already marked invalid and
    interpreter caches.

.PARAMETER KeepLogs
    Publish .log files too. Worth it only for a run that failed and needs to be explained.

.PARAMETER Apply
    Actually copy. Without it the script only reports.

.EXAMPLE
    .\Publish-ComputeFolder.ps1 -Source C:\workspace\COMSOL\queue_2026\J_junction `
        -Dest "C:\Users\User\Мой диск\Obsidian\PhD\...\CODEX\mph_2026-08\J_junction" -Apply
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Source,
    [Parameter(Mandatory = $true)][string]$Dest,
    [string[]]$ExcludeBulk = @('field_*_field.csv'),
    [double]$MaxCsvMB = 1.0,
    [string[]]$ExcludeDir = @('_invalid*', '__pycache__', '.ipynb_checkpoints'),
    [switch]$KeepLogs,
    [switch]$Apply
)

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not (Test-Path $Source)) { throw "source not found: $Source" }

$keepExt = @('.java', '.py', '.m', '.c', '.h', '.md', '.csv', '.json', '.txt',
             '.png', '.svg', '.pdf')
if ($KeepLogs) { $keepExt += '.log' }
$dropName = @('*.class', '*.status', '*.recovery', '*_Model.mph')

$all = Get-ChildItem -LiteralPath $Source -File -Recurse
$take = @()
$skip = @()
foreach ($f in $all) {
    $rel = $f.FullName.Substring($Source.TrimEnd('\').Length + 1)
    $isDrop = $false
    foreach ($p in $dropName) { if ($f.Name -like $p) { $isDrop = $true } }
    foreach ($p in $ExcludeBulk) { if ($f.Name -like $p) { $isDrop = $true } }
    foreach ($p in $ExcludeDir) {
        if ($rel -like "*$p\*" -or $rel -like "$p\*") { $isDrop = $true }
    }
    if ($f.Extension -ieq '.csv' -and $f.Length -gt $MaxCsvMB * 1MB) { $isDrop = $true }
    if ($f.Extension -ieq '.mph') { continue }        # handled by the stripper below
    if ($isDrop -or ($keepExt -notcontains $f.Extension.ToLower())) {
        $skip += $f
    } else {
        $take += [pscustomobject]@{ File = $f; Rel = $rel }
    }
}

# Windows PowerShell 5.1 rejects a script block for -Property, so sum by hand
$takeBytes = 0L
foreach ($t in $take) { $takeBytes += $t.File.Length }
$skipBytes = 0L
foreach ($s in $skip) { $skipBytes += $s.Length }
$takeMB = $takeBytes / 1MB
$skipMB = $skipBytes / 1MB
Write-Output ("publish {0} files, {1:N1} MB   skip {2} files, {3:N1} MB" -f `
    $take.Count, $takeMB, $skip.Count, $skipMB)

if (-not $Apply) {
    $take | Select-Object -First 40 | ForEach-Object { Write-Output ("  + " + $_.Rel) }
    if ($take.Count -gt 40) { Write-Output ("  ... and {0} more" -f ($take.Count - 40)) }
    return
}

if (-not (Test-Path $Dest)) { New-Item -ItemType Directory -Force $Dest | Out-Null }
foreach ($t in $take) {
    $target = Join-Path $Dest $t.Rel
    $dir = Split-Path -Parent $target
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
    Copy-Item -LiteralPath $t.File.FullName -Destination $target -Force
}

# models go through the stripper. A sibling <name>_stripped.mph that is newer than its source
# is reused under the original name instead of being produced again - stripping a large model
# is minutes of work and there is no reason to repeat it.
$models = Get-ChildItem -LiteralPath $Source -Filter *.mph -File -Recurse |
    Where-Object { $_.Name -notlike '*_stripped.mph' }
foreach ($m in $models) {
    $sib = Join-Path $m.DirectoryName ($m.BaseName + '_stripped.mph')
    $target = Join-Path $Dest $m.Name
    if ((Test-Path $sib) -and (Get-Item $sib).LastWriteTime -ge $m.LastWriteTime) {
        Copy-Item -LiteralPath $sib -Destination $target -Force
        Write-Output ("reused stripped  {0,7:N1} MB  {1}" -f ((Get-Item $sib).Length / 1MB), $m.Name)
    } else {
        & (Join-Path $here 'Compress-MphModel.ps1') -Path $m.FullName -OutDir $Dest -MinMB 0 -Apply
    }
}

$published = Get-ChildItem -LiteralPath $Dest -File -Recurse
$lines = @()
$lines += "Опубликовано из ``$Source`` — " + (Get-Date -Format 'yyyy-MM-dd')
$lines += ''
$lines += 'Модели `.mph` очищены от решений, сетки, таблиц и истории правок: геометрия, материалы, физика и все настройки сохранены, файл открывается и пересчитывается на другом ПК.'
$lines += ''
$lines += '| Файл | Размер, КБ |'
$lines += '| --- | --- |'
foreach ($f in ($published | Where-Object { $_.Name -ne 'MANIFEST.md' } | Sort-Object Name)) {
    $lines += ('| {0} | {1:N0} |' -f $f.Name, ($f.Length / 1KB))
}
$totalBytes = 0L
foreach ($f in $published) { $totalBytes += $f.Length }
$total = $totalBytes / 1MB
$lines += ''
$lines += ('Всего {0} файлов, {1:N1} МБ.' -f $published.Count, $total)
Set-Content -LiteralPath (Join-Path $Dest 'MANIFEST.md') -Value $lines -Encoding utf8

Write-Output ("published to {0}: {1} files, {2:N1} MB" -f $Dest, $published.Count, $total)
