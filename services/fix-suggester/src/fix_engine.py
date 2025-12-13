import yaml
import re
from typing import Dict, List, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

class FixEngine:
    """Engine for generating security fixes for GitHub Actions workflows"""
    
    def __init__(self):
        # Setup Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['yaml', 'yml'])
        )
    
    def generate_fix(self, workflow_yaml: str, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a fix for a specific vulnerability.
        
        Args:
            workflow_yaml: Original workflow YAML content
            vulnerability: Vulnerability details
            
        Returns:
            Dictionary with fixed_yaml and metadata
        """
        vuln_type = vulnerability.get('type', '')
        
        if vuln_type == 'unpinned_action':
            return self.lock_action_versions(workflow_yaml, vulnerability)
        elif vuln_type == 'excessive_permissions':
            return self.restrict_permissions(workflow_yaml, vulnerability)
        elif vuln_type == 'hardcoded_secret':
            return self.add_secret_encryption(workflow_yaml, vulnerability)
        elif vuln_type == 'weak_hardening':
            return self.improve_hardening(workflow_yaml, vulnerability)
        else:
            return {
                'fixed_yaml': workflow_yaml,
                'description': 'Unknown vulnerability type',
                'severity': 'low',
                'auto_applicable': False
            }
    
    def lock_action_versions(self, workflow_yaml: str, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pin GitHub Actions to specific commit SHAs.
        
        Args:
            workflow_yaml: Original workflow YAML
            vulnerability: Vulnerability details
            
        Returns:
            Fix details
        """
        lines = workflow_yaml.split('\n')
        fixed_lines = []
        
        # Common actions with their pinned versions (SHA@version)
        pinned_versions = {
            'actions/checkout@main': 'actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1',
            'actions/checkout@v4': 'actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1',
            'actions/checkout@v3': 'actions/checkout@f43a0e5ff2bd294095638e18286ca9a3d1956744 # v3.6.0',
            'actions/setup-node@v3': 'actions/setup-node@64ed1c7eab4cce3362f8c340dee64e5eaeef8f7c # v3.6.0',
            'actions/setup-node@v4': 'actions/setup-node@60edb5dd545a775178f52524783378180af0d1f8 # v4.0.2',
            'actions/setup-python@v4': 'actions/setup-python@65d7f2d534ac1bc67fcd62888c5f4f3d2cb2b236 # v4.7.1',
            'actions/setup-python@v5': 'actions/setup-python@0a5c61591373683505ea898e09a3ea4f39ef2b9c # v5.0.0',
        }
        
        for line in lines:
            # Check if line contains 'uses:' with unpinned action
            if 'uses:' in line and '@' in line:
                for unpinned, pinned in pinned_versions.items():
                    if unpinned in line:
                        line = line.replace(unpinned, pinned)
                        break
            fixed_lines.append(line)
        
        fixed_yaml = '\n'.join(fixed_lines)
        
        return {
            'fixed_yaml': fixed_yaml,
            'description': 'Pinned GitHub Actions to specific commit SHAs to prevent supply chain attacks',
            'severity': 'high',
            'auto_applicable': True
        }
    
    def restrict_permissions(self, workflow_yaml: str, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add minimal required permissions to workflow.
        
        Args:
            workflow_yaml: Original workflow YAML
            vulnerability: Vulnerability details
            
        Returns:
            Fix details
        """
        try:
            workflow_dict = yaml.safe_load(workflow_yaml)
            
            # Add minimal permissions at workflow level if not present
            if 'permissions' not in workflow_dict:
                workflow_dict['permissions'] = {
                    'contents': 'read',
                    'pull-requests': 'write'
                }
            
            # Convert back to YAML
            fixed_yaml = yaml.dump(workflow_dict, default_flow_style=False, sort_keys=False)
            
            return {
                'fixed_yaml': fixed_yaml,
                'description': 'Added minimal required permissions following the principle of least privilege',
                'severity': 'medium',
                'auto_applicable': True
            }
        except Exception as e:
            return {
                'fixed_yaml': workflow_yaml,
                'description': f'Failed to parse YAML: {str(e)}',
                'severity': 'medium',
                'auto_applicable': False
            }
    
    def add_secret_encryption(self, workflow_yaml: str, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replace hardcoded secrets with GitHub Secrets references.
        
        Args:
            workflow_yaml: Original workflow YAML
            vulnerability: Vulnerability details
            
        Returns:
            Fix details
        """
        lines = workflow_yaml.split('\n')
        fixed_lines = []
        
        # Patterns to detect potential secrets
        secret_patterns = [
            (r'password:\s*["\']?[\w]+["\']?', 'password: ${{ secrets.PASSWORD }}'),
            (r'token:\s*["\']?[\w]+["\']?', 'token: ${{ secrets.GITHUB_TOKEN }}'),
            (r'api_key:\s*["\']?[\w]+["\']?', 'api_key: ${{ secrets.API_KEY }}'),
            (r'secret:\s*["\']?[\w]+["\']?', 'secret: ${{ secrets.SECRET }}'),
        ]
        
        for line in lines:
            modified = False
            for pattern, replacement in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE) and '${{' not in line:
                    # Extract the key name
                    key = line.split(':')[0].strip()
                    line = f"{key}: ${{{{ secrets.{key.upper()} }}}}"
                    modified = True
                    break
            fixed_lines.append(line)
        
        fixed_yaml = '\n'.join(fixed_lines)
        
        return {
            'fixed_yaml': fixed_yaml,
            'description': 'Replaced hardcoded secrets with GitHub Secrets references',
            'severity': 'critical',
            'auto_applicable': False  # Requires manual secret setup
        }
    
    def improve_hardening(self, workflow_yaml: str, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add security hardening measures to workflow.
        
        Args:
            workflow_yaml: Original workflow YAML
            vulnerability: Vulnerability details
            
        Returns:
            Fix details
        """
        try:
            workflow_dict = yaml.safe_load(workflow_yaml)
            
            # Add concurrency control if not present
            if 'concurrency' not in workflow_dict:
                workflow_dict['concurrency'] = {
                    'group': '${{ github.workflow }}-${{ github.ref }}',
                    'cancel-in-progress': True
                }
            
            # Add timeouts to jobs if not present
            if 'jobs' in workflow_dict:
                for job_name, job_config in workflow_dict['jobs'].items():
                    if isinstance(job_config, dict) and 'timeout-minutes' not in job_config:
                        job_config['timeout-minutes'] = 30
            
            # Convert back to YAML
            fixed_yaml = yaml.dump(workflow_dict, default_flow_style=False, sort_keys=False)
            
            return {
                'fixed_yaml': fixed_yaml,
                'description': 'Added security hardening: concurrency control and job timeouts',
                'severity': 'low',
                'auto_applicable': True
            }
        except Exception as e:
            return {
                'fixed_yaml': workflow_yaml,
                'description': f'Failed to parse YAML: {str(e)}',
                'severity': 'low',
                'auto_applicable': False
            }
