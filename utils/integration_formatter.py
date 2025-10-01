"""
Integration Formatters for JIRA and Microsoft Teams
Formats deployment data for different platforms
"""

from typing import Dict, Any


class JiraFormatter:
    """Format deployment data as JIRA-compatible Markdown table"""

    @staticmethod
    def format(deployment_data: Dict[str, Any]) -> str:
        """
        Format deployment data as a Markdown table for JIRA

        Args:
            deployment_data: Dictionary containing deployment information

        Returns:
            Formatted Markdown table string
        """
        # Extract data with defaults
        jira_ticket = deployment_data.get('jira_patch_id', 'N/A')
        timestamp = deployment_data.get('timestamp', '')
        project_name = deployment_data.get('project_name', '')
        component_name = deployment_data.get('component_name', '')
        environment = deployment_data.get('environment', 'QA')
        build_server = deployment_data.get('build_server', '')
        deploy_server = deployment_data.get('deploy_server', '')
        vcs_url = deployment_data.get('vcs_url', '')
        database_name = deployment_data.get('database_name', '')
        database_script = deployment_data.get('database_script', 'N/A')
        backup_location = deployment_data.get('backup_location', '')
        build_status = deployment_data.get('build_status', False)
        deploy_status = deployment_data.get('deploy_status', False)
        notes = deployment_data.get('notes', '')
        deployed_by = deployment_data.get('deployed_by', '')

        # Format status with emojis
        build_status_text = "✅ Success" if build_status else "❌ Failed"
        deploy_status_text = "✅ Success" if deploy_status else "❌ Failed"

        # Format DB Script info
        db_info = database_name
        if database_script and database_script != 'N/A':
            db_info = f"Has DB backup taken - {database_name}"

        # Build markdown table
        table = []
        table.append("| Field | Value |")
        table.append("|-------|-------|")

        if jira_ticket and jira_ticket != 'N/A':
            table.append(f"| JIRA Ticket | {jira_ticket} |")

        table.append(f"| Project | {project_name} - {component_name} |")
        table.append(f"| Environment | {environment} |")
        table.append(f"| Timestamp | {timestamp} |")
        table.append(f"| Build Server | {build_server} |")
        table.append(f"| Build Status | {build_status_text} |")
        table.append(f"| Deploy Server | {deploy_server} |")
        table.append(f"| Deploy Status | {deploy_status_text} |")

        if vcs_url:
            table.append(f"| VCS URL | {vcs_url} |")

        if database_name:
            table.append(f"| Database | {db_info} |")

        if backup_location:
            table.append(f"| Backup Location | {backup_location} |")

        if notes:
            table.append(f"| Notes | {notes} |")

        table.append(f"| Deployed By | {deployed_by} |")

        return "\n".join(table)


class TeamsFormatter:
    """Format deployment data as Microsoft Teams message with emojis and bullet points"""

    @staticmethod
    def format(deployment_data: Dict[str, Any]) -> str:
        """
        Format deployment data as a Teams-friendly message with clean bullets

        Args:
            deployment_data: Dictionary containing deployment information

        Returns:
            Formatted message string with bullet points
        """
        # Extract data with defaults
        jira_ticket = deployment_data.get('jira_patch_id', 'N/A')
        timestamp = deployment_data.get('timestamp', '')
        project_name = deployment_data.get('project_name', '')
        component_name = deployment_data.get('component_name', '')
        environment = deployment_data.get('environment', 'QA')
        build_server = deployment_data.get('build_server', '')
        deploy_server = deployment_data.get('deploy_server', '')
        vcs_url = deployment_data.get('vcs_url', '')
        database_name = deployment_data.get('database_name', '')
        database_script = deployment_data.get('database_script', 'N/A')
        backup_location = deployment_data.get('backup_location', '')
        build_status = deployment_data.get('build_status', False)
        deploy_status = deployment_data.get('deploy_status', False)
        notes = deployment_data.get('notes', '')
        deployed_by = deployment_data.get('deployed_by', '')
        developer_name = deployment_data.get('developer_name', '')

        # Format status with emojis (at end of line)
        build_status_text = "Success ✅" if build_status else "Failed ❌"
        deploy_status_text = "Success ✅" if deploy_status else "Failed ❌"

        # Determine VCS type (SVN or Git) from URL
        vcs_type = "Git" if "git" in vcs_url.lower() else "SVN"

        # Build message
        message = []

        # Header with prominent JIRA ID and Patch number
        if jira_ticket and jira_ticket != 'N/A':
            message.append(f"🎫 PATCH: {jira_ticket} | {project_name} - Deployment Complete")
        else:
            message.append(f"🎫 {project_name} - Deployment Complete (No JIRA ID)")

        message.append("")  # Empty line

        # Project and component info
        message.append(f"• Project: {project_name} - {component_name}")
        message.append(f"• Environment: {environment}")

        # Build information
        message.append(f"• Build Server: {build_server}")
        message.append(f"• Build Status: {build_status_text}")

        # VCS information
        if vcs_url:
            message.append(f"• {vcs_type} URL: {vcs_url}")

        # Deploy information
        message.append(f"• Deploy Server: {deploy_server}")
        message.append(f"• Deploy Status: {deploy_status_text}")

        # Database information
        if database_name:
            if database_script and database_script != 'N/A':
                message.append(f"• Database: {database_name} (DB backup taken)")
            else:
                message.append(f"• Database: {database_name}")

        # Backup location
        if backup_location:
            message.append(f"• Backup Location: {backup_location}")

        # Developer information
        if developer_name:
            message.append(f"• Developer: {developer_name}")

        # Deployed by and timestamp
        message.append(f"• Deployed By: {deployed_by}")
        message.append(f"• Timestamp: {timestamp}")

        # Notes (if any)
        if notes:
            message.append("")  # Empty line
            message.append(f"• Notes: {notes}")

        return "\n".join(message)


# Convenience function to get formatter by type
def get_formatter(formatter_type: str):
    """
    Get formatter instance by type

    Args:
        formatter_type: Either 'jira' or 'teams'

    Returns:
        Formatter class instance

    Raises:
        ValueError: If formatter_type is not recognized
    """
    formatters = {
        'jira': JiraFormatter,
        'teams': TeamsFormatter
    }

    formatter_type = formatter_type.lower()
    if formatter_type not in formatters:
        raise ValueError(f"Unknown formatter type: {formatter_type}. Valid types: {list(formatters.keys())}")

    return formatters[formatter_type]