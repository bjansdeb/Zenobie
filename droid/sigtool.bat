@echo off
REM Infer DROID_HOME from script location
SET DROID_HOME=%~dp0

"%DROID_HOME%/jre/bin/java" -jar droid-tools-6.8.1.jar %*
