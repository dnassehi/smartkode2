#!/usr/bin/env python3
"""
Simplified Railway deployment script
"""
import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(filename):
    """Check if a file exists"""
    return Path(filename).exists()

def apply_optimizations(level="optimized"):
    """Apply the optimized Dockerfile and .dockerignore"""
    print(f"🔧 Applying {level} optimizations...")
    
    if level == "minimal":
        dockerfile = "Dockerfile.minimal"
        dockerignore = ".dockerignore.minimal"
    else:
        dockerfile = "Dockerfile.optimized"
        dockerignore = ".dockerignore.optimized"
    
    # Check if optimized files exist
    if not check_file_exists(dockerfile):
        print(f"❌ {dockerfile} not found!")
        return False
    
    if not check_file_exists(dockerignore):
        print(f"❌ {dockerignore} not found!")
        return False
    
    # Apply optimizations
    subprocess.run(f"copy {dockerfile} Dockerfile", shell=True)
    subprocess.run(f"copy {dockerignore} .dockerignore", shell=True)
    
    print(f"✅ Applied {level} Dockerfile and .dockerignore")
    return True

def show_deployment_instructions():
    """Show deployment instructions"""
    print("\n🚀 Railway Deployment Instructions:")
    print("=" * 50)
    print("1. 📁 Push your code to GitHub:")
    print("   git add .")
    print("   git commit -m 'Optimized Docker image'")
    print("   git push origin main")
    print()
    print("2. 🌐 Go to Railway Dashboard:")
    print("   https://railway.app")
    print()
    print("3. 🔗 Connect your GitHub repo:")
    print("   • Click 'New Project'")
    print("   • Select 'Deploy from GitHub repo'")
    print("   • Choose your repository")
    print()
    print("4. ⚙️  Configure environment variables:")
    print("   • MISTRAL_API_KEY=your_api_key_here")
    print("   • MISTRAL_MODEL=mistral-large-latest")
    print()
    print("5. 🚀 Deploy:")
    print("   • Railway will automatically detect Dockerfile")
    print("   • Build will start automatically")
    print("   • Monitor build logs in Railway dashboard")
    print()
    print("💡 Tips:")
    print("   • Use 'deploy-minimal' if you have size issues")
    print("   • Check Railway logs if build fails")
    print("   • Ensure all environment variables are set")

def main():
    print("🐳 Railway Deployment Helper")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "apply":
            if apply_optimizations():
                show_deployment_instructions()
            else:
                print("❌ Failed to apply optimizations")
        
        elif command == "deploy-minimal":
            if apply_optimizations("minimal"):
                show_deployment_instructions()
            else:
                print("❌ Failed to apply optimizations")
        
        elif command == "help":
            show_deployment_instructions()
        
        else:
            print("❌ Unknown command. Use: apply, deploy-minimal, or help")
    
    else:
        print("Usage:")
        print("  python deploy_railway.py apply         - Apply optimized version")
        print("  python deploy_railway.py deploy-minimal - Apply minimal version")
        print("  python deploy_railway.py help          - Show deployment instructions")

if __name__ == "__main__":
    main()
