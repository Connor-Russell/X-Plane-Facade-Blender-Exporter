#Define paths
$cd = Get-Location
$TestDir = "$cd\Tests"
$OutputTestDir = "$cd\Tests\WorkingDir"
$DateAndTime = Get-Date -Format "yyyy-MM-dd HH-mm-ss"

#Define Blender version locations
$BlenderExe29 = "D:\Blender Versions\2.93\blender.exe"
$BlenderExe30 = "D:\Blender Versions\3.01\blender.exe"
$BlenderExe31 = "A:\Software\Blender 3.1\blender.exe"
$BlenderExe32 = "D:\Blender Versions\3.22\blender.exe"
$BlenderExe33 = "D:\Blender Versions\3.39\blender.exe"
$BlenderExe34 = "D:\Blender Versions\3.41\blender.exe"
$BlenderExe35 = "D:\Blender Versions\3.51\blender.exe"
$BlenderExe36 = "D:\Blender Versions\3.69\blender.exe"
$BlenderExe40 = "D:\Blender Versions\4.02\blender.exe"
$BlenderExe41 = "D:\Blender Versions\4.11\blender.exe"
$BlenderExe42 = "D:\Blender Versions\4.23\blender.exe"

#Define functions to individual tests

#Exporter function. Opens Blender, runs the export script and compares the results
function Test-Exporter {
    param (
        [string]$BlenderExe
    )

    #Remove the old exported .fac
    Remove-Item "$OutputTestDir\Exporter.fac" -ErrorAction SilentlyContinue

    #Launch Blender and run the export and compare test
    & $BlenderExe --background --python "$TestDir\Exporter.py" --test-dir $OutputTestDir

    #Remove the old exported .fac
    Remove-Item "$OutputTestDir\Exporter.fac" -ErrorAction SilentlyContinue
}

#Remove the old result file
Remove-Item "$OutputTestDir\Test Results.csv" -ErrorAction SilentlyContinue

#Creat the new results file, starting with the text "Test Name,Result"
Add-Content "$OutputTestDir\Test Results.csv" "$DateAndTime`nTest Name,Result"

#Run the tests

#2.9 Tests
Add-Content "$OutputTestDir\Test Results.csv" "2.9 Tests"
Test-Exporter -BlenderExe $BlenderExe29

#3.0 Tests
Add-Content "$OutputTestDir\Test Results.csv" "3.0 Tests"
Test-Exporter -BlenderExe $BlenderExe30

#3.1 Tests
Add-Content "$OutputTestDir\Test Results.csv" "3.1 Tests"
Test-Exporter -BlenderExe $BlenderExe31

#3.2 Tests
Add-Content "$OutputTestDir\Test Results.csv" "3.2 Tests"
Test-Exporter -BlenderExe $BlenderExe32

#3.3 Tests
Add-Content "$OutputTestDir\Test Results.csv" "3.3 Tests"
Test-Exporter -BlenderExe $BlenderExe33

#3.4 Tests
Add-Content "$OutputTestDir\Test Results.csv" "3.4 Tests"
Test-Exporter -BlenderExe $BlenderExe34

#3.5 Tests
Add-Content "$OutputTestDir\Test Results.csv" "3.5 Tests"
Test-Exporter -BlenderExe $BlenderExe35

#3.6 Tests
Add-Content "$OutputTestDir\Test Results.csv" "3.6 Tests"
Test-Exporter -BlenderExe $BlenderExe36

#4.0 Tests
Add-Content "$OutputTestDir\Test Results.csv" "4.0 Tests"
Test-Exporter -BlenderExe $BlenderExe40

#4.1 Tests
Add-Content "$OutputTestDir\Test Results.csv" "4.1 Tests"
Test-Exporter -BlenderExe $BlenderExe41

#4.2 Tests
Add-Content "$OutputTestDir\Test Results.csv" "4.2 Tests"
Test-Exporter -BlenderExe $BlenderExe42
