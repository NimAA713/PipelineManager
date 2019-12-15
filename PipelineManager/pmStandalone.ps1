function V2{
    $scriptPath = split-path -parent $MyInvocation.MyCommand.Definition
    mayapy $scriptPath/pmStandalone.py
}

function V5{
    mayapy $PSScriptRoot/pmStandalone.py
}

Switch ($PSVersionTable.PSVersion.Major){
    2{V2} # win 7
    3{V5} # win 8
    4{V5} # win 8.1
    5{V5} # win 10
}
