# Read-only configuration checks; Windows PowerShell 5.1 and PowerShell 7.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Root,
    [string]$MenuDirectory = 'Bar\xpl',
    [string]$TabDirectory = 'Tab',
    [int]$LegacyCodePage = 0,
    [switch]$Strict
)
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path -LiteralPath $Root).Path.TrimEnd('\')
$errorsFound = [Collections.Generic.List[string]]::new()
$notes = [Collections.Generic.List[string]]::new()
$unresolved = [Collections.Generic.List[object]]::new()
if ($LegacyCodePage -eq 0) { $LegacyCodePage = (Get-Culture).TextInfo.ANSICodePage }
$utf8Strict = [Text.UTF8Encoding]::new($false, $true)
$legacy = [Text.Encoding]::GetEncoding($LegacyCodePage, [Text.EncoderFallback]::ExceptionFallback, [Text.DecoderFallback]::ExceptionFallback)

function Read-TcText([string]$Path) {
    $bytes = [IO.File]::ReadAllBytes($Path)
    if (($bytes.Length -ge 2 -and (($bytes[0] -eq 255 -and $bytes[1] -eq 254) -or ($bytes[0] -eq 254 -and $bytes[1] -eq 255))) -or
        ($bytes.Length -ge 4 -and $bytes[0] -eq 0 -and $bytes[1] -eq 0 -and $bytes[2] -eq 254 -and $bytes[3] -eq 255)) {
        # StreamReader honors BOMs, including UTF-32, without changing the file.
        return [IO.File]::ReadAllText($Path)
    }
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191) {
        return $utf8Strict.GetString($bytes, 3, $bytes.Length - 3)
    }
    try { return $utf8Strict.GetString($bytes) }
    catch [Text.DecoderFallbackException] { return $legacy.GetString($bytes) }
}

function Expand-TcPath([string]$Value) {
    $expanded = [regex]::Replace($Value.Trim().Trim('"'), '(?i)%Commander_path%', { param($m) $Root })
    return [Environment]::ExpandEnvironmentVariables($expanded)
}

function Local-Directory([string]$Relative) {
    if ([IO.Path]::IsPathRooted($Relative)) { throw 'MenuDirectory and TabDirectory must be relative to Root.' }
    $path = [IO.Path]::GetFullPath((Join-Path $Root $Relative))
    if (-not $path.StartsWith($Root + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Configuration directory escapes Root.' }
    if (-not (Test-Path -LiteralPath $path -PathType Container)) { throw "Configuration directory missing: $path" }
    return $path
}

function Parse-Ini([string]$Path) {
    $sections = @{}; $current = $null
    foreach ($line in ((Read-TcText $Path) -split '\r?\n')) {
        if ($line -match '^\s*\[([^\]]+)\]\s*$') {
            $name = $Matches[1]
            if ($sections.ContainsKey($name)) { $errorsFound.Add("Duplicate section: $Path [$name]") }
            $current = @{}; $sections[$name] = $current
        } elseif ($null -ne $current -and $line -notmatch '^\s*[;#]' -and $line -match '^([^=]+)=(.*)$') {
            $key = $Matches[1].Trim(); $value = $Matches[2]
            if ($current.ContainsKey($key)) { $errorsFound.Add("Duplicate key: $Path $key") }
            $current[$key] = $value
        }
    }
    return ,$sections
}

function Check-Reference([string]$File, [string]$Key, [string]$Value) {
    $path = Expand-TcPath $Value
    if ($path -match '^\\\\|^ftp[s]?://|%[^%]+%') {
        $notes.Add("Reference not checked (remote/unresolved variable): $File $Key=$Value")
    } elseif (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        $errorsFound.Add("Missing reference: $File $Key=$Value")
    }
}

$menuPath = Local-Directory $MenuDirectory
$tabPath = Local-Directory $TabDirectory
$bars = @(@(Get-ChildItem -LiteralPath $Root -Filter '*.bar' -File) + @(Get-ChildItem -LiteralPath $menuPath -Filter '*.bar' -File) | Sort-Object FullName -Unique)
$tabs = @(Get-ChildItem -LiteralPath $tabPath -Filter '*.tab' -File)
foreach ($file in $bars) {
    $sections = Parse-Ini $file.FullName
    $bar = $sections['Buttonbar']
    if ($null -eq $bar -or $bar['Buttoncount'] -notmatch '^\d+$') { $errorsFound.Add("Invalid Buttoncount: $($file.FullName)"); continue }
    $count = [int]$bar['Buttoncount']
    foreach ($key in $bar.Keys) {
        if ($key -match '^([A-Za-z_]+)(\d+)$' -and ([int]$Matches[2] -lt 1 -or [int]$Matches[2] -gt $count)) {
            $errorsFound.Add("Button index outside count: $($file.Name) $key")
        }
    }
    for ($i = 1; $i -le $count; $i++) {
        $hasFields = @($bar.Keys | Where-Object { $_ -match ('^[A-Za-z_]+' + $i + '$') }).Count -gt 0
        if (-not $hasFields) { $errorsFound.Add("Missing button index: $($file.Name) $i"); continue }
        $cmd = $bar["cmd$i"]; $icon = $bar["button$i"]
        if ($bar["menu$i"] -and -not $cmd) { $errorsFound.Add("Labeled button has no command: $($file.Name) $i") }
        if ($cmd -match '(?i)^(OPENTABS|APPENDTABS|OPENBAR)\s+(.+)$') {
            Check-Reference $file.Name "cmd$i" $Matches[2]
        } elseif ($cmd -match '^em_') { $notes.Add("User command definition requires separate inspection: $($file.Name) cmd$i=$cmd") }
        if ($icon) {
            $iconPath = Expand-TcPath ($icon -replace ',\s*-?\d+$', '')
            if ($iconPath -match '^\\\\|%[^%]+%') { $notes.Add("Icon reference not checked: $($file.Name) $i") }
            elseif ([IO.Path]::IsPathRooted($iconPath)) {
                if (-not (Test-Path -LiteralPath $iconPath -PathType Leaf)) { $errorsFound.Add("Missing icon: $($file.Name) button$i=$icon") }
            } else { $notes.Add("Native icon/resource index not checked: $($file.Name) button$i=$icon") }
        }
        foreach ($key in @("cmd$i", "button$i", "path$i", "param$i")) {
            if ($bar[$key] -and $bar[$key].IndexOf($Root + '\', [StringComparison]::OrdinalIgnoreCase) -ge 0) {
                $errorsFound.Add("Absolute TC installation reference: $($file.Name) $key")
            }
        }
    }
}
foreach ($file in $tabs) {
    $sections = Parse-Ini $file.FullName
    $recognized = 0
    foreach ($name in @('activetabs', 'inactivetabs')) {
        if (-not $sections.ContainsKey($name)) { continue }
        $recognized++; $section = $sections[$name]
        $indices = @($section.Keys | Where-Object { $_ -match '^\d+_path$' } | ForEach-Object { [int]($_ -split '_')[0] } | Sort-Object)
        for ($i = 0; $i -lt $indices.Count; $i++) {
            if ($indices[$i] -ne $i) { $errorsFound.Add("Non-contiguous tab indices: $($file.Name) [$name]"); break }
        }
        if ($indices.Count -eq 0 -or $section['activetab'] -notmatch '^\d+$' -or [int]$section['activetab'] -ge $indices.Count) {
            $errorsFound.Add("Invalid selected tab: $($file.Name) [$name]")
        }
        foreach ($i in $indices) {
            $value = $section["${i}_path"]; $path = Expand-TcPath $value
            $reason = $null
            if ($path -match '^\\\\|^ftp[s]?://|%[^%]+%') { $reason = 'Remote or unresolved variable; not accessed' }
            elseif ($path -match '(?i)\.(zip|rar|7z)(?=\\|$)') { $reason = 'Archive contents not checked' }
            elseif (-not (Test-Path -LiteralPath $path -PathType Container)) { $reason = 'Directory missing or drive offline' }
            if ($reason) { $unresolved.Add([pscustomobject]@{File=$file.Name; Section=$name; Index=$i; Path=$value; Reason=$reason}) }
            if ($value.StartsWith($Root + '\', [StringComparison]::OrdinalIgnoreCase)) { $errorsFound.Add("Absolute TC installation reference: $($file.Name) [$name] ${i}_path") }
        }
    }
    if ($recognized -eq 0) { $errorsFound.Add("No recognized tab sections: $($file.Name)") }
}
$result = [pscustomobject]@{ Root=$Root; BarCount=$bars.Count; TabCount=$tabs.Count; Errors=@($errorsFound.ToArray()); Notes=@($notes.ToArray()); UnresolvedPaths=@($unresolved.ToArray()) }
$result
if ($Strict -and $errorsFound.Count -gt 0) { throw "TC configuration contains $($errorsFound.Count) structural/reference errors." }
