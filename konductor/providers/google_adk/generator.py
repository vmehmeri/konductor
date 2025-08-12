"""
Google ADK specific code generator.
"""
import os
from typing import Dict, List, Any
from jinja2 import Environment, FileSystemLoader
from ..base import CodeGenerator
from ...core.models import ParsedManifest
from ...core.parser import ManifestParser

class GoogleAdkGenerator(CodeGenerator):
    """Code generator for Google ADK framework."""
    
    def __init__(self):
        super().__init__("google_adk")
        self.templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))
    
    def generate_code(self, manifest: ParsedManifest, output_dir: str, **kwargs) -> Dict[str, str]:
        """Generate Google ADK code from parsed manifest."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Find root agent
        parser = ManifestParser()
        root_agents = parser.find_root_agents(manifest)
        root_agent_name = root_agents[0]  # Use first root agent
        print(f"Identified '{root_agent_name}' as the root agent.")
        
        generated_files = {}
        
        # Generate tools.py
        tools_template = self.env.get_template("tools.py.j2")
        tools_content = tools_template.render(tools=manifest.tools)
        tools_path = os.path.join(output_dir, "tools.py")
        with open(tools_path, "w") as f:
            f.write(tools_content)
        generated_files[tools_path] = tools_content
        print(f"Generated {tools_path}")
        
        # Generate agent.py
        agent_template = self.env.get_template("agent.py.j2")
        agent_content = agent_template.render(
            tools=manifest.tools,
            models=manifest.models,
            llm_agents=manifest.llm_agents,
            sequential_agents=manifest.sequential_agents,
            root_agent_name=root_agent_name
        )
        agent_path = os.path.join(output_dir, "agent.py")
        with open(agent_path, "w") as f:
            f.write(agent_content)
        generated_files[agent_path] = agent_content
        print(f"Generated {agent_path}")
        
        # Generate main.py
        main_template = self.env.get_template("main.py.j2")
        main_content = main_template.render()
        main_path = os.path.join(output_dir, "main.py")
        with open(main_path, "w") as f:
            f.write(main_content)
        generated_files[main_path] = main_content
        print(f"Generated {main_path}")
        
        # Create __init__.py
        init_path = os.path.join(output_dir, "__init__.py")
        init_content = "# Auto-generated __init__.py"
        with open(init_path, "w") as f:
            f.write(init_content)
        generated_files[init_path] = init_content
        print(f"Generated {init_path}")
        
        return generated_files
    
    def get_required_dependencies(self) -> List[str]:
        """Get required dependencies for Google ADK."""
        return [
            "google-adk>=1.10.0",
        ]
    
    def validate_manifest_for_provider(self, manifest: ParsedManifest) -> List[str]:
        """Validate manifest for Google ADK specific requirements."""
        errors = []
        
        # Check that all models use Google provider
        for model in manifest.models:
            if model.spec.provider != "google":
                errors.append(f"Model '{model.metadata.name}' uses provider '{model.spec.provider}', but Google ADK only supports 'google' provider")
        
        # Check for Google-specific model IDs
        google_model_prefixes = ["gemini", "text", "chat"]
        for model in manifest.models:
            if not any(model.spec.modelId.startswith(prefix) for prefix in google_model_prefixes):
                errors.append(f"Model '{model.metadata.name}' has modelId '{model.spec.modelId}' which doesn't appear to be a Google model")
        
        return errors