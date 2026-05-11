@echo off
REM Windows 打包脚本 — 将 ipd-cadtool-agent 打包为独立可执行文件
pip install pyinstaller
pyinstaller --name ipd-cadtool-agent --add-data "ipd_cadtool_agent;ipd_cadtool_agent" --onedir --clean --noconfirm ipd_cadtool_agent/main.py
echo 打包完成: dist\ipd-cadtool-agent\ipd-cadtool-agent.exe
pause
