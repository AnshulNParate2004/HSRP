# Build HSRP AI Framework LaTeX document
$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Diagrams are AI-generated PNGs in images/ (not matplotlib script)
if (-not (Test-Path "images/hsrp-architecture-flow.png")) {
    Write-Host "ERROR: Missing images/hsrp-architecture-flow.png - regenerate via AI image prompts."
    exit 1
}

Write-Host "Compiling LaTeX (pass 1)..."
pdflatex -interaction=nonstopmode hsrp-ai-framework.tex | Out-Null

Write-Host "Compiling LaTeX (pass 2)..."
pdflatex -interaction=nonstopmode hsrp-ai-framework.tex | Out-Null

if (Test-Path "hsrp-ai-framework.pdf") {
    Write-Host "Success: hsrp-ai-framework.pdf"
} else {
    Write-Host "Build failed. Check hsrp-ai-framework.log"
    exit 1
}
