#!/usr/bin/env python3
"""
SafeErase Launcher
Simple launcher that works without external dependencies
"""

import sys
import os
import subprocess
import webbrowser
from pathlib import Path

def print_banner():
    """Print SafeErase banner"""
    print("🔒 SafeErase - Secure Data Wiping Solution")
    print("=" * 50)
    print("Professional-grade secure data destruction")
    print("with tamper-proof certificates")
    print()

def check_python_gui():
    """Check if Python GUI dependencies are available"""
    try:
        import tkinter
        return True, "Tkinter available (basic GUI possible)"
    except ImportError:
        return False, "Tkinter not available"

def check_customtkinter():
    """Check if CustomTkinter is available"""
    try:
        import customtkinter
        return True, "CustomTkinter available (full GUI)"
    except ImportError:
        return False, "CustomTkinter not installed"

def check_flutter():
    """Check if Flutter is available"""
    try:
        result = subprocess.run(['flutter', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True, "Flutter available"
        else:
            return False, "Flutter not working"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, "Flutter not installed"

def launch_web_demo():
    """Launch the web demo"""
    web_demo_path = Path("demo/web_demo.html")
    if web_demo_path.exists():
        file_url = f"file:///{web_demo_path.absolute()}"
        webbrowser.open(file_url)
        return True, f"Web demo opened in browser: {file_url}"
    else:
        return False, "Web demo file not found"

def launch_python_demo():
    """Launch the Python interactive demo"""
    demo_path = Path("run_python_demo_standalone.py")
    if demo_path.exists():
        try:
            subprocess.run([sys.executable, str(demo_path)], check=True)
            return True, "Python demo completed successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Python demo failed: {e}"
    else:
        return False, "Python demo file not found"

def launch_basic_gui():
    """Launch a basic Tkinter GUI"""
    try:
        import tkinter as tk
        from tkinter import messagebox, ttk
        
        # Create basic GUI
        root = tk.Tk()
        root.title("SafeErase - Basic Interface")
        root.geometry("600x400")
        
        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🔒 SafeErase", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status
        status_label = ttk.Label(main_frame, 
                                text="Secure Data Wiping Solution\nBasic Interface Mode")
        status_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Buttons
        def show_info():
            messagebox.showinfo("SafeErase Info", 
                              "SafeErase - Professional secure data wiping\n\n"
                              "Features:\n"
                              "• Multiple wiping algorithms\n"
                              "• Tamper-proof certificates\n"
                              "• Cross-platform support\n"
                              "• Industry compliance\n\n"
                              "For full functionality, install:\n"
                              "pip install customtkinter")
        
        def launch_web():
            success, message = launch_web_demo()
            if success:
                messagebox.showinfo("Web Demo", "Web demo opened in browser!")
            else:
                messagebox.showerror("Error", message)
        
        def launch_demo():
            messagebox.showinfo("Demo", "Running Python demo in terminal...")
            root.after(100, lambda: launch_python_demo())
        
        info_btn = ttk.Button(main_frame, text="📋 About SafeErase", command=show_info)
        info_btn.grid(row=2, column=0, padx=(0, 10), pady=5, sticky=tk.W+tk.E)
        
        web_btn = ttk.Button(main_frame, text="🌐 Web Demo", command=launch_web)
        web_btn.grid(row=2, column=1, padx=(10, 0), pady=5, sticky=tk.W+tk.E)
        
        demo_btn = ttk.Button(main_frame, text="🐍 Python Demo", command=launch_demo)
        demo_btn.grid(row=3, column=0, columnspan=2, pady=5, sticky=tk.W+tk.E)
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                                text="For full GUI experience, install dependencies:\n"
                                     "pip install customtkinter pillow",
                                font=("Arial", 9))
        instructions.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        root.mainloop()
        return True, "Basic GUI launched successfully"
        
    except ImportError:
        return False, "Tkinter not available"
    except Exception as e:
        return False, f"GUI launch failed: {e}"

def show_menu():
    """Show the launcher menu"""
    print("🚀 SafeErase Launcher Menu")
    print("-" * 30)
    print("1. 🌐 Web Demo (Browser)")
    print("2. 🐍 Python Interactive Demo")
    print("3. 🖥️ Basic GUI (Tkinter)")
    print("4. ⚡ CLI Tools Demo")
    print("5. 📊 System Status")
    print("6. 🔧 Install Dependencies")
    print("7. ❌ Exit")
    print()

def show_system_status():
    """Show system status and available components"""
    print("\n📊 SafeErase System Status")
    print("-" * 40)
    
    # Check Python
    print(f"Python: ✅ {sys.version}")
    
    # Check GUI options
    tkinter_ok, tkinter_msg = check_python_gui()
    print(f"Tkinter: {'✅' if tkinter_ok else '❌'} {tkinter_msg}")
    
    customtk_ok, customtk_msg = check_customtkinter()
    print(f"CustomTkinter: {'✅' if customtk_ok else '❌'} {customtk_msg}")
    
    flutter_ok, flutter_msg = check_flutter()
    print(f"Flutter: {'✅' if flutter_ok else '❌'} {flutter_msg}")
    
    # Check demo files
    web_demo_exists = Path("demo/web_demo.html").exists()
    print(f"Web Demo: {'✅' if web_demo_exists else '❌'} {'Available' if web_demo_exists else 'Not found'}")
    
    python_demo_exists = Path("run_python_demo_standalone.py").exists()
    print(f"Python Demo: {'✅' if python_demo_exists else '❌'} {'Available' if python_demo_exists else 'Not found'}")
    
    print(f"\n🎯 Recommended Action:")
    if customtk_ok:
        print("   Run full Python GUI: python python-ui/main.py")
    elif tkinter_ok:
        print("   Use basic GUI or install CustomTkinter")
    else:
        print("   Use web demo or install Python GUI dependencies")

def install_dependencies():
    """Install Python dependencies"""
    print("\n🔧 Installing SafeErase Dependencies")
    print("-" * 40)
    
    requirements = [
        "customtkinter>=5.2.0",
        "pillow>=10.0.0",
        "pyyaml>=6.0.0"
    ]
    
    print("Installing packages:")
    for req in requirements:
        print(f"  • {req}")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install"] + requirements, 
                      check=True)
        print("\n✅ Dependencies installed successfully!")
        print("You can now run: python python-ui/main.py")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Installation failed: {e}")
        print("Try running manually: pip install customtkinter pillow pyyaml")

def main():
    """Main launcher function"""
    print_banner()
    
    while True:
        show_menu()
        choice = input("Select option (1-7): ").strip()
        
        if choice == "1":
            print("\n🌐 Launching Web Demo...")
            success, message = launch_web_demo()
            print(f"{'✅' if success else '❌'} {message}")
            
        elif choice == "2":
            print("\n🐍 Launching Python Interactive Demo...")
            success, message = launch_python_demo()
            print(f"{'✅' if success else '❌'} {message}")
            
        elif choice == "3":
            print("\n🖥️ Launching Basic GUI...")
            success, message = launch_basic_gui()
            print(f"{'✅' if success else '❌'} {message}")
            
        elif choice == "4":
            print("\n⚡ Launching CLI Tools Demo...")
            try:
                subprocess.run([sys.executable, "demo_cli_tools.py"], check=True)
                print("✅ CLI Tools demo completed")
            except subprocess.CalledProcessError:
                print("❌ CLI Tools demo failed")
                
        elif choice == "5":
            show_system_status()
            
        elif choice == "6":
            install_dependencies()
            
        elif choice == "7":
            print("\n👋 Thank you for using SafeErase!")
            break
            
        else:
            print("❌ Invalid option. Please select 1-7.")
            
        input("\nPress Enter to continue...")
        print()

if __name__ == "__main__":
    main()
