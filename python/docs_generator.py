#!/usr/bin/env python3
"""
Governance Documentation Generator
Automatically generates documentation from policies and compliance rules.
"""

import json
import yaml
import os
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path


class DocsGenerator:
    def __init__(self, output_dir: str = "docs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_from_policy(self, policy_path: str) -> Dict[str, Any]:
        """Generate documentation from a policy file."""
        with open(policy_path, 'r') as f:
            if policy_path.endswith('.yaml') or policy_path.endswith('.yml'):
                policy = yaml.safe_load(f)
            else:
                policy = json.load(f)
        
        doc = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "policy_file": policy_path,
                "policy_name": policy.get('metadata', {}).get('name', 'unknown')
            },
            "policy": policy,
            "sections": self._create_policy_sections(policy)
        }
        
        return doc
    
    def _create_policy_sections(self, policy: Dict) -> List[Dict]:
        """Create documentation sections from policy."""
        sections = []
        
        # Overview section
        metadata = policy.get('metadata', {})
        sections.append({
            "title": "Overview",
            "content": {
                "description": metadata.get('description', ''),
                "severity": metadata.get('severity', 'medium'),
                "category": metadata.get('category', 'security'),
                "version": metadata.get('version', '1.0.0')
            }
        })
        
        # Rules section
        spec = policy.get('spec', {})
        rules = spec.get('rules', [])
        if rules:
            sections.append({
                "title": "Rules",
                "content": {
                    "target_resource": spec.get('targetResource'),
                    "rules": rules
                }
            })
        
        # Remediation section
        remediation = spec.get('remediation', {})
        if remediation:
            sections.append({
                "title": "Remediation",
                "content": remediation
            })
        
        # Compliance section
        compliance = policy.get('compliance', {})
        if compliance:
            sections.append({
                "title": "Compliance",
                "content": compliance
            })
        
        return sections
    
    def generate_markdown(self, doc: Dict) -> str:
        """Generate markdown documentation."""
        metadata = doc['metadata']
        policy = doc['policy']
        sections = doc['sections']
        
        lines = [
            f"# {policy.get('metadata', {}).get('name', 'Policy')}",
            "",
            f"*Generated at: {metadata['generated_at']}*",
            "",
            policy.get('metadata', {}).get('description', ''),
            "",
        ]
        
        for section in sections:
            lines.extend([
                f"## {section['title']}",
                ""
            ])
            
            if section['title'] == "Overview":
                content = section['content']
                lines.extend([
                    f"- **Severity**: {content['severity']}",
                    f"- **Category**: {content['category']}",
                    f"- **Version**: {content['version']}",
                    ""
                ])
            
            elif section['title'] == "Rules":
                content = section['content']
                lines.extend([
                    f"**Target Resource**: `{content['target_resource']}`",
                    "",
                    "### Rules Details:",
                    ""
                ])
                
                for i, rule in enumerate(content['rules'], 1):
                    lines.extend([
                        f"#### Rule {i}: {rule.get('name', f'rule-{i}')}",
                        f"- **Condition**: `{rule.get('condition')}`",
                        f"- **Message**: {rule.get('message', '')}",
                        ""
                    ])
            
            elif section['title'] == "Remediation":
                content = section['content']
                lines.extend([
                    f"**Type**: {content.get('type', 'manual')}",
                    "",
                    "### Template:",
                    "",
                    "```" + content.get('language', 'hcl'),
                    content.get('template', ''),
                    "```",
                    ""
                ])
        
        return "\n".join(lines)
    
    def save_documentation(self, policy_path: str, output_format: str = "markdown"):
        """Generate and save documentation for a policy."""
        doc = self.generate_from_policy(policy_path)
        
        if output_format == "markdown":
            markdown = self.generate_markdown(doc)
            policy_name = doc['metadata']['policy_name']
            output_file = self.output_dir / f"{policy_name}.md"
            
            with open(output_file, 'w') as f:
                f.write(markdown)
            
            print(f"Documentation generated: {output_file}")
            return output_file
        
        elif output_format == "html":
            # HTML generation would go here
            pass
        
        elif output_format == "json":
            output_file = self.output_dir / f"{doc['metadata']['policy_name']}.json"
            with open(output_file, 'w') as f:
                json.dump(doc, f, indent=2)
            print(f"JSON documentation generated: {output_file}")
            return output_file


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate documentation from governance policies')
    parser.add_argument('policy_files', nargs='+', help='Policy files to document')
    parser.add_argument('--output-dir', default='docs', help='Output directory')
    parser.add_argument('--format', choices=['markdown', 'html', 'json'], 
                       default='markdown', help='Output format')
    
    args = parser.parse_args()
    
    generator = DocsGenerator(args.output_dir)
    
    for policy_file in args.policy_files:
        if os.path.exists(policy_file):
            try:
                generator.save_documentation(policy_file, args.format)
            except Exception as e:
                print(f"Error processing {policy_file}: {e}")
        else:
            print(f"File not found: {policy_file}")


if __name__ == "__main__":
    main()
