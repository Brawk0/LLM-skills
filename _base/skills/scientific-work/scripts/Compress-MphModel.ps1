<#
.SYNOPSIS
    Strip COMSOL .mph models of solution data, mesh data, tables and edit history so they are
    small enough to live in the synced vault instead of only on one PC.

.DESCRIPTION
    A model that exists only in a local scratch folder is a model that will be lost. The models
    behind published numbers have to be reproducible on another machine, which means they belong
    next to the notes in Google Drive. A solved model is far too large for that; the same model
    without its solution usually is not - the observed ratio on this vault's models is a few per
    cent of the original size.

    What survives the strip: geometry, materials, physics, mesh SETTINGS, study and solver
    SETTINGS, results definitions, parameters. What goes: computed solutions, generated mesh
    data, derived tables, and the model's edit history (which alone can dominate the file).
    Re-running the model reproduces all of it.

    Companion Java program: StripMph.java in this folder. It is compiled on demand.

.PARAMETER Path
    A .mph file, or a directory to scan.

.PARAMETER OutDir
    Where stripped copies go. Default: alongside the input, with a _stripped suffix.

.PARAMETER Recurse
    Scan subdirectories when Path is a directory.

.PARAMETER MinMB
    Only process files at least this large. Default 1 MB - smaller models are already fine.

.PARAMETER KeepMesh
    Keep generated mesh data. Use only when the mesh is expensive and irreproducible.

.PARAMETER Apply
    Actually run. Without it the script only lists what it would do.

.EXAMPLE
    .\Compress-MphModel.ps1 -Path C:\workspace\COMSOL\queue_2026 -Recurse -Apply

.EXAMPLE
    .\Compress-MphModel.ps1 -Path model.mph -OutDir "C:\Users\User\Мой диск\Obsidian\...\_media" -Apply
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Path,
    [string]$OutDir,
    [switch]$Recurse,
    [double]$MinMB = 1.0,
    [switch]$KeepMesh,
    [switch]$Apply
)

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$java = Join-Path $here 'StripMph.java'
$class = Join-Path $here 'StripMph.class'

$comsolBin = 'C:\Program Files\COMSOL\COMSOL62\Multiphysics\bin\win64'
$compile = Join-Path $comsolBin 'comsolcompile.exe'
$batch = Join-Path $comsolBin 'comsolbatch.exe'
foreach ($exe in @($compile, $batch)) {
    if (-not (Test-Path $exe)) { throw "COMSOL not found: $exe" }
}

if (-not (Test-Path $class) -or
    (Get-Item $java).LastWriteTime -gt (Get-Item $class).LastWriteTime) {
    Write-Output "compiling StripMph.java"
    & $compile $java | Out-Null
    if (-not (Test-Path $class)) { throw "compilation failed" }
}

if (Test-Path $Path -PathType Container) {
    $files = Get-ChildItem -LiteralPath $Path -Filter *.mph -File -Recurse:$Recurse
} else {
    $files = @(Get-Item -LiteralPath $Path)
}
$files = $files | Where-Object { $_.Length -ge $MinMB * 1MB -and $_.Name -notlike '*_stripped.mph' }

if (-not $files) { Write-Output "nothing to do"; return }

$totalBefore = 0L
$totalAfter = 0L
foreach ($f in $files) {
    $totalBefore += $f.Length
    if ($OutDir) {
        if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force $OutDir | Out-Null }
        $out = Join-Path $OutDir $f.Name
    } else {
        $out = Join-Path $f.DirectoryName ($f.BaseName + '_stripped.mph')
    }
    if (-not $Apply) {
        Write-Output ("would strip {0,8:N1} MB  {1}" -f ($f.Length / 1MB), $f.FullName)
        continue
    }
    $env:MPH_IN = $f.FullName
    $env:MPH_OUT = $out
    $env:MPH_KEEP = $(if ($KeepMesh) { 'mesh' } else { '' })
    $log = Join-Path $env:TEMP ('strip_' + $f.BaseName + '.log')
    # stderr is captured for us; the program prints its report on stdout
    $report = & $batch -inputfile $class -batchlog $log -nosave
    $line = $report | Where-Object { $_ -like 'STRIP OUT*' }
    if (Test-Path $out) {
        $after = (Get-Item $out).Length
        $totalAfter += $after
        Write-Output ("{0,8:N1} -> {1,7:N1} MB  ({2,5:N1} %)  {3}" -f `
            ($f.Length / 1MB), ($after / 1MB), (100.0 * $after / $f.Length), $f.Name)
    } else {
        Write-Output ("FAILED  {0}  (see {1})" -f $f.Name, $log)
        if ($line) { Write-Output "  $line" }
    }
}

if ($Apply -and $totalAfter -gt 0) {
    Write-Output ("total {0,0:N1} MB -> {1,0:N1} MB  ({2:N1} %)" -f `
        ($totalBefore / 1MB), ($totalAfter / 1MB), (100.0 * $totalAfter / $totalBefore))
}
