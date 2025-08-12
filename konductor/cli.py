"""
Command-line interface for Konductor.
"""
import argparse
import os
import sys
from .core.generator import KonductorGenerator

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate agent code from Konductor YAML manifests.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  konductor generate simple_agent.yaml
  konductor generate -p google_adk -o my_agent simple_agent.yaml
  konductor list-providers
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate code from manifest")
    generate_parser.add_argument(
        "manifest_file", 
        help="Path to the input YAML manifest file"
    )
    generate_parser.add_argument(
        "-p", "--provider", 
        default="google_adk",
        help="Provider to use for code generation (default: google_adk)"
    )
    generate_parser.add_argument(
        "-o", "--output-dir", 
        default="generated_agent",
        help="Directory to save generated code (default: generated_agent)"
    )
    
    # List providers command
    list_parser = subparsers.add_parser("list-providers", help="List available providers")
    
    # Dependencies command
    deps_parser = subparsers.add_parser("dependencies", help="Show required dependencies")
    deps_parser.add_argument(
        "-p", "--provider", 
        default="google_adk",
        help="Provider to show dependencies for (default: google_adk)"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "generate":
            if not os.path.exists(args.manifest_file):
                print(f"Error: Manifest file not found at '{args.manifest_file}'")
                sys.exit(1)
            
            generator = KonductorGenerator(provider=args.provider)
            generator.generate_from_manifest(args.manifest_file, args.output_dir)
            
        elif args.command == "list-providers":
            generator = KonductorGenerator()
            providers = generator.list_available_providers()
            print("Available providers:")
            for provider in providers:
                print(f"  - {provider}")
        
        elif args.command == "dependencies":
            generator = KonductorGenerator(provider=args.provider)
            deps_info = generator.get_required_dependencies()
            print(f"Dependencies for provider '{deps_info['provider']}':")
            for dep in deps_info['dependencies']:
                print(f"  - {dep}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()