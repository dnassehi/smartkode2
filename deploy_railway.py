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
    elif level == "robust":
        dockerfile = "Dockerfile.robust"
        dockerignore = ".dockerignore.optimized"
    elif level == "debian":
        dockerfile = "Dockerfile.debian"
        dockerignore = ".dockerignore.optimized"
    elif level == "fast":
        dockerfile = "Dockerfile.fast"
        dockerignore = ".dockerignore.optimized"
    elif level == "ultra-fast":
        dockerfile = "Dockerfile.ultra-fast"
        dockerignore = ".dockerignore.optimized"
    elif level == "simple":
        dockerfile = "Dockerfile.simple"
        dockerignore = ".dockerignore.optimized"
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
    print("   • Use 'deploy-ultra-fast' if Railway times out (recommended)")
    print("   • Use 'deploy-fast' for faster builds")
    print("   • Use 'deploy-robust' if build fails")
    print("   • Use 'deploy-debian' for maximum compatibility")
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
        
        elif command == "deploy-robust":
            if apply_optimizations("robust"):
                show_deployment_instructions()
            else:
                print("❌ Failed to apply optimizations")
        
        elif command == "deploy-debian":
            if apply_optimizations("debian"):
                show_deployment_instructions()
            else:
                print("❌ Failed to apply optimizations")
        
        elif command == "deploy-fast":
            if apply_optimizations("fast"):
                show_deployment_instructions()
            else:
                print("❌ Failed to apply optimizations")
        
        elif command == "deploy-ultra-fast":
            if apply_optimizations("ultra-fast"):
                show_deployment_instructions()
            else:
                print("❌ Failed to apply optimizations")
        
        elif command == "deploy-simple":
            if apply_optimizations("simple"):
                show_deployment_instructions()
            else:
                print("❌ Failed to apply optimizations")
        
        elif command == "help":
            show_deployment_instructions()
        
        else:
            print("❌ Unknown command. Use: apply, deploy-minimal, deploy-robust, deploy-debian, deploy-fast, deploy-ultra-fast, deploy-simple, or help")
    
    else:
        print("Usage:")
        print("  python deploy_railway.py apply         - Apply optimized version")
        print("  python deploy_railway.py deploy-minimal - Apply minimal version")
        print("  python deploy_railway.py deploy-robust  - Apply robust version (recommended)")
        print("  python deploy_railway.py deploy-debian  - Apply Debian version (most compatible)")
        print("  python deploy_railway.py deploy-fast    - Apply fast version (for Railway timeout)")
        print("  python deploy_railway.py deploy-ultra-fast - Apply ultra-fast version (best for Railway)")
        print("  python deploy_railway.py deploy-simple  - Apply simple version (fastest build)")
        print("  python deploy_railway.py help          - Show deployment instructions")

if __name__ == "__main__":
    main()
