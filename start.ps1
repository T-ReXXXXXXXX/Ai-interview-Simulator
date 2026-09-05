# AI Interview Simulator - PowerShell Startup Script
Set-Location $PSScriptRoot

# Activate virtual environment
& ".\.venv\Scripts\Activate.ps1"

# Initialize database
Write-Host "Initializing database..." -ForegroundColor Cyan
python init_db.py

# Start Streamlit app
Write-Host "Starting AI Interview Simulator..." -ForegroundColor Green
streamlit run app.py --client.showErrorDetails=false --logger.level=warning
