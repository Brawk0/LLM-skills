#requires -Version 5.1

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$LogicalName,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Artifact,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$OutputDirectory,

    [ValidateSet('BUILDOK', 'HWRUN', 'HWOK')]
    [string]$Status = 'BUILDOK',

    [string]$RepoRoot,
    [string]$ExpectedRepository = 'ak-tech-electronics/ToF-LIDAR-FPGA',
    [ValidateSet('TDC7201', 'LTDC', 'FPGA_TDC', 'Other')]
    [string]$TimingArchitecture,
    [string]$FsFileForUserCode,
    [string]$TopModule,
    [string]$Target,
    [string]$BuildCommand,
    [string]$ToolVersion,
    [string]$Notes,

    [switch]$AllowDirty,
    [switch]$AllowArtifactOlderThanCommit,
    [switch]$AllowOtherBranch,
    [switch]$OmitUserCodeFromName,
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-RepositoryGit {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $output = @(& git -c core.safecrlf=false -C $script:RepositoryRoot @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    if ($exitCode -ne 0) {
        $rendered = [string]::Join(' ', $Arguments)
        $details = [string]::Join([Environment]::NewLine, @($output | ForEach-Object { [string]$_ }))
        throw "git $rendered failed with exit code $exitCode.$([Environment]::NewLine)$details"
    }

    return @($output | ForEach-Object { [string]$_ })
}

function Normalize-RepositoryName {
    param([string]$Value)

    $normalized = $Value.Trim()
    $normalized = $normalized -replace '^git@github\.com:', ''
    $normalized = $normalized -replace '^ssh://git@github\.com/', ''
    $normalized = $normalized -replace '^https?://github\.com/', ''
    $normalized = $normalized.TrimEnd('/')
    $normalized = $normalized -replace '\.git$', ''
    return $normalized
}

function Get-TextSha256 {
    param([string]$Text)

    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
        $digest = $algorithm.ComputeHash($bytes)
        return ([System.BitConverter]::ToString($digest) -replace '-', '').ToLowerInvariant()
    }
    finally {
        $algorithm.Dispose()
    }
}

function Get-OptionalValue {
    param([string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $null
    }

    return $Value
}

$repositoryCandidate = $RepoRoot
if ([string]::IsNullOrWhiteSpace($repositoryCandidate)) {
    $repositoryCandidate = (Get-Location).Path
}

$rootOutput = @(& git -C $repositoryCandidate rev-parse --show-toplevel 2>&1)
if ($LASTEXITCODE -ne 0) {
    throw "Cannot locate a Git repository from '$repositoryCandidate'."
}

$rootText = [string]($rootOutput | Select-Object -First 1)
$script:RepositoryRoot = (Resolve-Path -LiteralPath $rootText).Path

$fpgaPattern = '^(?<model>[A-Z][A-Z0-9-]*)\.BF(?<BF>[1-9][0-9]*)MF(?<MF>[1-9][0-9]*)FP(?<FP>[1-9][0-9]*)X(?<X>[1-9][0-9]*)$'
$mcuPattern = '^(?<model>[A-Z][A-Z0-9-]*)\.BM(?<BM>[1-9][0-9]*)MF(?<MF>[1-9][0-9]*)MP(?<MP>[1-9][0-9]*)X(?<X>[1-9][0-9]*)$'

$kind = $null
$logicalMatch = [System.Text.RegularExpressions.Regex]::Match($LogicalName, $fpgaPattern)
if ($logicalMatch.Success) {
    $kind = 'fpga'
    $compatibility = [ordered]@{
        BF = [int]$logicalMatch.Groups['BF'].Value
        MF = [int]$logicalMatch.Groups['MF'].Value
        FP = [int]$logicalMatch.Groups['FP'].Value
        X  = [int]$logicalMatch.Groups['X'].Value
    }
}
else {
    $logicalMatch = [System.Text.RegularExpressions.Regex]::Match($LogicalName, $mcuPattern)
    if (-not $logicalMatch.Success) {
        throw "Invalid logical name '$LogicalName'. Expected canonical <model>.BM...MF...MP...X... or <model>.BF...MF...FP...X... without underscores."
    }

    $kind = 'mcu'
    $compatibility = [ordered]@{
        BM = [int]$logicalMatch.Groups['BM'].Value
        MF = [int]$logicalMatch.Groups['MF'].Value
        MP = [int]$logicalMatch.Groups['MP'].Value
        X  = [int]$logicalMatch.Groups['X'].Value
    }
}

$model = $logicalMatch.Groups['model'].Value
$firmwareIteration = [int]$logicalMatch.Groups['X'].Value

if (-not $model.Equals('R120M', [System.StringComparison]::Ordinal)) {
    throw "Unsupported product model '$model'. Expected 'R120M'."
}

# BF кодирует физическую плату, не измеритель: плата BF2 (BM2BF1X1) несёт LTDC и
# TDC7201; боевая линия BF2 — LTDC, TDC7201 собирается из вариантной ветки.
$allowedArchitectures = @()
$expectedBranch = $model
if ($kind -eq 'fpga') {
    $bf = [int]$compatibility.BF
    $expectedBranch = "$model.BF$bf"

    if ($model.Equals('R120M', [System.StringComparison]::Ordinal)) {
        switch ($bf) {
            1 { $allowedArchitectures = @('TDC7201') }
            2 { $allowedArchitectures = @('LTDC', 'TDC7201') }
        }
    }
}
$knownArchitecture = $null
if ($allowedArchitectures.Count -gt 0) {
    $knownArchitecture = $allowedArchitectures[0]
}
if (
    ($allowedArchitectures.Count -gt 0) -and
    (-not [string]::IsNullOrWhiteSpace($TimingArchitecture)) -and
    (-not ($allowedArchitectures -ccontains $TimingArchitecture))
) {
    throw "Timing architecture '$TimingArchitecture' conflicts with the allowed set '$([string]::Join(', ', $allowedArchitectures))' for '$LogicalName'."
}
if (-not [string]::IsNullOrWhiteSpace($TimingArchitecture)) {
    $architecture = $TimingArchitecture
}
elseif (-not [string]::IsNullOrWhiteSpace($knownArchitecture)) {
    $architecture = $knownArchitecture
}
else {
    $architecture = 'Unspecified'
}

$originUrl = [string](Invoke-RepositoryGit -Arguments @('remote', 'get-url', 'origin') | Select-Object -First 1)
$normalizedOrigin = Normalize-RepositoryName -Value $originUrl
$normalizedExpectedRepository = Normalize-RepositoryName -Value $ExpectedRepository
if (-not $normalizedOrigin.Equals($normalizedExpectedRepository, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Unexpected origin '$originUrl'. Expected '$ExpectedRepository'."
}

$branch = [string](Invoke-RepositoryGit -Arguments @('rev-parse', '--abbrev-ref', 'HEAD') | Select-Object -First 1)
if ($branch -eq 'HEAD') {
    throw 'Detached HEAD is not allowed for release packaging.'
}

$branchMatches = $branch.Equals($expectedBranch, [System.StringComparison]::Ordinal)
if ((-not $branchMatches) -and (-not $AllowOtherBranch)) {
    throw "Logical name '$LogicalName' belongs to production branch '$expectedBranch', current branch is '$branch'."
}
if ((-not $branchMatches) -and ($Status -eq 'HWOK')) {
    throw 'HWOK is not allowed when the product name and production branch do not match.'
}

$commitFull = [string](Invoke-RepositoryGit -Arguments @('rev-parse', 'HEAD') | Select-Object -First 1)
$commitShort = $commitFull.Substring(0, [Math]::Min(12, $commitFull.Length))
$commitTime = [string](Invoke-RepositoryGit -Arguments @('show', '-s', '--format=%cI', 'HEAD') | Select-Object -First 1)
$commitTimeUtc = [System.DateTimeOffset]::Parse(
    $commitTime,
    [System.Globalization.CultureInfo]::InvariantCulture
).UtcDateTime
$commitUrl = "https://github.com/$normalizedOrigin/commit/$commitFull"

$trackedStatus = @(
    Invoke-RepositoryGit -Arguments @('status', '--porcelain=v1', '--untracked-files=no') |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
)
$untrackedFiles = @(
    Invoke-RepositoryGit -Arguments @('ls-files', '--others', '--exclude-standard') |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
)
$submodules = @(
    Invoke-RepositoryGit -Arguments @('submodule', 'status', '--recursive') |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
)

$sourceTrackedClean = ($trackedStatus.Count -eq 0)
if ((-not $sourceTrackedClean) -and (-not $AllowDirty)) {
    $details = [string]::Join([Environment]::NewLine, $trackedStatus)
    throw "Tracked files or submodules are dirty. Commit them or use -AllowDirty for a diagnostic image only.$([Environment]::NewLine)$details"
}
if ((-not $sourceTrackedClean) -and ($Status -eq 'HWOK')) {
    throw 'HWOK is not allowed for a dirty source tree.'
}

$dirtyDiffSha256 = $null
if (-not $sourceTrackedClean) {
    $diff = @(
        Invoke-RepositoryGit -Arguments @('diff', '--binary', '--submodule=short', 'HEAD', '--')
    )
    $dirtyIdentity = [string]::Join(
        [Environment]::NewLine,
        @($trackedStatus + $submodules + $diff)
    )
    $dirtyDiffSha256 = Get-TextSha256 -Text $dirtyIdentity
}

$resolvedArtifact = Resolve-Path -LiteralPath $Artifact
$artifactItem = Get-Item -LiteralPath $resolvedArtifact.Path
if ($artifactItem.PSIsContainer) {
    throw "Artifact '$Artifact' is a directory."
}

$artifactFreshForCommit = ($artifactItem.LastWriteTimeUtc -ge $commitTimeUtc.AddSeconds(-2))
if ((-not $artifactFreshForCommit) -and (-not $AllowArtifactOlderThanCommit)) {
    throw "Artifact '$($artifactItem.FullName)' is older than commit $commitShort. Rebuild from HEAD or use -AllowArtifactOlderThanCommit for diagnostics only."
}
if ((-not $artifactFreshForCommit) -and ($Status -eq 'HWOK')) {
    throw 'HWOK is not allowed for an artifact older than the source commit.'
}

$artifactSha256 = (Get-FileHash -LiteralPath $artifactItem.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
$artifactShort = $artifactSha256.Substring(0, 12)
$extension = $artifactItem.Extension.ToLowerInvariant()
if ([string]::IsNullOrWhiteSpace($extension)) {
    throw 'Artifact must have a file extension.'
}

$userCode = $null
$userCodeSource = $null
if ($extension.Equals('.fs', [System.StringComparison]::OrdinalIgnoreCase)) {
    $userCodeSource = $artifactItem.FullName
}
elseif (-not [string]::IsNullOrWhiteSpace($FsFileForUserCode)) {
    $userCodeSource = (Resolve-Path -LiteralPath $FsFileForUserCode).Path
}

if (-not [string]::IsNullOrWhiteSpace($userCodeSource)) {
    $headerLines = @(Get-Content -LiteralPath $userCodeSource -TotalCount 128)
    $headerText = [string]::Join([Environment]::NewLine, $headerLines)
    $userCodeMatch = [System.Text.RegularExpressions.Regex]::Match(
        $headerText,
        'UserCode:\s*0x(?<code>[0-9A-Fa-f]{8})',
        [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
    )
    if ($userCodeMatch.Success) {
        $userCode = $userCodeMatch.Groups['code'].Value.ToUpperInvariant()
    }
}

$nameParts = @(
    $LogicalName
    "git-$commitShort"
    "img-$artifactShort"
)
if ((-not $OmitUserCodeFromName) -and (-not [string]::IsNullOrWhiteSpace($userCode))) {
    $nameParts += "uc-$userCode"
}
if (-not $sourceTrackedClean) {
    $nameParts += 'dirty'
}
if (-not $artifactFreshForCommit) {
    $nameParts += 'stale'
}
$nameParts += $Status
$releaseStem = [string]::Join('.', $nameParts)

if ([System.IO.Path]::IsPathRooted($OutputDirectory)) {
    $outputRoot = [System.IO.Path]::GetFullPath($OutputDirectory)
}
else {
    $outputRoot = [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $OutputDirectory))
}
[System.IO.Directory]::CreateDirectory($outputRoot) | Out-Null

$releasedArtifactName = "$releaseStem$extension"
$releasedArtifactPath = Join-Path $outputRoot $releasedArtifactName
$manifestPath = Join-Path $outputRoot "$releaseStem.manifest.json"
$checksumPath = Join-Path $outputRoot "$releaseStem.sha256"

foreach ($candidatePath in @($releasedArtifactPath, $manifestPath, $checksumPath)) {
    if ((Test-Path -LiteralPath $candidatePath) -and (-not $Force)) {
        throw "Output '$candidatePath' already exists. Use -Force to replace it."
    }
}

Copy-Item -LiteralPath $artifactItem.FullName -Destination $releasedArtifactPath -Force:$Force
$copiedSha256 = (Get-FileHash -LiteralPath $releasedArtifactPath -Algorithm SHA256).Hash.ToLowerInvariant()
if (-not $copiedSha256.Equals($artifactSha256, [System.StringComparison]::Ordinal)) {
    throw 'Copied artifact SHA-256 does not match the source artifact.'
}

$manifest = [ordered]@{
    schema_version = 2
    trace_id = "$commitShort-$artifactShort"
    logical_name = $LogicalName
    firmware_kind = $kind
    status = $Status
    official_release = (
        ($Status -eq 'HWOK') -and
        $sourceTrackedClean -and
        $branchMatches -and
        $artifactFreshForCommit
    )
    packaged_at_utc = [System.DateTime]::UtcNow.ToString('o')
    product = [ordered]@{
        model = $model
        firmware_iteration = $firmwareIteration
        timing_architecture = $architecture
        release_branch = $expectedBranch
    }
    compatibility = $compatibility
    source = [ordered]@{
        repository = $normalizedOrigin
        origin_url = $originUrl
        branch = $branch
        expected_branch = $expectedBranch
        branch_matches_release_line = $branchMatches
        commit = $commitFull
        commit_short = $commitShort
        commit_url = $commitUrl
        commit_time = $commitTime
        tracked_clean = $sourceTrackedClean
        reproducible_from_commit = ($sourceTrackedClean -and $artifactFreshForCommit)
        tracked_status = @($trackedStatus)
        untracked_files_not_in_commit = @($untrackedFiles)
        dirty_diff_sha256 = $dirtyDiffSha256
        submodules = @($submodules)
    }
    build = [ordered]@{
        top_module = Get-OptionalValue -Value $TopModule
        target = Get-OptionalValue -Value $Target
        command = Get-OptionalValue -Value $BuildCommand
        tool_version = Get-OptionalValue -Value $ToolVersion
        gowin_user_code = $userCode
        gowin_user_code_source = $userCodeSource
        stale_artifact_override = [bool]$AllowArtifactOlderThanCommit
        notes = Get-OptionalValue -Value $Notes
    }
    artifact = [ordered]@{
        original_path = $artifactItem.FullName
        original_name = $artifactItem.Name
        released_name = $releasedArtifactName
        size_bytes = [int64]$artifactItem.Length
        original_last_write_utc = $artifactItem.LastWriteTimeUtc.ToString('o')
        source_commit_time_utc = $commitTimeUtc.ToString('o')
        fresh_for_source_commit = $artifactFreshForCommit
        seconds_after_source_commit = [Math]::Round(
            ($artifactItem.LastWriteTimeUtc - $commitTimeUtc).TotalSeconds,
            3
        )
        sha256 = $artifactSha256
        sha256_short = $artifactShort
        checksum_file = [System.IO.Path]::GetFileName($checksumPath)
    }
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$manifestJson = $manifest | ConvertTo-Json -Depth 8
[System.IO.File]::WriteAllText($manifestPath, $manifestJson + [Environment]::NewLine, $utf8NoBom)
[System.IO.File]::WriteAllText(
    $checksumPath,
    "$artifactSha256  $releasedArtifactName$([Environment]::NewLine)",
    $utf8NoBom
)

[pscustomobject]@{
    LogicalName = $LogicalName
    Branch = $branch
    Commit = $commitFull
    ArtifactSha256 = $artifactSha256
    GowinUserCode = $userCode
    Status = $Status
    TrackedClean = $sourceTrackedClean
    ReleasedArtifact = $releasedArtifactPath
    Manifest = $manifestPath
    Checksum = $checksumPath
}
