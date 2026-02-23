# 故障排除指南

## 虚拟环境相关

### 问题: "Permission denied: python.exe"

**错误信息**:
```
Error: [Errno 13] Permission denied: '...\\venv\\Scripts\\python.exe'
```

**原因**: 虚拟环境文件被锁定或权限不足

**解决方案**:

#### 方法 1: 删除现有虚拟环境
```powershell
# 关闭所有 Python 进程和 PowerShell 窗口
# 然后删除 venv 文件夹
Remove-Item -Recurse -Force venv

# 重新运行 setup
.\setup.bat
```

#### 方法 2: 以管理员身份运行
- 右键点击 PowerShell
- 选择"以管理员身份运行"
- 再次运行 `.\setup.bat`

#### 方法 3: 使用 setup.bat 的选项
- `setup.bat` 现在会自动检测到已存在的虚拟环境
- 会询问是否删除并重新创建
- 选择 `Y` 删除现有虚拟环境

### 问题: 虚拟环境已存在但无法激活

**错误信息**:
```
[错误] 虚拟环境不存在，请先运行 setup.bat
```

**解决方案**:
```powershell
# 检查虚拟环境是否存在
Test-Path venv\Scripts\activate.bat

# 如果存在但无法激活，删除并重新创建
Remove-Item -Recurse -Force venv
.\setup.bat
```

## 权限相关

### 问题: "Access is denied"

**原因**: 文件或文件夹权限不足

**解决方案**:
```powershell
# 检查文件夹权限
Get-Acl venv

# 以管理员身份运行 PowerShell
# 右键点击 PowerShell -> 以管理员身份运行
```

## 网络相关

### 问题: 依赖安装失败

**错误信息**:
```
Could not find a version that satisfies the requirement...
```

**解决方案**:
```powershell
# 1. 升级 pip
python -m pip install --upgrade pip

# 2. 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 清理缓存
pip cache purge
```

## API 相关

### 问题: "未找到 .env 文件"

**错误信息**:
```
[提示] 未检测到 API 配置，将使用基础模式
```

**这不是错误**，这是正常的提示。系统会自动使用基础模式。

**如果需要使用 AI 增强**:
```powershell
# 1. 复制环境变量模板
copy .env.example .env

# 2. 使用文本编辑器打开 .env 文件
notepad .env

# 3. 填入你的 API 密钥
# 保存文件
```

## 服务启动相关

### 问题: "rasa: command not found"

**原因**: 虚拟环境未激活

**解决方案**:
```powershell
# 确保已激活虚拟环境
venv\Scripts\activate

# 再次运行
rasa train
```

### 问题: 端口已被占用

**错误信息**:
```
Address already in use
```

**解决方案**:
```powershell
# 查找占用端口的进程
netstat -ano | findstr :5005

# 结束进程
taskkill /PID <进程ID> /F

# 或修改端口
rasa run --port 5006
```

## 常见命令问题

### 问题: PowerShell 中无法执行 .bat 文件

**错误信息**:
```
无法将"xxx.bat"项识别为 cmdlet、函数、脚本文件
```

**解决方案**:
```powershell
# 添加 .\ 前缀
.\setup.bat
.\start.bat
.\stop.bat
.\update_kb.bat
```

## 数据库/文件问题

### 问题: FAQ 文件不存在

**错误信息**:
```
[提示] FAQ 尚未构建
```

**解决方案**:
```powershell
# 构建基础版 FAQ（不需要 API）
python scripts\build_faq_enhanced.py --no-enhance

# 或者构建增强版 FAQ（需要配置 .env）
python scripts\build_faq_enhanced.py
```

### 问题: confluence_html 文件夹为空

**解决方案**:
```powershell
# 检查文件夹是否存在
Test-Path confluence_html

# 创建文件夹
mkdir confluence_html

# 手动将 HTML 文件复制到文件夹
```

## 完全重置

如果遇到无法解决的问题，可以尝试完全重置项目：

```powershell
# 1. 停止所有服务
.\stop.bat

# 2. 删除虚拟环境
Remove-Item -Recurse -Force venv

# 3. 删除生成的数据文件
Remove-Item -Recurse -Force data
Remove-Item -Recurse -Force models

# 4. 重新初始化
.\setup.bat
```

## 获取帮助

如果以上方法都无法解决问题：

1. 查看日志文件（如果有）
2. 检查 Python 版本: `python --version`
3. 检查 pip 版本: `pip --version`
4. 查看 `REQUIREMENTS.md` 了解系统要求
5. 查看 `QUICKSTART.md` 获取详细指南

## 日志和调试

### 启用详细日志

```powershell
# Rasa 详细日志
rasa run --verbose

# 查看 Python 错误详情
$ErrorActionPreference = "Continue"
```

### 常用调试命令

```powershell
# 检查 Python 版本
python --version

# 检查已安装的包
pip list

# 检查 Rasa 版本
rasa --version

# 检查虚拟环境
Get-ChildItem venv\Scripts
```
