# PowerShell script to run Docker Video Generation Pipeline on Windows

Write-Host "Docker Video Generation Pipeline - Windows" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Check Docker
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running! Please start Docker Desktop" -ForegroundColor Red
    exit 1
}

# Check OpenAI API Key
if (-not $env:OPENAI_API_KEY) {
    Write-Host "OPENAI_API_KEY is not set!" -ForegroundColor Yellow
    Write-Host "Please set environment variable:" -ForegroundColor Yellow
    Write-Host '$env:OPENAI_API_KEY="your_api_key_here"' -ForegroundColor Cyan
    exit 1
}

Write-Host "OpenAI API Key is set: $($env:OPENAI_API_KEY.Substring(0,10))..." -ForegroundColor Green

# Check subjects.txt file
if (-not (Test-Path "subjects.txt")) {
    Write-Host "subjects.txt file not found!" -ForegroundColor Red
    Write-Host "Please create subjects.txt with video topics" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found subjects.txt file" -ForegroundColor Green

# Create output directory
if (-not (Test-Path "output")) {
    New-Item -ItemType Directory -Path "output" | Out-Null
    Write-Host "Created output directory" -ForegroundColor Green
}

# Build Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
try {
    docker build -t video-generation-pipeline .
    Write-Host "Build successful!" -ForegroundColor Green
} catch {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

# Run container
Write-Host "Running container..." -ForegroundColor Yellow
Write-Host "Mount output directory: $PWD/output -> /app/output" -ForegroundColor Cyan
Write-Host "Mount subjects.txt: $PWD/subjects.txt -> /app/subjects.txt" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Green

try {
    docker run --rm --memory=4g `
        -v "${PWD}/output:/app/output" `
        -v "${PWD}/subjects.txt:/app/subjects.txt" `
        -e OPENAI_API_KEY="$env:OPENAI_API_KEY" `
        video-generation-pipeline
    
    Write-Host "===============================================" -ForegroundColor Green
    Write-Host "Pipeline completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Results:" -ForegroundColor Yellow
    Write-Host "  - Output directory: $PWD/output" -ForegroundColor Cyan
    Write-Host "  - Plan file: $PWD/output/plan.txt" -ForegroundColor Cyan
    Write-Host "  - Video files: $PWD/output/my_result/" -ForegroundColor Cyan
    Write-Host ""
    
    # Show plan.txt if exists
    if (Test-Path "output/plan.txt") {
        Write-Host "Plan.txt content:" -ForegroundColor Yellow
        Write-Host "----------------------------" -ForegroundColor Gray
        Get-Content "output/plan.txt"
        Write-Host "----------------------------" -ForegroundColor Gray
    }
    
    # Show video list
    if (Test-Path "output/my_result") {
        $videos = Get-ChildItem "output/my_result" -Filter "*.mp4"
        if ($videos.Count -gt 0) {
            Write-Host "Generated videos:" -ForegroundColor Yellow
            $videos | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Cyan }
        } else {
            Write-Host "No videos found in my_result/" -ForegroundColor Yellow
        }
    }
    
    Write-Host "Pipeline completed!" -ForegroundColor Green
    
} catch {
    Write-Host "Container run failed!" -ForegroundColor Red
    Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} 