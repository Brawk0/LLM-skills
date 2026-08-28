[CmdletBinding()]
param(
    [string]$Owner = 'fufellen',
    [string]$Repository = 'LLM-skills',
    [switch]$AsJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-GitHubToken {
    foreach ($variableName in @('GH_TOKEN', 'GITHUB_TOKEN')) {
        $value = [Environment]::GetEnvironmentVariable($variableName)
        if (-not [string]::IsNullOrWhiteSpace($value)) {
            return $value
        }
    }

    # Do not pipe the request into `git credential fill`: PowerShell rewrites the
    # line endings to CRLF on the way to a native command, so git never sees the
    # empty LF-terminated line that closes the credential block and fails with
    # "refusing to work with credential missing protocol field". Writing the
    # request to a temp file with explicit LF and redirecting it is stable.
    $requestFile = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName())
    try {
        [System.IO.File]::WriteAllText(
            $requestFile,
            "protocol=https`nhost=github.com`n`n",
            [System.Text.Encoding]::ASCII)
        $credentialLines = & cmd /c "git credential fill < `"$requestFile`""
        if ($LASTEXITCODE -ne 0) {
            throw 'Git could not obtain a GitHub credential from the configured credential helper.'
        }
    }
    finally {
        Remove-Item -LiteralPath $requestFile -Force -ErrorAction SilentlyContinue
    }

    foreach ($line in $credentialLines) {
        if ($line -match '^password=(.+)$') {
            return $Matches[1]
        }
    }

    throw 'No GitHub token was returned. Authenticate Git or set GH_TOKEN/GITHUB_TOKEN, then run the check again.'
}

function Test-RefPatternMatch {
    param(
        [Parameter(Mandatory)]
        [string]$Pattern,

        [Parameter(Mandatory)]
        [string]$RefName,

        [Parameter(Mandatory)]
        [string]$DefaultBranch
    )

    if ($Pattern -eq '~ALL') {
        return $true
    }
    if ($Pattern -eq '~DEFAULT_BRANCH') {
        return $RefName -eq "refs/heads/$DefaultBranch"
    }

    $wildcard = [System.Management.Automation.WildcardPattern]::new(
        $Pattern,
        [System.Management.Automation.WildcardOptions]::CultureInvariant
    )
    return $wildcard.IsMatch($RefName)
}

function Test-RulesetAppliesToDefaultBranch {
    param(
        [Parameter(Mandatory)]
        $Ruleset,

        [Parameter(Mandatory)]
        [string]$DefaultBranch
    )

    if ($Ruleset.enforcement -ne 'active' -or $Ruleset.target -ne 'branch') {
        return $false
    }

    $defaultRef = "refs/heads/$DefaultBranch"
    $includes = @($Ruleset.conditions.ref_name.include)
    $excludes = @($Ruleset.conditions.ref_name.exclude)

    $included = $includes.Count -eq 0
    foreach ($pattern in $includes) {
        if (Test-RefPatternMatch -Pattern $pattern -RefName $defaultRef -DefaultBranch $DefaultBranch) {
            $included = $true
            break
        }
    }
    if (-not $included) {
        return $false
    }

    foreach ($pattern in $excludes) {
        if (Test-RefPatternMatch -Pattern $pattern -RefName $defaultRef -DefaultBranch $DefaultBranch) {
            return $false
        }
    }

    return $true
}

$token = Get-GitHubToken
try {
    $headers = @{
        Authorization = "Bearer $token"
        Accept = 'application/vnd.github+json'
        'X-GitHub-Api-Version' = '2022-11-28'
        'User-Agent' = 'LLM-skills-contribution-mode-check'
    }

    $user = Invoke-RestMethod -Method Get -Uri 'https://api.github.com/user' -Headers $headers
    $repo = Invoke-RestMethod -Method Get -Uri "https://api.github.com/repos/$Owner/$Repository" -Headers $headers

    $isAdministrator = $repo.permissions.admin -eq $true
    $canPush = $repo.permissions.push -eq $true
    $defaultBranch = [string]$repo.default_branch
    $accessClass = if ($isAdministrator) {
        'administrator'
    }
    elseif ($canPush) {
        'write-collaborator'
    }
    else {
        'external'
    }

    $directMainAllowed = $false
    $bypassStatus = 'not-applicable'
    $applicableRulesetCount = 0

    if ($isAdministrator) {
        $query = @'
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    rulesets(first: 100) {
      nodes {
        databaseId
        bypassActors(first: 100) {
          nodes {
            bypassMode
            repositoryRoleName
          }
        }
      }
    }
  }
}
'@
        $graphBody = @{
            query = $query
            variables = @{
                owner = $Owner
                name = $Repository
            }
        } | ConvertTo-Json -Depth 10
        $graphResponse = Invoke-RestMethod -Method Post -Uri 'https://api.github.com/graphql' -Headers $headers -ContentType 'application/json' -Body $graphBody
        if ($null -ne $graphResponse.PSObject.Properties['errors'] -and $graphResponse.errors) {
            $messages = @($graphResponse.errors | ForEach-Object { $_.message }) -join '; '
            throw "GitHub GraphQL ruleset check failed: $messages"
        }

        $graphRulesets = @($graphResponse.data.repository.rulesets.nodes)
        $restRulesets = @(Invoke-RestMethod -Method Get -Uri "https://api.github.com/repos/$Owner/$Repository/rulesets?includes_parents=true&per_page=100" -Headers $headers)
        $rulesetsWithoutAdminBypass = @()

        foreach ($rulesetSummary in $restRulesets) {
            $ruleset = Invoke-RestMethod -Method Get -Uri "https://api.github.com/repos/$Owner/$Repository/rulesets/$($rulesetSummary.id)" -Headers $headers
            if (-not (Test-RulesetAppliesToDefaultBranch -Ruleset $ruleset -DefaultBranch $defaultBranch)) {
                continue
            }

            $applicableRulesetCount++
            $graphRuleset = $graphRulesets | Where-Object { $_.databaseId -eq $ruleset.id } | Select-Object -First 1
            $hasAdminBypass = $false
            if ($null -ne $graphRuleset) {
                $hasAdminBypass = @($graphRuleset.bypassActors.nodes | Where-Object {
                    $_.repositoryRoleName -eq 'admin' -and $_.bypassMode -eq 'ALWAYS'
                }).Count -gt 0
            }

            if (-not $hasAdminBypass) {
                $rulesetsWithoutAdminBypass += [string]$ruleset.name
            }
        }

        if ($applicableRulesetCount -eq 0) {
            $directMainAllowed = $true
            $bypassStatus = 'no-active-default-branch-ruleset'
        }
        elseif ($rulesetsWithoutAdminBypass.Count -eq 0) {
            $directMainAllowed = $true
            $bypassStatus = 'confirmed-always'
        }
        else {
            $bypassStatus = 'not-confirmed'
        }
    }

    $branchName = "main_$($user.login)"
    $recommendedAction = if ($isAdministrator -and $directMainAllowed) {
        "Push to origin/$defaultBranch; a pull request is optional."
    }
    elseif ($canPush) {
        "Push origin/$branchName and open a pull request to $Owner/${Repository}:$defaultBranch."
    }
    else {
        "Create a fork, push fork/$branchName, and open a pull request to $Owner/${Repository}:$defaultBranch."
    }

    $result = [pscustomobject]@{
        Login = [string]$user.login
        Repository = "$Owner/$Repository"
        AccessClass = $accessClass
        DefaultBranch = $defaultBranch
        AdministratorBypass = $bypassStatus
        DirectMainAllowed = $directMainAllowed
        RequiresFork = -not $canPush
        RequiresPullRequest = -not ($isAdministrator -and $directMainAllowed)
        WorkingBranch = if ($isAdministrator -and $directMainAllowed) { $defaultBranch } else { $branchName }
        RecommendedAction = $recommendedAction
        RulesetsChecked = $applicableRulesetCount
    }

    if ($AsJson) {
        $result | ConvertTo-Json -Depth 5
    }
    else {
        $result
    }
}
finally {
    $token = $null
}
