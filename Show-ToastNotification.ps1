<#
.SYNOPSIS
    Sends a Windows Toast Notification using PowerShell.
.DESCRIPTION
    This script sends a toast notification with text and optionally an image. 
    It supports multiple template types and allows specifying a duration. 
    Additionally, it supports user-supplied XML document.
.PARAMETER templateType
    Specifies the toast template type (e.g., ToastText01, ToastImageAndText01). Defaults to "". If not supplied, -fromXml is required.
.PARAMETER text1
    Primary text to be displayed in the notification.
.PARAMETER text2
    Secondary text to be displayed.
.PARAMETER text3
    Tertiary text to be displayed.
.PARAMETER imagePath
    Absolute path to an image for ImageAndText templates. Defaults to "C:\Windows\IdentityCRL\WLive48x48.png".
.PARAMETER durationLong
    (Optional) Duration of the notification. Set to long duration (25 seconds) when flag is provided. 
.PARAMETER fromXml
    (Required if templateType is not supplied) The entire XML document as a string or a file path to an XML file.
.EXAMPLE
    .\Show-ToastNotification.ps1 -templateType "ToastText02" -text1 "Hello" -text2 "This is a notification" -duration "long"
.EXAMPLE
    .\Show-ToastNotification.ps1 -templateType "ToastImageAndText01" -text1 "Hello" -imagePath "file:///C:/path/to/image.png" -duration "short"
.EXAMPLE
    .\Show-ToastNotification.ps1 -fromXml "C:\path\to\toast.xml"
.EXAMPLE
    .\Show-ToastNotification.ps1 -fromXml "<toast><visual><binding template='ToastGeneric'><text>Hello</text></binding></visual></toast>"
#>

param (
    [string]$templateType = "",  # Defaults to empty; if not supplied, -fromXml is required
    [string]$text1,
    [string]$text2,
    [string]$text3,
    [string]$imagePath = "C:\Windows\IdentityCRL\WLive48x48.png",
    [switch]$durationLong,    
    [string]$fromXml  # Required if templateType is not supplied
)

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
    # Check if fromXml is a file path
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
    
    if ($templateType -match 'Text') {
        $TemplateContent.GetElementsByTagName('text').Item(0).InnerText = $text1
        if ($text2) { $TemplateContent.GetElementsByTagName('text').Item(1).InnerText = $text2 }
        if ($text3) { $TemplateContent.GetElementsByTagName('text').Item(2).InnerText = $text3 }
    }
    
    if ($templateType -match 'ImageAndText') {
        $TemplateContent.GetElementsByTagName('image').Item(0).SetAttribute("src", $imagePath)
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
