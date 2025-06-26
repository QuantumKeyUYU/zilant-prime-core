[Setup]
AppName=Zilant Prime
AppVersion=0.9.9-rc1
DefaultDirName={pf}\Zilant
DisableProgramGroupPage=yes
OutputDir=..
OutputBaseFilename=ZilantSetup

[Files]
Source: "..\dist\*"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Zilant"; Filename: "{app}\zilant.exe"
