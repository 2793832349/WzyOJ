# WzyOJ 本地开发环境启动脚本（Windows）
# 用法: .\start-dev-windows.ps1

$ErrorActionPreference = "Stop"

$BLUE = "[94m"
$GREEN = "[92m"
$YELLOW = "[93m"
$RED = "[91m"
$RESET = "[0m"

function Print-Step {
    Write-Host "${BLUE}==== $args ====${RESET}" -ForegroundColor Cyan
}

function Print-Success {
    Write-Host "${GREEN}✓ $args${RESET}" -ForegroundColor Green
}

function Print-Warning {
    Write-Host "${YELLOW}⚠ $args${RESET}" -ForegroundColor Yellow
}

function Print-Error {
    Write-Host "${RED}✗ $args${RESET}" -ForegroundColor Red
}

# 项目根目录
$PROJECT_ROOT = "d:\Users\why\Downloads\WzyOJ"
$BACKEND_DIR = "$PROJECT_ROOT\backend"
$FRONTEND_DIR = "$PROJECT_ROOT\frontend-naive"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        WzyOJ 本地开发环境启动 (Windows)                   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 检查目录是否存在
Print-Step "检查项目结构"

if (-not (Test-Path $BACKEND_DIR)) {
    Print-Error "Backend 目录不存在: $BACKEND_DIR"
    exit 1
}
Print-Success "Backend 目录存在: $BACKEND_DIR"

if (-not (Test-Path $FRONTEND_DIR)) {
    Print-Error "Frontend 目录不存在: $FRONTEND_DIR"
    exit 1
}
Print-Success "Frontend 目录存在: $FRONTEND_DIR"

Write-Host ""

# 检查 Python
Print-Step "检查 Python 环境"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Print-Error "Python 未安装或不在 PATH 中"
    exit 1
}

$PYTHON_VERSION = python --version 2>&1
Print-Success "$PYTHON_VERSION"

Write-Host ""

# 检查 Node.js
Print-Step "检查 Node.js 环境"

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Print-Warning "Node.js 未安装，前端服务将无法启动"
} else {
    $NODE_VERSION = node --version
    Print-Success "Node.js $NODE_VERSION"
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Print-Warning "npm 未安装，前端依赖无法安装"
} else {
    $NPM_VERSION = npm --version
    Print-Success "npm $NPM_VERSION"
}

Write-Host ""

# 安装 Backend 依赖
Print-Step "安装 Backend 依赖"

Push-Location $BACKEND_DIR

if (-not (Test-Path "requirements.txt")) {
    Print-Error "找不到 requirements.txt"
    Pop-Location
    exit 1
}

Write-Host "正在安装 Python 依赖...（可能需要 2-5 分钟）" -ForegroundColor Yellow
Write-Host ""

try {
    python -m pip install -q --upgrade pip setuptools wheel 2>&1 | Out-Null
    Print-Success "pip 已升级"
    
    python -m pip install -r requirements.txt -q --upgrade 2>&1 | Out-Null
    Print-Success "Django 依赖已安装"
    
    # 验证 Django
    python -c "import django; print(django.VERSION)" | Out-Null
    Print-Success "Django 验证通过"
    
} catch {
    Print-Error "依赖安装失败: $_"
    Pop-Location
    exit 1
}

Pop-Location

Write-Host ""

# 检查或创建数据库
Print-Step "检查数据库"

Push-Location $BACKEND_DIR

if (Test-Path "db.sqlite3") {
    Print-Success "SQLite 数据库已存在"
} else {
    Print-Warning "SQLite 数据库不存在，执行迁移..."
    
    try {
        python manage.py makemigrations -q 2>&1 | Out-Null
        python manage.py migrate -q 2>&1 | Out-Null
        Print-Success "数据库迁移完成"
    } catch {
        Print-Error "数据库迁移失败: $_"
        Pop-Location
        exit 1
    }
}

Pop-Location

Write-Host ""

# 安装 Frontend 依赖
Print-Step "安装 Frontend 依赖"

if (Get-Command node -ErrorAction SilentlyContinue) {
    Push-Location $FRONTEND_DIR
    
    if (Test-Path "package.json") {
        Write-Host "正在安装 npm 依赖...（可能需要 1-2 分钟）" -ForegroundColor Yellow
        Write-Host ""
        
        try {
            npm install 2>&1 | Out-Null
            Print-Success "npm 依赖已安装"
        } catch {
            Print-Warning "npm 依赖安装失败，但不影响后端运行"
        }
    }
    
    Pop-Location
} else {
    Print-Warning "跳过 Frontend 依赖安装（Node.js 未安装）"
}

Write-Host ""

# 启动服务
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              准备启动开发服务器                          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "选择启动方式 (1=后端+前端, 2=仅后端, 3=仅前端, 其他=退出)"

switch ($choice) {
    "1" {
        Write-Host ""
        Print-Step "启动后端和前端服务"
        Write-Host ""
        
        Write-Host "后端服务: http://localhost:8000" -ForegroundColor Green
        Write-Host "前端服务: http://localhost:5173" -ForegroundColor Green
        Write-Host "API 文档: http://localhost:8000/api/" -ForegroundColor Green
        Write-Host ""
        Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
        Write-Host ""
        
        # 启动后端（后台）
        $BACKEND_PROCESS = Start-Process -WindowStyle Normal `
            -FilePath "powershell" `
            -ArgumentList "-NoExit", "-Command", `
            "cd '$BACKEND_DIR'; python manage.py runserver 0.0.0.0:8000" `
            -PassThru
        
        Print-Success "后端服务已启动 (PID: $($BACKEND_PROCESS.Id))"
        
        Start-Sleep -Seconds 3
        
        # 启动前端
        if (Get-Command node -ErrorAction SilentlyContinue) {
            $FRONTEND_PROCESS = Start-Process -WindowStyle Normal `
                -FilePath "powershell" `
                -ArgumentList "-NoExit", "-Command", `
                "cd '$FRONTEND_DIR'; npm run dev" `
                -PassThru
            
            Print-Success "前端服务已启动 (PID: $($FRONTEND_PROCESS.Id))"
        }
        
        Write-Host ""
        Write-Host "服务已启动！" -ForegroundColor Green
        Write-Host "请在浏览器中访问: http://localhost:5173" -ForegroundColor Cyan
    }
    
    "2" {
        Write-Host ""
        Print-Step "启动后端服务（仅后端）"
        Write-Host ""
        
        Write-Host "API: http://localhost:8000" -ForegroundColor Green
        Write-Host "API 文档: http://localhost:8000/api/" -ForegroundColor Green
        Write-Host ""
        
        Push-Location $BACKEND_DIR
        python manage.py runserver 0.0.0.0:8000
        Pop-Location
    }
    
    "3" {
        if (Get-Command node -ErrorAction SilentlyContinue) {
            Write-Host ""
            Print-Step "启动前端服务（仅前端）"
            Write-Host ""
            
            Write-Host "前端: http://localhost:5173" -ForegroundColor Green
            Write-Host ""
            
            Push-Location $FRONTEND_DIR
            npm run dev
            Pop-Location
        } else {
            Print-Error "Node.js 未安装，无法启动前端服务"
        }
    }
    
    default {
        Print-Warning "已取消启动"
        exit 0
    }
}
