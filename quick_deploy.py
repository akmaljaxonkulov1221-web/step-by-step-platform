#!/usr/bin/env python3
"""
Quick Deploy Script for Render
Auto-deploy latest changes to Render platform
"""

import os
import sys
import subprocess
from datetime import datetime

def check_git_status():
    """Check git status"""
    print("=== CHECKING GIT STATUS ===")
    
    try:
        # Check if git repository exists
        if not os.path.exists('.git'):
            print("Git repository not found. Initializing...")
            subprocess.run(['git', 'init'], check=True)
            subprocess.run(['git', 'branch', '-M', 'main'], check=True)
            print("Git repository initialized!")
        
        # Check git status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("Changes detected:")
            print(result.stdout)
            return True
        else:
            print("No changes to commit")
            return False
            
    except Exception as e:
        print(f"Git status check error: {e}")
        return False

def add_and_commit_changes():
    """Add and commit changes"""
    print("\n=== ADDING AND COMMITTING CHANGES ===")
    
    try:
        # Add all changes
        subprocess.run(['git', 'add', '.'], check=True)
        print("All changes added to staging area")
        
        # Commit changes
        commit_message = f"Auto-deploy - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        print(f"Changes committed: {commit_message}")
        
        return True
        
    except Exception as e:
        print(f"Commit error: {e}")
        return False

def push_to_github():
    """Push to GitHub"""
    print("\n=== PUSHING TO GITHUB ===")
    
    try:
        # Check if remote exists
        result = subprocess.run(['git', 'remote'], 
                              capture_output=True, text=True)
        
        if 'origin' not in result.stdout:
            print("No remote 'origin' found")
            print("Please add your GitHub repository:")
            print("git remote add origin https://github.com/YOUR_USERNAME/step-by-step-platform.git")
            return False
        
        # Push to GitHub
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("Pushed to GitHub successfully!")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Push error: {e}")
        print("Please check your GitHub credentials and repository URL")
        return False
    except Exception as e:
        print(f"Push error: {e}")
        return False

def show_render_info():
    """Show Render deployment info"""
    print("\n=== RENDER DEPLOYMENT INFO ===")
    
    print("Your changes are now being deployed to Render!")
    print("\nWhat happens next:")
    print("1. Render detects the push to GitHub")
    print("2. Render automatically builds your application")
    print("3. Render deploys the new version")
    print("4. Your application updates automatically")
    
    print("\nMonitor deployment at:")
    print("- Render Dashboard: https://dashboard.render.com")
    print("- Your app URL: https://step-by-step-platform.onrender.com")
    
    print("\nDeployment usually takes 2-5 minutes")
    print("You can check the build logs in Render dashboard")

def main():
    """Main deployment function"""
    print("STEP BY STEP EDUCATION PLATFORM - QUICK DEPLOY")
    print("Auto-deploying latest changes to Render...")
    
    # Check git status
    if not check_git_status():
        print("No changes to deploy")
        return True
    
    # Add and commit changes
    if not add_and_commit_changes():
        print("Failed to commit changes")
        return False
    
    # Push to GitHub
    if not push_to_github():
        print("Failed to push to GitHub")
        return False
    
    # Show Render info
    show_render_info()
    
    print("\n=== DEPLOYMENT INITIATED ===")
    print("Your application is now being deployed to Render!")
    print("Auto-deploy is configured and will handle everything automatically.")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
