# One isolated behavior check; never reads or writes an installed TC.
$ErrorActionPreference = 'Stop'
$sandbox = Join-Path ([IO.Path]::GetTempPath()) ('tc-config-check-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path "$sandbox\Tab", "$sandbox\Bar\xpl", "$sandbox\PIC", "$sandbox\Docs" | Out-Null
$checker = Join-Path $PSScriptRoot 'Test-TcConfig.ps1'
$cp936 = [Text.Encoding]::GetEncoding(936)
$utf16 = [Text.UnicodeEncoding]::new($false, $true)
try {
    $tab = "[activetabs]`r`n0_path=%Commander_path%\Docs\`r`n0_caption=每日连载`r`n0_options=1|3|1|0|0|0|0|`r`nactivetab=0`r`n[inactivetabs]`r`n0_path=%Commander_path%\Docs\`r`nactivetab=0`r`n"
    [IO.File]::WriteAllText("$sandbox\Tab\连载 记录.tab", $tab, $cp936)
    [IO.File]::WriteAllBytes("$sandbox\PIC\阅读.ico", [byte[]]@(0,0,1,0))
    $bar = "[Buttonbar]`r`nButtoncount=2`r`nbutton1=%Commander_path%\PIC\阅读.ico`r`ncmd1=OPENTABS `"%Commander_path%\Tab\连载 记录.tab`"`r`nmenu1=每日连载`r`nbutton2=`r`niconic2=0`r`n"
    [IO.File]::WriteAllText("$sandbox\Bar\xpl\培训.BAR", $bar, $cp936)
    $before = (Get-FileHash -LiteralPath "$sandbox\Bar\xpl\培训.BAR").Hash
    $r = & $checker -Root $sandbox -LegacyCodePage 936
    if ($r.Errors.Count -ne 0 -or $r.UnresolvedPaths.Count -ne 0 -or $r.BarCount -ne 1 -or $r.TabCount -ne 1) { throw ('Valid CP936 configuration rejected: ' + ($r.Errors -join '; ') + ' paths=' + ($r.UnresolvedPaths | ConvertTo-Json -Compress)) }
    if ((Get-FileHash -LiteralPath "$sandbox\Bar\xpl\培训.BAR").Hash -ne $before) { throw 'Checker modified input' }
    [IO.File]::WriteAllText("$sandbox\Tab\连载 记录.tab", $tab, $utf16)
    $r = & $checker -Root $sandbox -LegacyCodePage 936
    if ($r.Errors.Count -ne 0 -or $r.UnresolvedPaths.Count -ne 0) { throw 'UTF-16 BOM handling failed' }
    $badTab = $tab.Replace('activetab=0', 'activetab=3').Replace("0_path=%Commander_path%\Docs\", "0_path=%Commander_path%\Missing\")
    [IO.File]::WriteAllText("$sandbox\Tab\连载 记录.tab", $badTab, [Text.UTF8Encoding]::new($false))
    $r = & $checker -Root $sandbox -LegacyCodePage 936
    if ($r.Errors.Count -ne 2 -or $r.UnresolvedPaths.Count -ne 2) { throw 'Selected index or missing-directory detection failed' }
    $badBar = $bar.Replace('Buttoncount=2', 'Buttoncount=1') + "menu1=重复`r`ncmd3=OPENTABS %Commander_path%\Tab\missing.tab`r`n"
    [IO.File]::WriteAllText("$sandbox\Bar\xpl\培训.BAR", $badBar, $cp936)
    $r = & $checker -Root $sandbox -LegacyCodePage 936
    if (-not ($r.Errors -match 'Duplicate key') -or -not ($r.Errors -match 'outside count')) { throw 'Menu corruption not detected' }
    [IO.File]::WriteAllText("$sandbox\Bar\xpl\培训.BAR", $bar.Replace('button2=', 'button2=%Commander_path%\PIC\missing.ico').Replace('连载 记录.tab', 'missing.tab'), $cp936)
    $r = & $checker -Root $sandbox -LegacyCodePage 936
    if (-not ($r.Errors -match 'Missing icon') -or -not ($r.Errors -match 'Missing reference')) { throw 'Missing icon/tab not detected' }
    $strictFailed = $false
    try { & $checker -Root $sandbox -LegacyCodePage 936 -Strict | Out-Null } catch { $strictFailed = $true }
    if (-not $strictFailed) { throw 'Strict mode accepted corrupt configuration' }
    $escaped = $false
    try { & $checker -Root $sandbox -MenuDirectory '..' | Out-Null } catch { $escaped = $true }
    if (-not $escaped) { throw 'Escaping configuration directory accepted' }
    Write-Output 'PASS: CP936, UTF-8, UTF-16, quoted Chinese paths, read-only behavior, bad indices, duplicate keys, missing icons, directory bounds.'
} finally {
    # Only delete the exact random temp directory created above.
    $resolved = [IO.Path]::GetFullPath($sandbox)
    $tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\') + '\'
    if ($resolved.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase) -and [IO.Path]::GetFileName($resolved) -like 'tc-config-check-*') {
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
}
