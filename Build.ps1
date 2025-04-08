
#Define a function to copy the files from the Source directory to the Blender directory
function Copy-Files {
    param (
        [string]$SourcePath,
        [string]$BlenderPath
    )

    $Files = Get-ChildItem -Path $SourcePath -Recurse

    foreach ($CurFile in $Files) {
        $RelativePath = $CurFile.FullName.Replace($SourcePath, "")
        $DestinationPath = $BlenderPath + $RelativePath

        $DestinationDirectory = Split-Path $DestinationPath
        if (!(Test-Path $DestinationDirectory)) {
            New-Item -Path $DestinationDirectory -ItemType Directory -Force
        }

        # Remove the file if it already exists
        if (Test-Path $DestinationPath) {
            Remove-Item -Path $DestinationPath -Force -Recurse
        }

        Copy-Item -Path $CurFile.FullName -Destination $DestinationPath -Force

        Write-Host "Copied $RelativePath to $DestinationPath"
    }
}

#Define paths
$cd = Get-Location
$appData = $env:APPDATA
$SourcePath = "$cd\Source" #Change this to your repository path
$BlenderPath = "$appData\Blender Foundation\Blender\3.6\scripts\addons"   #Change this to your Blender directory. MAKE A BACKUP OF OLDER VERSIONS OF THIS ADDON FIRST!
$BlenderTestingAddonPath = "D:\Blender Versions\scripts\addons"

#Copy the files from the Source directory to the Blender directory
Copy-Files -SourcePath $SourcePath -BlenderPath $BlenderPath

#Copy the files from the Source directory to the BlenderTestingAddon directory
#Copy-Files -SourcePath $SourcePath -BlenderPath $BlenderTestingAddonPath

