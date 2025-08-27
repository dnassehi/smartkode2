#!/usr/bin/env python3
"""
Script for deploying optimized Docker image to Railway
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result
    except Exception as e:
        print(f"Error running command '{cmd}': {e}")
        return None

def check_file_exists(filename):
    """Check if a file exists"""
    return Path(filename).exists()

def backup_original_files():
    """Backup original files before optimization"""
    files_to_backup = ['Dockerfile', '.dockerignore']
    
    for file in files_to_backup:
        if check_file_exists(file):
            backup_name = f"{file}.backup"
            if not check_file_exists(backup_name):
                run_command(f"cp {file} {backup_name}")
                print(f"✅ Backed up {file} to {backup_name}")

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
    run_command(f"cp {dockerfile} Dockerfile")
    run_command(f"cp {dockerignore} .dockerignore")
    
    print(f"✅ Applied {level} Dockerfile and .dockerignore")
    return True

def restore_original_files():
    """Restore original files"""
    print("🔄 Restoring original files...")
    
    files_to_restore = ['Dockerfile', '.dockerignore']
    
    for file in files_to_restore:
        backup_name = f"{file}.backup"
        if check_file_exists(backup_name):
            run_command(f"cp {backup_name} {file}")
            print(f"✅ Restored {file} from backup")
        else:
            print(f"⚠️  No backup found for {file}")

def check_railway_cli():
    """Check if Railway CLI is installed"""
    result = run_command("railway --version")
    return result and result.returncode == 0

def deploy_to_railway():
    """Deploy to Railway"""
    print("🚀 Deploying to Railway...")
    
    if not check_railway_cli():
        print("❌ Railway CLI not found. Please install it first:")
        print("   npm install -g @railway/cli")
        return False
    
    # Check if logged in
    result = run_command("railway whoami")
    if not result or result.returncode != 0:
        print("❌ Not logged in to Railway. Please run 'railway login' first.")
        return False
    
    # Deploy
    print("📤 Starting deployment...")
    result = run_command("railway up", capture_output=False)
    
    if result and result.returncode == 0:
        print("✅ Deployment successful!")
        return True
    else:
        print("❌ Deployment failed!")
        return False

def show_optimization_summary():
    """Show summary of optimizations"""
    print("\n📊 Optimization Summary:")
    print("=" * 50)
    print("🔧 Available optimizations:")
    print("  • Multi-stage Docker build")
    print("  • Alpine Linux base image")
    print("  • Minimal runtime dependencies")
    print("  • Aggressive .dockerignore")
    print("  • Non-root user for security")
    print("  • Optimized layer caching")
    print()
    print("📈 Expected size reductions:")
    print("  • Original: ~7.9 GB")
    print("  • Optimized: ~2-3 GB (60-70% reduction)")
    print("  • Minimal: ~1.5-2.5 GB (70-80% reduction)")
    print()
    print("🚀 Ready for Railway deployment!")
    print("💡 Use 'deploy-minimal' if you still have size issues")

def main():
    print("🐳 Railway Optimized Deployment Tool")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "apply":
            backup_original_files()
            if apply_optimizations():
                show_optimization_summary()
            else:
                print("❌ Failed to apply optimizations")
        
        elif command == "restore":
            restore_original_files()
            print("✅ Original files restored")
        
        elif command == "deploy":
            if apply_optimizations():
                deploy_to_railway()
            else:
                print("❌ Cannot deploy without optimizations")
        
        elif command == "deploy-minimal":
            if apply_optimizations("minimal"):
                deploy_to_railway()
            else:
                print("❌ Cannot deploy without optimizations")
        
        elif command == "summary":
            show_optimization_summary()
        
        else:
            print("❌ Unknown command. Use: apply, restore, deploy, deploy-minimal, or summary")
    
    else:
        print("Usage:")
        print("  python deploy_optimized.py apply         - Apply optimized version")
        print("  python deploy_optimized.py restore       - Restore original files")
        print("  python deploy_optimized.py deploy        - Deploy optimized to Railway")
        print("  python deploy_optimized.py deploy-minimal - Deploy minimal version to Railway")
        print("  python deploy_optimized.py summary       - Show optimization summary")

if __name__ == "__main__":
    main()
