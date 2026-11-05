@echo off
title Servidor Local - Rotina e Estudos Mobile
echo ==============================================================================
echo    INICIANDO SERVIDOR LOCAL PARA ACESSO NO CELULAR
echo ==============================================================================
echo.
echo No navegador do seu celular (conectado no mesmo Wi-Fi), acesse:
echo.
echo    http://192.168.0.110:8080/rotina_mobile.html
echo.
echo Dica: No iPhone (Safari), toque em Compartilhar -^> "Adicionar a Tela de Inicio"
echo       No Android (Chrome), toque no menu -^> "Adicionar a tela inicial"
echo.
echo Pressione Ctrl+C para encerrar o servidor quando terminar.
echo ==============================================================================
echo.
python -m http.server 8080

