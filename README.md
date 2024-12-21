# PowerShell via System.Management.Automation.dll

## Overview
This project explores the capabilities of `System.Management.Automation.dll`, a critical Windows API library developed by Microsoft for PowerShell script management and execution and *not use* the powershell.exe or powershell_ise.exe

### Potential Evasion Techniques
- Run PowerShell scripts without traditional binaries
- Potential to bypass standard EDR/XDR detection mechanisms
- Demonstrated effectiveness against certain security solutions

### 1. Script Execution
- Run PowerShell scripts as executable files
- Direct command execution within scripts
- Access to built-in PowerShell cmdlets

### 2. System Interaction
- Process management
- Security settings configuration

### 3. .NET Framework Integration
- Tight integration with .NET Framework
- Enables use of .NET languages within PowerShell scripts

## Technical Details
**Default Path:**
```
C:\WINDOWS\Microsoft.Net\assembly\GAC_MSIL\System.Management.Automation\v4.0_3.0.0.0__31bf3856ad364e35\System.Management.Automation.dll
```
Historically downloadable from NuGet Package repositories

##  Research

### MITRE ATT&CK Mapping
Technique: [T1059 - Command and Scripting Interpreter](https://attack.mitre.org/techniques/T1059/)



## Proof of Concept

### Python Integration
- Utilize `clr` library for DLL loading
- Enable cross-language scripting and automation

## 🚨 Responsible Use Warning 🚨
**This research is strictly for educational purposes. Ensure compliance with legal and ethical standards. Do not use these techniques for malicious purposes.**

## Screenshots
<div>
        <img src="https://github.com/idanless/Powershell_Hide/blob/main/PsGui.jpg?raw=true" alt=" Screenshot" style="max-width: 100%; height: auto; display: block; margin: 20px 0;" />
    </div>
