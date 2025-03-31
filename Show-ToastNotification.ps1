<#
.SYNOPSIS
    Sends a Windows Toast Notification using PowerShell.
.DESCRIPTION
    This script sends a toast notification with text and optionally an image. 
    It supports multiple template types and allows specifying a duration. 
    Additionally, it supports user-supplied XML document.
.PARAMETER templateType
    Specifies the toast template type. Valid templates are as follows:
        - ToastText01 (one line of text only)
        - ToastText02 (two lines of text)
        - ToastText03 (two lines of text)
        - ToastText04 (three lines of text)
        - ToastImageAndText01 (image icon and one line of text only)
        - ToastImageAndText02 (image icon and two lines of text)
        - ToastImageAndText03 (image icon and two lines of text)
        - ToastImageAndText04 (image icon and three lines of text)    
    If not supplied, -fromXml is required.
.PARAMETER text1
    Primary text to be displayed in the notification.
.PARAMETER text2
    Secondary text to be displayed. May not be supported by some templates.
.PARAMETER text3
    Tertiary text to be displayed. May not be supported by some templates.
.PARAMETER imagePath
    Absolute path to an image for ImageAndText templates. 
    Only applicable for templates that support images.
.PARAMETER durationLong
    (Optional) Sets the duration of the notification to long (25 seconds) when this flag is provided. 
.PARAMETER fromXml
    (Required if templateType is not supplied) The entire XML document as a string or a file path to an XML file. 
    Other parameters are ignored when this is provided.
.OUTPUTS
    None. (Toast notification is displayed to the user)
.EXAMPLE
    .\Show-ToastNotification.ps1 -templateType "ToastText02" -text1 "Hello" -text2 "This is a notification" -durationLong
.EXAMPLE
    .\Show-ToastNotification.ps1 -fromXml "C:\path\to\toast.xml"
.EXAMPLE
    .\Show-ToastNotification.ps1 -fromXml "<toast><visual><binding template='ToastGeneric'><text>Hello</text></binding></visual></toast>"
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory=$false)]
    [string]$templateType = "",  # Defaults to empty; if not supplied, -fromXml is required

    [Parameter(Mandatory=$false)]
    [string]$text1,

    [Parameter(Mandatory=$false)]
    [string]$text2,

    [Parameter(Mandatory=$false)]
    [string]$text3,

    [Parameter(Mandatory=$false)]
    [string]$imagePath,

    [Parameter(Mandatory=$false)]
    [switch]$durationLong,    

    [Parameter(Mandatory=$false)]
    [string]$fromXml  # Required if templateType is not supplied
)

# Ensure templateType and fromXml are mutually exclusive
if (-not [string]::IsNullOrEmpty($templateType) -and -not [string]::IsNullOrEmpty($fromXml)) {
    Write-Error "Parameters -templateType and -fromXml cannot be used together. Please provide only one."
    exit 1
}

# Ensure imagePath is only used with templates that support images
if (-not [string]::IsNullOrEmpty($imagePath) -and $templateType -ne "" -and $templateType -notmatch "ImageAndText") {
    Write-Error "The -imagePath parameter is only applicable for ImageAndText templates."
    exit 1
}

$NotificationType = [Windows.UI.Notifications.ToastTemplateType, Windows.UI.Notifications, ContentType = WindowsRuntime]
$ToastManager = [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]
$ToastNotification = [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime]
$XmlDocument = [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime]::New()

$templates = @{
    ToastText01 = $NotificationType::ToastText01
    ToastText02 = $NotificationType::ToastText02
    ToastText03 = $NotificationType::ToastText03
    ToastText04 = $NotificationType::ToastText04
    ToastImageAndText01 = $NotificationType::ToastImageAndText01
    ToastImageAndText02 = $NotificationType::ToastImageAndText02
    ToastImageAndText03 = $NotificationType::ToastImageAndText03
    ToastImageAndText04 = $NotificationType::ToastImageAndText04
}

if ($templateType -eq "" -and -Not $fromXml) {
    Write-Error "Either -templateType or -fromXml must be supplied."
    exit 1
}

if ($fromXml) {
    if (Test-Path $fromXml -PathType Leaf -ErrorAction SilentlyContinue) {
        $xmlContent = Get-Content -Path $fromXml -Raw
    } else {
        $xmlContent = $fromXml
    }
    
    try {
        $XmlDocument.loadXml($xmlContent)
    } catch {
        Write-Error "Invalid XML provided in -fromXml. Ensure it is a valid XML file or a well-formed XML string."
        exit 1
    }

} elseif ($templates.ContainsKey($templateType)) {
    $TemplateContent = $ToastManager::GetTemplateContent($templates[$templateType])
    
    try {
        if ($templateType -match 'Text') {
            $TemplateContent.GetElementsByTagName('text').Item(0).InnerText = $text1
            if ($text2) { $TemplateContent.GetElementsByTagName('text').Item(1).InnerText = $text2 }
            if ($text3) { $TemplateContent.GetElementsByTagName('text').Item(2).InnerText = $text3 }
        }
    } catch {
        Write-Error "Error setting text values. Ensure the correct template type is used and text fields are within valid limits."
        exit 1
    }
    
    try {
        if ($templateType -match 'ImageAndText') {
            $TemplateContent.GetElementsByTagName('image').Item(0).SetAttribute("src", $imagePath)
        }
    } catch {
        Write-Error "Error setting image. Ensure the correct template type supports images."
        exit 1
    }

    if ($durationLong) {
        $TemplateContent.DocumentElement.SetAttribute("duration", "long")
    }

    $XmlDocument = $TemplateContent
} else {
    Write-Error "Invalid templateType provided. Please use a valid template (e.g., ToastText01, ToastImageAndText01) or supply -fromXml."
    exit 1
}

$Toast = New-Object Windows.UI.Notifications.ToastNotification $XmlDocument
$AppId = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe'
$ToastManager::CreateToastNotifier($AppId).Show($Toast)