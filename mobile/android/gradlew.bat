@echo off
set DIR=%~dp0
set JAVA_EXE="%JAVA_HOME%\bin\java.exe"
if not exist %JAVA_EXE% set JAVA_EXE=java
%JAVA_EXE% -classpath "%DIR%gradle\wrapper\gradle-wrapper.jar" org.gradle.wrapper.GradleWrapperMain %*
