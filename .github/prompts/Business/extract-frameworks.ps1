# Extract Framework Files Script
# This script parses frameworks-master-content.md and populates individual files

$masterFile = ".\frameworks-master-content.md"
$frameworksDir = ".\frameworks"

Write-Host "`n🔧 Extracting framework files from master content..." -ForegroundColor Green

# Read master content
$content = Get-Content $masterFile -Raw

# Split by file markers
$filePattern = '### FILE: (.+?\.md)'
$matches = [regex]::Matches($content, "### FILE: (?<filename>.+?\.md)\s+(?<content>(?:(?!### FILE:).)+)", [System.Text.RegularExpressions.RegexOptions]::Singleline)

$filesCreated = 0

foreach ($match in $matches) {
    $filename = $match.Groups['filename'].Value.Trim()
    $fileContent = $match.Groups['content'].Value.Trim()
    
    $outputPath = Join-Path $frameworksDir $filename
    
    #Write content to file
    $fileContent | Out-File -FilePath $outputPath -Encoding UTF8 -NoNewline
    
    $fileSize = (Get-Item $outputPath).Length
    Write-Host "  ✓ $filename" -NoNewline -ForegroundColor Cyan
    Write-Host " ($([math]::Round($fileSize/1KB, 1)) KB)" -ForegroundColor Gray
    
    $filesCreated++
}

Write-Host "`n✅ Successfully extracted $filesCreated framework files!" -ForegroundColor Green
Write-Host "   Location: $frameworksDir\" -ForegroundColor Cyan
