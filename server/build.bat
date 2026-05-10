@echo off
REM Windows 打包脚本 — 将 ipd-emcad-agent 打包为独立可执行文件
pip install pyinstaller
pyinstaller --name ipd-emcad-agent --add-data "ipd_emcad_agent;ipd_emcad_agent" --onedir --clean --noconfirm ipd_emcad_agent/main.py
echo 打包完成: dist\ipd-emcad-agent\ipd-emcad-agent.exe
pause
