param(
    [Parameter(Mandatory=$true, HelpMessage="请输入视频网址")]
    [string]$Url,
    [Parameter(Mandatory=$true, HelpMessage="请输入项目名称")]
    [string]$Name
)

$ProjectDir = ".\$Name"
New-Item -ItemType Directory -Path $ProjectDir -Force | Out-Null

Write-Host "下载视频中..."
yt-dlp -f 399+140 --write-thumbnail --convert-thumbnails jpg -o "$ProjectDir\$Name.%(ext)s" $Url
if ($LASTEXITCODE -ne 0) {
    Write-Error "视频下载失败（网络/SSL 错误）"
    exit 1
}

$ThumbJpg  = "$ProjectDir\$Name.jpg"
if (-not (Test-Path $ThumbJpg)) {
    Write-Warning "缩略图未下载，网络问题或需手动补下"
}

Write-Host "获取视频信息..."
$Title = "?"
$Author = "?"
$Date = "?"
$Id = ""
$meta = yt-dlp --skip-download --print "%(title)s" --print "%(uploader)s" --print "%(upload_date)s" --print "%(id)s" $Url 2>$null
if ($LASTEXITCODE -eq 0) {
    $lines = $meta -split "`n"
    $Title = $lines[0]
    $Author = $lines[1]
    $Date = $lines[2]
    $Id = $lines[3]
} else {
    Write-Warning "无法获取视频信息（网络问题），info.txt 可能为空"
}

if ($Id) {
    if ($Url -match "/shorts/") {
        $ShortUrl = "https://www.youtube.com/shorts/$Id"
    } else {
        $ShortUrl = "https://youtu.be/$Id"
    }
} else {
    $ShortUrl = $Url
}

@"
URL: $ShortUrl
Title: $Title
Author: $Author
Date: $Date
"@ | Out-File -FilePath "$ProjectDir\info.txt" -Encoding utf8

$Name | Out-File -FilePath ".\current.txt" -Encoding utf8

Write-Host "下载完成: $Name"
