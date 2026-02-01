#!/usr/bin/env python3
"""
AI Engine for generating intelligent explanations and recommendations.
This module provides an abstracted interface to LLM APIs.
"""

import os
from typing import Dict, Any, Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, will use system environment variables
    pass


class AIEngine:
    """
    Abstracted AI engine for generating recommendations.
    Supports multiple LLM providers via environment variables.
    """
    
    def __init__(self):
        # Check for API keys in order of preference
        self.api_key = (
            os.getenv("GEMINI_API_KEY") or 
            os.getenv("OPENAI_API_KEY") or 
            os.getenv("ANTHROPIC_API_KEY")
        )
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        
    def generate_recommendations(
        self,
        data: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate AI-powered recommendations based on system data and analysis.
        
        Args:
            data: Collected system data
            analysis: Rule-based analysis results
            
        Returns:
            Markdown-formatted recommendations or None if API unavailable
        """
        # If no API key, return None (graceful degradation)
        if not self.api_key:
            return None
        
        # Prepare context for LLM
        context = self._prepare_context(data, analysis)
        
        # Generate prompt
        prompt = self._build_prompt(context, analysis)
        
        # Call LLM (abstracted)
        try:
            if self.provider == "gemini":
                return self._call_gemini(prompt)
            elif self.provider == "openai":
                return self._call_openai(prompt)
            elif self.provider == "anthropic":
                return self._call_anthropic(prompt)
            else:
                # Fallback: return structured recommendations
                return self._generate_fallback_recommendations(analysis)
        except Exception as e:
            print(f"Warning: LLM API call failed: {e}", file=__import__("sys").stderr)
            return self._generate_fallback_recommendations(analysis)
    
    def _prepare_context(self, data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare a clean context summary for the LLM."""
        context = {
            "health_metrics": {},
            "security_config": {},
            "log_summary": {},
            "findings_count": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }
        
        # Health metrics
        health = data.get("health", {})
        if health:
            context["health_metrics"] = {
                "cpu_percent": health.get("cpu", {}).get("usage_percent", 0),
                "memory_percent": health.get("memory", {}).get("usage_percent", 0),
                "disk_percent": health.get("disk", {}).get("usage_percent", 0)
            }
        
        # Security config
        ssh = data.get("ssh_config", {})
        if ssh:
            context["security_config"] = {
                "root_login_enabled": ssh.get("root_login_enabled"),
                "password_auth_enabled": ssh.get("password_auth_enabled")
            }
        
        # Log summary
        log_analysis = data.get("log_analysis", {})
        if log_analysis:
            context["log_summary"] = {
                "failed_ssh_logins": log_analysis.get("failed_ssh_logins", 0),
                "service_errors": log_analysis.get("service_errors", []),
                "segfaults": log_analysis.get("segfaults", 0)
            }
        
        # Count findings by severity
        for finding in analysis.get("health", []) + analysis.get("security", []):
            severity = finding.get("severity", "LOW").lower()
            if severity in context["findings_count"]:
                context["findings_count"][severity] += 1
        
        return context
    
    def _build_prompt(self, context: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Build the prompt for the LLM."""
        prompt = """You are a senior Linux system administrator analyzing a server health and security audit.

System Context:
- CPU Usage: {cpu}%
- Memory Usage: {memory}%
- Disk Usage: {disk}%
- SSH Root Login: {root_login}
- SSH Password Auth: {password_auth}
- Failed SSH Logins: {failed_logins}
- Service Errors: {service_errors}
- Segmentation Faults: {segfaults}

Findings Summary:
- Critical Issues: {critical}
- High Severity: {high}
- Medium Severity: {medium}
- Low Severity: {low}

Please provide:
1. A brief explanation of the most critical issues in plain language
2. Actionable recommendations (what to do, not specific commands)
3. Prioritized action items

Keep the response concise, professional, and focused on system administration best practices.
Do not include specific command-line instructions.
Format your response in markdown.""".format(
            cpu=context["health_metrics"].get("cpu_percent", 0),
            memory=context["health_metrics"].get("memory_percent", 0),
            disk=context["health_metrics"].get("disk_percent", 0),
            root_login=context["security_config"].get("root_login_enabled", "unknown"),
            password_auth=context["security_config"].get("password_auth_enabled", "unknown"),
            failed_logins=context["log_summary"].get("failed_ssh_logins", 0),
            service_errors=", ".join(context["log_summary"].get("service_errors", [])[:5]) or "None",
            segfaults=context["log_summary"].get("segfaults", 0),
            critical=context["findings_count"]["critical"],
            high=context["findings_count"]["high"],
            medium=context["findings_count"]["medium"],
            low=context["findings_count"]["low"]
        )
        
        return prompt
    
    def _call_gemini(self, prompt: str) -> Optional[str]:
        """Call Google Gemini API (requires google-generativeai package)."""
        try:
            import google.generativeai as genai
            
            # Configure the API
            genai.configure(api_key=self.api_key)
            
            # Get model (default to gemini-pro)
            model_name = os.getenv("GEMINI_MODEL", "gemini-pro")
            model = genai.GenerativeModel(model_name)
            
            # Build the full prompt with system context
            full_prompt = f"""You are a senior Linux system administrator analyzing a server health and security audit.

{prompt}"""
            
            # Generate content
            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 500,
                }
            )
            
            return response.text
        except ImportError:
            print("Warning: google-generativeai package not installed. Install with: pip install google-generativeai", 
                  file=__import__("sys").stderr)
            return None
        except Exception as e:
            print(f"Warning: Gemini API call failed: {e}", file=__import__("sys").stderr)
            return None
    
    def _call_openai(self, prompt: str) -> Optional[str]:
        """Call OpenAI API (requires openai package)."""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are a senior Linux system administrator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        except ImportError:
            return None
        except Exception:
            return None
    
    def _call_anthropic(self, prompt: str) -> Optional[str]:
        """Call Anthropic API (requires anthropic package)."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            message = client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
                max_tokens=500,
                system="You are a senior Linux system administrator.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
        except ImportError:
            return None
        except Exception:
            return None
    
    def _generate_fallback_recommendations(self, analysis: Dict[str, Any]) -> str:  # noqa: ARG002
        """Generate basic recommendations without LLM API."""
        recommendations = []
        recommendations.append("### Recommendations\n")
        
        findings = analysis.get("health", []) + analysis.get("security", [])
        
        # Group by severity
        critical = [f for f in findings if f.get("severity") == "CRITICAL"]
        high = [f for f in findings if f.get("severity") == "HIGH"]
        medium = [f for f in findings if f.get("severity") == "MEDIUM"]
        
        if critical:
            recommendations.append("#### Critical Priority\n")
            for finding in critical:
                recommendations.append(f"- **{finding['metric']}**: {finding['message']}")
                recommendations.append("  - Investigate immediately and take corrective action")
            recommendations.append("")
        
        if high:
            recommendations.append("#### High Priority\n")
            for finding in high:
                recommendations.append(f"- **{finding['metric']}**: {finding['message']}")
                recommendations.append("  - Address within 24-48 hours")
            recommendations.append("")
        
        if medium:
            recommendations.append("#### Medium Priority\n")
            for finding in medium[:5]:  # Limit to top 5
                recommendations.append(f"- **{finding['metric']}**: {finding['message']}")
                recommendations.append("  - Monitor and plan remediation")
            recommendations.append("")
        
        if not findings:
            recommendations.append("No critical issues detected. Continue regular monitoring.")
        
        return "\n".join(recommendations)
