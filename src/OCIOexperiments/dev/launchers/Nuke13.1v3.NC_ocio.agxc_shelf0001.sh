# launcher for NukeX non commercial

export NUKE_PATH="Z:\dccs\nuke\library\shelf0001"

OCIO="$PWD\..\data\configs\AgXc-v0.1.4\config.ocio"
export OCIO=$(realpath $OCIO)
echo $OCIO

"C:\Program Files\Nuke13.1v3\Nuke13.1.exe" --nukex --nc