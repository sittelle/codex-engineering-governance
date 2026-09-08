@{
    Severity = @('Error', 'Warning')
    # These scripts are user-facing CLI utilities. Write-Host is intentionally
    # used for display-only status/preview text, not for pipeline data or logging.
    # Keep every other default Warning/Error rule enabled.
    ExcludeRules = @('PSAvoidUsingWriteHost')
}
