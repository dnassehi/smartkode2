#!/usr/bin/env python3
"""
Script for testing and comparing Docker image sizes
"""
import subprocess
import json
import os
import sys
from pathlib import Path

def run_command(cmd, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result
    except Exception as e:
        print(f"Error running command '{cmd}': {e}")
        return None

def get_image_size(image_name):
    """Get the size of a Docker image"""
    cmd = f"docker images {image_name} --format '{{{{.Size}}}}'"
    result = run_command(cmd)
    if result and result.returncode == 0:
        return result.stdout.strip()
    return "Unknown"

def build_image(dockerfile, tag, dockerignore=None):
    """Build a Docker image with specified Dockerfile"""
    print(f"\n🔨 Building image with {dockerfile}...")
    
    # Copy dockerignore if specified
    if dockerignore and os.path.exists(dockerignore):
        run_command(f"cp {dockerignore} .dockerignore")
    
    # Build the image
    cmd = f"docker build -f {dockerfile} -t {tag} ."
    result = run_command(cmd, capture_output=False)
    
    if result and result.returncode == 0:
        size = get_image_size(tag)
        print(f"✅ Successfully built {tag} - Size: {size}")
        return size
    else:
        print(f"❌ Failed to build {tag}")
        return None

def cleanup_images(tags):
    """Remove Docker images"""
    for tag in tags:
        run_command(f"docker rmi {tag}")

def main():
    print("🐳 Docker Image Size Comparison Tool")
    print("=" * 50)
    
    # Check if Docker is available
    result = run_command("docker --version")
    if not result or result.returncode != 0:
        print("❌ Docker is not available. Please install Docker first.")
        sys.exit(1)
    
    # Test different configurations
    configs = [
        {
            "name": "Original",
            "dockerfile": "Dockerfile",
            "tag": "icpc2-original",
            "dockerignore": ".dockerignore"
        },
        {
            "name": "Optimized",
            "dockerfile": "Dockerfile.optimized", 
            "tag": "icpc2-optimized",
            "dockerignore": ".dockerignore.optimized"
        }
    ]
    
    results = {}
    
    for config in configs:
        if os.path.exists(config["dockerfile"]):
            size = build_image(
                config["dockerfile"], 
                config["tag"], 
                config["dockerignore"]
            )
            results[config["name"]] = {
                "size": size,
                "tag": config["tag"]
            }
        else:
            print(f"⚠️  {config['dockerfile']} not found, skipping...")
    
    # Print comparison
    print("\n📊 Image Size Comparison:")
    print("-" * 40)
    
    for name, data in results.items():
        print(f"{name:12}: {data['size']}")
    
    # Cleanup
    print("\n🧹 Cleaning up test images...")
    tags = [data["tag"] for data in results.values()]
    cleanup_images(tags)
    
    print("\n✅ Done!")

if __name__ == "__main__":
    main()
