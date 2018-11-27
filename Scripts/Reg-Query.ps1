'''
I dont know if this one works still.
'''
Function ComputerName
{
    param
    (
        [Parameter(
            Mandatory = $True)]
            [String]$ComputerName
    )
	write-host 'Currently Running command on'$ComputerName 'Searching for' $KeyName
	#$Key=Invoke-command -ComputerName $ComputersName {Get-ItemProperty -Path HKLM:\SOFTWARE\CarbonBlack\config -Name $Using:KeyName | select-object $Using:KeyName } -ErrorVariable ErrMsg 2> $null
	if(!$?)
	{
	$ErrMsg | Add-Content -Path $ErrorLog
	write-host "Failed to connect to"$ComputerName"check File"$ErrorLog 
        $CB_CONN_Error[$ComputerName] = $ErrorLog
	}
    else
    {
	    if ($Key.$KeyName -ne $KeyValue)
	    {
    	    $CB_BAD_RegKey[$ComputerName] = $Key.$KeyName
	    }
	    else
	    {
	    $CB_GOOD_RegKey[$ComputerName] = $Key.$KeyName
	    }
    }
}

Function CB-Reg-Query
{
<#

.SYNOPSIS

Retrieves Carbon Black Client registry keys from Standard in

.Requirements

Active Directory Moudle (Get-ADComputers)
Admin Access to Computers 

.DESCRIPTION

CB-Req-Query extracts Carbon Black Server Registry key information. Writes information to Current Directory.

Key Values to Search
~~~
BootId
ConfigName
CollectStoreFiles
CollectModuleLoads
CollectModuleInfo
CollectFileMods
CollectRegMods
CollectNetConns
CollectProcesses
CollectCrossProcess
CollectEmetEvents
CollectProcessUserContext
CollectDataFileWrites
SensorBackendServer
MaxLicenses
QuotaEventlogPercent
QuotaEventlogBytes
QuotaStorefileBytes
QuotaStorefilePercent
VdiEnabled
TamperLevel
SensorExeName
ProcessFilterLevel
FilterKnownDLLs
EventLogThresholdBytes
EventLogThresholdSeconds
CollectSensorOperations
ProtectionDisabled
SensorId
LogFileDiskQuotaMb
LogFileDiskQuotaPercentage
CbExeName
SuppressProcessNotifications
SuppressKnownDllImageLoads
SensorIpAddr
CbServerCert
SensorClientKey
SensorClientCert
~~~

Author: Casey Parman
License: BSD 3-Clause

.EXAMPLE

Get-ADComputer -Filter * -Properties Name,LastLogonDate -SearchBase "OU" | Where { $_.LastLogonDate -GT (Get-Date).AddDays(-30) } | Select-Object Name | CB-Reg-Query  -KeyValue https://cbresponse.domain.org -KeyName SensorBackendServer 

#Production
$AD_Workstation = Get-ADComputer -Filter * -Properties Name,LastLogonDate -SearchBase $OU | Where { $_.LastLogonDate -GT (Get-Date).AddDays(-30) } | Select-Object Name
#Test
#Get-ADComputer -Filter {Name -eq 'cfg4236' -or Name -eq 'cfg22569' -or Name -eq 'cfg22568'-or Name -eq 'cfg4236-vm3' -or Name -eq 'cfg4236-vm1'  } -Properties Name,LastLogonDate -SearchBase $OU | Where { $_.LastLogonDate -GT (Get-Date).AddDays(-30) } | Select-Object Name
        
#>
 [CmdletBinding()]
    param
    (
        [Parameter(
            Position = 0,
            Mandatory = $True,
            ValueFromPipeline = $True)]
        [String]$Computers,

        [Parameter(
            Mandatory=$False,
            HelpMessage='Enter the key value expected if left blank all results will be in CB_keyBad.csv')]
        [AllowNull()]
        [string]$KeyValue,
                
        [Parameter(
            Mandatory=$True,
            HelpMessage='Enter Key Name to search')]
        [ValidateSet("BootId","ConfigName","CollectStoreFiles","CollectModuleLoads","CollectModuleInfo","CollectFileMods","CollectRegMods","CollectNetConns","CollectProcesses","CollectCrossProcess","CollectEmetEvents","CollectProcessUserContext","CollectDataFileWrites","SensorBackendServer","MaxLicenses","QuotaEventlogPercent","QuotaEventlogBytes","QuotaStorefileBytes","QuotaStorefilePercent","VdiEnabled","TamperLevel","SensorExeName","ProcessFilterLevel","FilterKnownDLLs","EventLogThresholdBytes","EventLogThresholdSeconds","CollectSensorOperations","ProtectionDisabled","SensorId","LogFileDiskQuotaMb","LogFileDiskQuotaPercentage","CbExeName","SuppressProcessNotifications","SuppressKnownDllImageLoads","SensorIpAddr","CbServerCert","SensorClientKey","SensorClientCert")]
        [ValidateNotNull()]
        [ValidateNotNullorEmpty()]
        [string]$KeyName
        
    )
##Error Logging
    Begin {
            $ErrorLog = "Error.log"
            if (Test-Path $ErrorLog) 
            {
                Remove-Item $ErrorLog
            }
           
            if (!$KeyValue)
            { 
                $KeyValue ="" 
            }
    
            $CB_BAD_RegKey = @{}
            $CB_GOOD_RegKey = @{}
            $CB_CONN_Error  = @{}
    }
    Process {
            $Computers | Get-Member -MemberType NoteProperty
            foreach ($Computer in $Computers)
            {
               if($Computer.Name)
               {
               write-host "True Computer=" $Computer
               $ComputerName = $Computer.Name
               write-host "ComputerName=" $Computer.Name
               ComputerName -ComputerName $ComputerName
               }
               else
               {
               $Computer | Get-Member -MemberType NoteProperty
               write-host "False Broken=" $Computer.Name
               write-host "False Computer=" $Computer
               $ComputerName = $Computer
               write-host "ComputerName=" $ComputerName
               ComputerName -ComputerName $ComputerName
               }
                    
            }
            $CB_BAD_RegKey.GetEnumerator() |select-object Key,Value | Export-Csv -NoTypeInformation -Path CB_keyBad.csv
            $CB_GOOD_RegKey.GetEnumerator() | Select-Object key,value| Export-Csv -NoTypeInformation -Path CB_keyGood.csv
            $CB_CONN_Error.GetEnumerator() | Select-Object key,value| Export-Csv -NoTypeInformation -Path CB_ConnError.csv
    }
    End {
    Write-Verbose -Message "End Block"

    }
}
# SIG # Begin signature block
# MIIZMAYJKoZIhvcNAQcCoIIZITCCGR0CAQExCzAJBgUrDgMCGgUAMGkGCisGAQQB
# gjcCAQSgWzBZMDQGCisGAQQBgjcCAR4wJgIDAQAABBAfzDtgWUsITrck0sYpfvNR
# AgEAAgEAAgEAAgEAAgEAMCEwCQYFKw4DAhoFAAQUNstoF2bkpL5QK1GvwSOm08Ld
# 0uWgghQ+MIIEmTCCA4GgAwIBAgIPFojwOSVeY45pFDkH5jMLMA0GCSqGSIb3DQEB
# BQUAMIGVMQswCQYDVQQGEwJVUzELMAkGA1UECBMCVVQxFzAVBgNVBAcTDlNhbHQg
# TGFrZSBDaXR5MR4wHAYDVQQKExVUaGUgVVNFUlRSVVNUIE5ldHdvcmsxITAfBgNV
# BAsTGGh0dHA6Ly93d3cudXNlcnRydXN0LmNvbTEdMBsGA1UEAxMUVVROLVVTRVJG
# aXJzdC1PYmplY3QwHhcNMTUxMjMxMDAwMDAwWhcNMTkwNzA5MTg0MDM2WjCBhDEL
# MAkGA1UEBhMCR0IxGzAZBgNVBAgTEkdyZWF0ZXIgTWFuY2hlc3RlcjEQMA4GA1UE
# BxMHU2FsZm9yZDEaMBgGA1UEChMRQ09NT0RPIENBIExpbWl0ZWQxKjAoBgNVBAMT
# IUNPTU9ETyBTSEEtMSBUaW1lIFN0YW1waW5nIFNpZ25lcjCCASIwDQYJKoZIhvcN
# AQEBBQADggEPADCCAQoCggEBAOnpPd/XNwjJHjiyUlNCbSLxscQGBGue/YJ0UEN9
# xqC7H075AnEmse9D2IOMSPznD5d6muuc3qajDjscRBh1jnilF2n+SRik4rtcTv6O
# KlR6UPDV9syR55l51955lNeWM/4Og74iv2MWLKPdKBuvPavql9LxvwQQ5z1IRf0f
# aGXBf1mZacAiMQxibqdcZQEhsGPEIhgn7ub80gA9Ry6ouIZWXQTcExclbhzfRA8V
# zbfbpVd2Qm8AaIKZ0uPB3vCLlFdM7AiQIiHOIiuYDELmQpOUmJPv/QbZP7xbm1Q8
# ILHuatZHesWrgOkwmt7xpD9VTQoJNIp1KdJprZcPUL/4ygkCAwEAAaOB9DCB8TAf
# BgNVHSMEGDAWgBTa7WR0FJwUPKvdmam9WyhNizzJ2DAdBgNVHQ4EFgQUjmstM2v0
# M6eTsxOapeAK9xI1aogwDgYDVR0PAQH/BAQDAgbAMAwGA1UdEwEB/wQCMAAwFgYD
# VR0lAQH/BAwwCgYIKwYBBQUHAwgwQgYDVR0fBDswOTA3oDWgM4YxaHR0cDovL2Ny
# bC51c2VydHJ1c3QuY29tL1VUTi1VU0VSRmlyc3QtT2JqZWN0LmNybDA1BggrBgEF
# BQcBAQQpMCcwJQYIKwYBBQUHMAGGGWh0dHA6Ly9vY3NwLnVzZXJ0cnVzdC5jb20w
# DQYJKoZIhvcNAQEFBQADggEBALozJEBAjHzbWJ+zYJiy9cAx/usfblD2CuDk5oGt
# Joei3/2z2vRz8wD7KRuJGxU+22tSkyvErDmB1zxnV5o5NuAoCJrjOU+biQl/e8Vh
# f1mJMiUKaq4aPvCiJ6i2w7iH9xYESEE9XNjsn00gMQTZZaHtzWkHUxY93TYCCojr
# QOUGMAu4Fkvc77xVCf/GPhIudrPczkLv+XZX4bcKBUCYWJpdcRaTcYxlgepv84n3
# +3OttOe/2Y5vqgtPJfO44dXddZhogfiqwNGAwsTEOYnB9smebNd0+dmX+E/CmgrN
# Xo/4GengpZ/E8JIh5i15Jcki+cPwOoRXrToW9GOUEB1d0MYwgge8MIIGpKADAgEC
# AhNUAACb+OltQ7t5q8dXAAAAAJv4MA0GCSqGSIb3DQEBCwUAMF0xEzARBgoJkiaJ
# k/IsZAEZFgNvcmcxHDAaBgoJkiaJk/IsZAEZFgxzdG9ybW9udHZhaWwxKDAmBgNV
# BAMTH1N0b3Jtb250IFZhaWwgSGVhbHRoIElzc3VpbmctQ0EwHhcNMTgwNjA0MjA0
# NjIxWhcNMjEwNjAzMjA0NjIxWjBuMRMwEQYKCZImiZPyLGQBGRYDb3JnMRwwGgYK
# CZImiZPyLGQBGRYMc3Rvcm1vbnR2YWlsMQ8wDQYDVQQLDAZfVXNlcnMxEDAOBgNV
# BAsTB0lTIERlcHQxFjAUBgNVBAMTDVBhcm1hbiwgQ2FzZXkwggEiMA0GCSqGSIb3
# DQEBAQUAA4IBDwAwggEKAoIBAQDIULm383HoRoU2V+zQLamQ1ATd8V8wlsaX6BHK
# QivKAcKQdqCvLXK2/C2YyGIN3hYa2+iK+sJrVzxwrUWVE31ABSVhB6bHU1blI4kJ
# aoS+x2+kVhruqAgER1jW7KiUGQ8Rs8dPcQ3FIbqJLARDoujhhXIEH4UMjKvkiogi
# Q8xLxKWc3AFlNt/aTk1v0BjXaL+uzX6xvSsXvF/2UIRUGlQbeA7YysGuD4wr95kI
# E8SW3wRRezsRuUar8lCrV+wPt+HNEJBEdR+UAu23LqmKFsyhV9XJ8brkADUttDWa
# 3jqTAFXbI8QIf7MwunQpw467E67O5KimhO51BzH91Rk+kN8DAgMBAAGjggRiMIIE
# XjAbBgkrBgEEAYI3FQoEDjAMMAoGCCsGAQUFBwMDMDwGCSsGAQQBgjcVBwQvMC0G
# JSsGAQQBgjcVCLeBVofh5gKFyYEEgdb6bYWVrxA/gYOOGoahon8CAWQCAQYwggHQ
# BggrBgEFBQcBAQSCAcIwggG+MIHJBggrBgEFBQcwAoaBvGxkYXA6Ly8vQ049U3Rv
# cm1vbnQlMjBWYWlsJTIwSGVhbHRoJTIwSXNzdWluZy1DQSxDTj1BSUEsQ049UHVi
# bGljJTIwS2V5JTIwU2VydmljZXMsQ049U2VydmljZXMsQ049Q29uZmlndXJhdGlv
# bixEQz1zdG9ybW9udHZhaWwsREM9b3JnP2NBQ2VydGlmaWNhdGU/YmFzZT9vYmpl
# Y3RDbGFzcz1jZXJ0aWZpY2F0aW9uQXV0aG9yaXR5MHcGCCsGAQUFBzAChmtodHRw
# Oi8vcGtpMS5zdG9ybW9udHZhaWwub3JnL0NlcnRFbnJvbGwvU1ZISW50Q0Euc3Rv
# cm1vbnR2YWlsLm9yZ19TdG9ybW9udCUyMFZhaWwlMjBIZWFsdGglMjBJc3N1aW5n
# LUNBLmNydDB3BggrBgEFBQcwAoZraHR0cDovL3BraTIuc3Rvcm1vbnR2YWlsLm9y
# Zy9DZXJ0RW5yb2xsL1NWSEludENBLnN0b3Jtb250dmFpbC5vcmdfU3Rvcm1vbnQl
# MjBWYWlsJTIwSGVhbHRoJTIwSXNzdWluZy1DQS5jcnQwHQYDVR0OBBYEFMiyKVw8
# tSlKhJvxdK6+6G0qNr3cMAsGA1UdDwQEAwIHgDAzBgNVHREELDAqoCgGCisGAQQB
# gjcUAgOgGgwYY3Bhcm1hbkBzdG9ybW9udHZhaWwub3JnMIIBlAYDVR0fBIIBizCC
# AYcwggGDoIIBf6CCAXuGgdJsZGFwOi8vL0NOPVN0b3Jtb250JTIwVmFpbCUyMEhl
# YWx0aCUyMElzc3VpbmctQ0EsQ049U1ZISW50Q0EsQ049Q0RQLENOPVB1YmxpYyUy
# MEtleSUyMFNlcnZpY2VzLENOPVNlcnZpY2VzLENOPUNvbmZpZ3VyYXRpb24sREM9
# c3Rvcm1vbnR2YWlsLERDPW9yZz9jZXJ0aWZpY2F0ZVJldm9jYXRpb25MaXN0P2Jh
# c2U/b2JqZWN0Q2xhc3M9Y1JMRGlzdHJpYnV0aW9uUG9pbnSGUWh0dHA6Ly9wa2kx
# LnN0b3Jtb250dmFpbC5vcmcvQ2VydEVucm9sbC9TdG9ybW9udCUyMFZhaWwlMjBI
# ZWFsdGglMjBJc3N1aW5nLUNBLmNybIZRaHR0cDovL3BraTIuc3Rvcm1vbnR2YWls
# Lm9yZy9DZXJ0RW5yb2xsL1N0b3Jtb250JTIwVmFpbCUyMEhlYWx0aCUyMElzc3Vp
# bmctQ0EuY3JsMB8GA1UdIwQYMBaAFGyqmkKFHYfTJsCX2u/HJX+l3cfjMBMGA1Ud
# JQQMMAoGCCsGAQUFBwMDMA0GCSqGSIb3DQEBCwUAA4IBAQCc/EpgwZOG7W9AlwiH
# v+DIdgDy/rjWeOXwojb2dIXp2oQ/4LwZHkZJ77q28setpqWq2MSwtlwzRalFNwvG
# D2KW+sIn6py2z6uyap6h/cFutR/Ee+o75WqwDd/lMzOhGPQRh7z/QdQhdP6kc5QZ
# ebbJP9PkB3vDfy6fxkePQKRdA00cul1jdeGf/Cf496NE2jfR263rpzwWGPdFAfym
# ytZtSuKwD9gqhdBpFpMKxnv+rui9nv9wjBUBsZdtHSp5qCQZqHJoIqE7uG/XrpfY
# WynHFe0kI1SUGoyE9W/zmPo69i/baOrVydCq7s8khBA8nKbCAvGkY9GcALrXSof7
# /r5/MIIH3TCCBcWgAwIBAgITSQAAAAJp++BorDSytwAAAAAAAjANBgkqhkiG9w0B
# AQsFADAnMSUwIwYDVQQDExxTdG9ybW9udCBWYWlsIEhlYWx0aCBSb290LUNBMB4X
# DTE2MDkyODE2NDAzOVoXDTI2MDkyODE2NTAzOVowXTETMBEGCgmSJomT8ixkARkW
# A29yZzEcMBoGCgmSJomT8ixkARkWDHN0b3Jtb250dmFpbDEoMCYGA1UEAxMfU3Rv
# cm1vbnQgVmFpbCBIZWFsdGggSXNzdWluZy1DQTCCASIwDQYJKoZIhvcNAQEBBQAD
# ggEPADCCAQoCggEBAMnBFZD7CwoGeZpRBSAIwF6YyeHNYsgnfxPNwK2Bgzeof0aH
# ebame+lXFc5UKJaxSaX0Hqeiz3PdkSMnUqQY804ZYjdl5UUe8zefJwb04KzFuVam
# znQ24fRgQodhZ+7yI1AwoKYMUfT+q6wUeq1P+3SxSJo+WOkMhfbR1OvCmvag/0PP
# REvaXnoOajxSgkXaWj9I9PVFlmYHF+Mr39Wh7ctGQAUbjsZ9h+bw6LaWAFFxcKUb
# yvtGQonjenUPwEG2FAXLzwQAMA/RczMc6qKwMLZQBDPCYFEjcfnYlIgwZY7LG1j7
# inOrAtH5bBQI0+pBxG0dJ+UfZt6seKk/mKKjUOsCAwEAAaOCA8owggPGMBAGCSsG
# AQQBgjcVAQQDAgEAMB0GA1UdDgQWBBRsqppChR2H0ybAl9rvxyV/pd3H4zAZBgkr
# BgEEAYI3FAIEDB4KAFMAdQBiAEMAQTALBgNVHQ8EBAMCAYYwDwYDVR0TAQH/BAUw
# AwEB/zAfBgNVHSMEGDAWgBTV3ctbn2IL3S04gc+ultzYecVmkTCCAYwGA1UdHwSC
# AYMwggF/MIIBe6CCAXegggFzhoHQbGRhcDovLy9DTj1TdG9ybW9udCUyMFZhaWwl
# MjBIZWFsdGglMjBSb290LUNBLENOPVNWSFJvb3RDQSxDTj1DRFAsQ049UHVibGlj
# JTIwS2V5JTIwU2VydmljZXMsQ049U2VydmljZXMsQ049Q29uZmlndXJhdGlvbixE
# Qz1zdG9ybW9udHZhaWwsREM9b3JnP2NlcnRpZmljYXRlUmV2b2NhdGlvbkxpc3Q/
# YmFzZT9vYmplY3RDbGFzcz1jUkxEaXN0cmlidXRpb25Qb2ludIZOaHR0cDovL3Br
# aTEuc3Rvcm1vbnR2YWlsLm9yZy9DZXJ0RW5yb2xsL1N0b3Jtb250JTIwVmFpbCUy
# MEhlYWx0aCUyMFJvb3QtQ0EuY3Jshk5odHRwOi8vcGtpMi5zdG9ybW9udHZhaWwu
# b3JnL0NlcnRFbnJvbGwvU3Rvcm1vbnQlMjBWYWlsJTIwSGVhbHRoJTIwUm9vdC1D
# QS5jcmwwggGnBggrBgEFBQcBAQSCAZkwggGVMIHGBggrBgEFBQcwAoaBuWxkYXA6
# Ly8vQ049U3Rvcm1vbnQlMjBWYWlsJTIwSGVhbHRoJTIwUm9vdC1DQSxDTj1BSUEs
# Q049UHVibGljJTIwS2V5JTIwU2VydmljZXMsQ049U2VydmljZXMsQ049Q29uZmln
# dXJhdGlvbixEQz1zdG9ybW9udHZhaWwsREM9b3JnP2NBQ2VydGlmaWNhdGU/YmFz
# ZT9vYmplY3RDbGFzcz1jZXJ0aWZpY2F0aW9uQXV0aG9yaXR5MGQGCCsGAQUFBzAC
# hlhodHRwOi8vcGtpMS5zdG9ybW9udHZhaWwub3JnL0NlcnRFbnJvbGwvU1ZIUm9v
# dENBX1N0b3Jtb250JTIwVmFpbCUyMEhlYWx0aCUyMFJvb3QtQ0EuY3J0MGQGCCsG
# AQUFBzAChlhodHRwOi8vcGtpMi5zdG9ybW9udHZhaWwub3JnL0NlcnRFbnJvbGwv
# U1ZIUm9vdENBX1N0b3Jtb250JTIwVmFpbCUyMEhlYWx0aCUyMFJvb3QtQ0EuY3J0
# MA0GCSqGSIb3DQEBCwUAA4ICAQCFv4HGzhDOohKRr3Ca2AqNnc0WZ3ETG+aNUcnG
# 6pjJhjc7XAbfH8QxLqk44y3P1+zX0cbzW6haTBbwHs6QRvktVx/rFZnMvow6QmP3
# 2/wYlhKoe/cEpa2o7UMBlQdVjlb89Zbuj+QWlqJqOUaSWle+dp8YX7wHhUlsEX2g
# yAdDknLBobSZxlbv1B/aHXZeMKExb1JydSCsmw0a236rV5p2sW7eXy4I91CJBjR9
# igIEjhLXeGa6NXHTfqISTajGXL5awBcROoRNXW9CcrzkWBxzLtX5i9vC31QE1kXc
# T6kf0DQQsvBeVbEKJGsYmdsgKG7FhgtkqIyfcW3fbjS5vGJb8XknY7I/i66rD6NW
# ldPsKg6flrHMTvX/1r+bEoigtD533iS0ILDtSaqsIh4MJi5l2N72mc2DYt5iSlVk
# fiPt/TYe4Lw6/K6iZ3GsXRwur8I0gTljJikNpPoUiFxbJmFc5TGqTn5LBQ7P2KkO
# lb9ofEGsV3Z5gIY3aElGW5vCVxfvNzwwQxRaLZHEpJv73VmhH+eLtb9SN2nj/fMU
# KGKRA9Jg0arsT2DZW0XMhyABii4bK2edszybDf/qw2mPqOjXd/E5yUG9UHXUHujL
# sfQgl84t7c03yGDpA3SiwWZ1+NVzqCXCnF0cO3GjgR3JjzAiKjLe11pSOeMEeNWG
# hl/QIDGCBFwwggRYAgEBMHQwXTETMBEGCgmSJomT8ixkARkWA29yZzEcMBoGCgmS
# JomT8ixkARkWDHN0b3Jtb250dmFpbDEoMCYGA1UEAxMfU3Rvcm1vbnQgVmFpbCBI
# ZWFsdGggSXNzdWluZy1DQQITVAAAm/jpbUO7eavHVwAAAACb+DAJBgUrDgMCGgUA
# oHgwGAYKKwYBBAGCNwIBDDEKMAigAoAAoQKAADAZBgkqhkiG9w0BCQMxDAYKKwYB
# BAGCNwIBBDAcBgorBgEEAYI3AgELMQ4wDAYKKwYBBAGCNwIBFTAjBgkqhkiG9w0B
# CQQxFgQUXP8jx9DlVD2yClrP2iNcV8XHO6wwDQYJKoZIhvcNAQEBBQAEggEAaTwd
# AzIBFe3ecmO4WuEMIcW5a1oGmx0tW8Gkob0kSqHK7kludgFkj4ZHJDYtZ4kQrRDU
# UJhSyan+pImFd4HQz2NyZSQO7LSN4pCffUu1DJL2Hd0iiXTVJIiD0wtsevn+oAPk
# Kv+BugSOLuwwmNET+IMQDGIhtoJ635WnF3LDjSix6YM2BKEWQXU42sITfg0DP2+J
# V+OIA4ftMgQDKjyHc8/jGjFzCPl5Qa4w36GUytjPRLTi2oMtuFWIYFPRLIgan2dR
# JpkRPSMGs53cblS6AlIHpkwzaTT1Nkyu6zV2gI49/I+KEd8ny24/3RPtEDWiDxrb
# fZ5VBu3UDpLOlIzyeKGCAkMwggI/BgkqhkiG9w0BCQYxggIwMIICLAIBATCBqTCB
# lTELMAkGA1UEBhMCVVMxCzAJBgNVBAgTAlVUMRcwFQYDVQQHEw5TYWx0IExha2Ug
# Q2l0eTEeMBwGA1UEChMVVGhlIFVTRVJUUlVTVCBOZXR3b3JrMSEwHwYDVQQLExho
# dHRwOi8vd3d3LnVzZXJ0cnVzdC5jb20xHTAbBgNVBAMTFFVUTi1VU0VSRmlyc3Qt
# T2JqZWN0Ag8WiPA5JV5jjmkUOQfmMwswCQYFKw4DAhoFAKBdMBgGCSqGSIb3DQEJ
# AzELBgkqhkiG9w0BBwEwHAYJKoZIhvcNAQkFMQ8XDTE4MDcxNjE1NTc0OFowIwYJ
# KoZIhvcNAQkEMRYEFPGJpINhaX+d4a8ENsGWFZmI8mmVMA0GCSqGSIb3DQEBAQUA
# BIIBAN5ECeOQQNiZMfevdA64p3xvByZQXOuT4GBTrISJDCJIlKV3rFsd1hKj9Fu9
# u8qDLhNxd+Z9FsB12lpqMgl3B7lkC070GWlyeK5u0OnVzHurXSYsHPbSKKi07RPu
# EfmIvRY2nOFvcB2uMhxp1GIHio8u4FDtPO1NGZD7akq6vm8QkIyiKhn/9SgvLYzO
# Gb/BxGTGtDXVjBtrwlF7BakknGA3yZ0GPrWdcnpCtv3LbzpxpUTc4vDJq7ikkbNS
# zOoRk3FxkYlemUgjZCHudLeKYkuJdZ8WyLDduF0uCWAYLaBGAFcm55MRQmtIGfIL
# KwPebkbFqznfHic2tygf94uK3RQ=
# SIG # End signature block
