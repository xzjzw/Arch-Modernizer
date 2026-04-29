@echo off
REM Arch-Modernizer Demo 运行脚本 (Windows)

echo ==========================================
echo Arch-Modernizer Agent Demo
echo ==========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)
echo ✓ Python 已安装

REM 创建示例代码库
echo.
echo 创建示例遗留代码库...
if not exist demo_legacy_codebase mkdir demo_legacy_codebase
if not exist demo_legacy_codebase\src mkdir demo_legacy_codebase\src
if not exist demo_legacy_codebase\src\controllers mkdir demo_legacy_codebase\src\controllers
if not exist demo_legacy_codebase\src\utils mkdir demo_legacy_codebase\src\utils

REM 创建示例文件
echo // Legacy AngularJS Controller > demo_legacy_codebase\src\controllers\main-controller.js
echo angular.module('app').controller('MainController', function($scope, $http, $q) { >> demo_legacy_codebase\src\controllers\main-controller.js
echo     $scope.users = []; >> demo_legacy_codebase\src\controllers\main-controller.js
echo     $scope.fetchUsers = function() { >> demo_legacy_codebase\src\controllers\main-controller.js
echo         $http.get('/api/users').then(function(response) { >> demo_legacy_codebase\src\controllers\main-controller.js
echo             $scope.users = response.data; >> demo_legacy_codebase\src\controllers\main-controller.js
echo         }); >> demo_legacy_codebase\src\controllers\main-controller.js
echo     }; >> demo_legacy_codebase\src\controllers\main-controller.js
echo }); >> demo_legacy_codebase\src\controllers\main-controller.js

echo // Legacy Utils > demo_legacy_codebase\src\utils\helpers.js
echo function formatDate(date) { >> demo_legacy_codebase\src\utils\helpers.js
echo     if (!date) return ''; >> demo_legacy_codebase\src\utils\helpers.js
echo     return new Date(date).toISOString().split('T')[0]; >> demo_legacy_codebase\src\utils\helpers.js
echo } >> demo_legacy_codebase\src\utils\helpers.js

echo ✓ 已创建示例代码库

REM 运行 Agent
echo.
echo 启动 Arch-Modernizer Agent...
echo ----------------------------------------
python agent_demo.py

echo.
echo ==========================================
echo Demo 运行完成！
echo ==========================================
pause