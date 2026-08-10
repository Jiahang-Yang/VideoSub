param(
    [string]$ProjectName
)

if (-not $ProjectName) {
    $ProjectName = Get-Content ".\current.txt" -First 1
    if (-not $ProjectName) {
        Write-Error "current.txt 为空，请提供 -ProjectName 参数"
        exit 1
    }
}

$ProjectDir = ".\$ProjectName"
$InputVideo = "$ProjectDir\$ProjectName.mp4"
$SubtitleAss = "$ProjectDir\$ProjectName.ass"
$NotesAss = "$ProjectDir\notes.ass"
$OutputVideo = "$ProjectDir\$ProjectName`_burnt.mp4"

if (-not (Test-Path $InputVideo)) {
    Write-Error "找不到视频: $InputVideo"
    exit 1
}
if (-not (Test-Path $SubtitleAss)) {
    Write-Error "找不到字幕: $SubtitleAss"
    exit 1
}

$HasNotes = Test-Path $NotesAss

Push-Location $ProjectDir

if ($HasNotes) {
    Write-Host "烧制硬字幕中（双语 + 注释）..."
    ffmpeg -y -i "$ProjectName.mp4" -vf "subtitles=$ProjectName.ass,subtitles=notes.ass" -c:a copy "$ProjectName`_burnt.mp4"
} else {
    Write-Host "烧制硬字幕中（仅双语）..."
    ffmpeg -y -i "$ProjectName.mp4" -vf "subtitles=$ProjectName.ass" -c:a copy "$ProjectName`_burnt.mp4"
}

Pop-Location

if ($LASTEXITCODE -eq 0) {
    Write-Host "完成: $OutputVideo"
} else {
    Write-Error "烧制失败"
    exit 1
}
