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
$Model = "large-v3"
$WhisperExe = "D:\Faster-Whisper-XXL\faster-whisper-xxl.exe"

if (-not (Test-Path $InputVideo)) {
    Write-Error "找不到视频: $InputVideo"
    exit 1
}

Write-Host "识别中... 模型: $Model"
& $WhisperExe "$InputVideo" -pp -o "$ProjectDir" --check_files --standard -f srt -m $Model

$RawSrt = "$ProjectDir\$ProjectName.srt"
$EnSrt = "$ProjectDir\$ProjectName.en.srt"

if (Test-Path $EnSrt) { Remove-Item $EnSrt }
if (Test-Path $RawSrt) {
    Move-Item $RawSrt $EnSrt
    Write-Host "完成: $EnSrt"
} else {
    Write-Error "未生成字幕文件: $RawSrt"
    exit 1
}
