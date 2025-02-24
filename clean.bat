@echo off
echo Cleaning build directories...

if exist build (
    rmdir /s /q build
    echo Removed build directory
)

if exist dist (
    rmdir /s /q dist
    echo Removed dist directory
)

if exist transient_absorption_analyser.egg-info (
    rmdir /s /q transient_absorption_analyser.egg-info
    echo Removed egg-info directory
)

echo Cleanup complete! 