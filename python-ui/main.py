#!/usr/bin/env python3
"""
SafeErase Python UI - Main Application Entry Point
A professional tkinter-based GUI for the SafeErase secure data wiping solution
"""

import sys
import os
import asyncio
import threading
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import customtkinter as ctk
    import tkinter as tk
    from tkinter import messagebox, filedialog
    from PIL import Image, ImageTk
except ImportError as e:
    print(f"Error importing GUI libraries: {e}")
    print("Please install required packages: pip install -r requirements.txt")
    sys.exit(1)

from python_ui.core.app_controller import SafeEraseController
from python_ui.core.config_manager import ConfigManager
from python_ui.ui.main_window import MainWindow
from python_ui.utils.logger import setup_logger
from python_ui.utils.platform_utils import check_admin_privileges, get_platform_info

class SafeEraseApp:
    """Main SafeErase application class"""
    
    def __init__(self):
        self.logger = setup_logger("SafeEraseApp")
        self.config = ConfigManager()
        self.controller = None
        self.main_window = None
        
        # Set up CustomTkinter appearance
        ctk.set_appearance_mode("system")  # "system", "dark", "light"
        ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
        
    def check_prerequisites(self):
        """Check system prerequisites before starting"""
        self.logger.info("Checking system prerequisites...")
        
        # Check admin privileges
        if not check_admin_privileges():
            messagebox.showwarning(
                "Administrator Privileges Required",
                "SafeErase requires administrator privileges to access storage devices.\n\n"
                "Please restart the application as administrator."
            )
            return False
            
        # Check platform compatibility
        platform_info = get_platform_info()
        self.logger.info(f"Running on {platform_info['platform']} {platform_info['version']}")
        
        if platform_info['platform'] not in ['Windows', 'Linux', 'Darwin']:
            messagebox.showerror(
                "Unsupported Platform",
                f"SafeErase does not support {platform_info['platform']}.\n\n"
                "Supported platforms: Windows, Linux, macOS"
            )
            return False
            
        return True
        
    def initialize_controller(self):
        """Initialize the application controller"""
        try:
            self.controller = SafeEraseController(self.config)
            self.logger.info("Application controller initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize controller: {e}")
            messagebox.showerror(
                "Initialization Error",
                f"Failed to initialize SafeErase controller:\n{e}\n\n"
                "Please check the logs for more details."
            )
            return False
            
    def create_main_window(self):
        """Create and configure the main application window"""
        try:
            self.main_window = MainWindow(self.controller, self.config)
            self.logger.info("Main window created successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create main window: {e}")
            messagebox.showerror(
                "UI Error",
                f"Failed to create main window:\n{e}\n\n"
                "Please check the logs for more details."
            )
            return False
            
    def setup_exception_handling(self):
        """Set up global exception handling"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
                
            self.logger.error(
                "Uncaught exception",
                exc_info=(exc_type, exc_value, exc_traceback)
            )
            
            messagebox.showerror(
                "Unexpected Error",
                f"An unexpected error occurred:\n{exc_value}\n\n"
                "Please check the logs for more details."
            )
            
        sys.excepthook = handle_exception
        
    def run(self):
        """Main application entry point"""
        self.logger.info("Starting SafeErase Python UI...")
        
        # Set up exception handling
        self.setup_exception_handling()
        
        # Check prerequisites
        if not self.check_prerequisites():
            return 1
            
        # Initialize controller
        if not self.initialize_controller():
            return 1
            
        # Create main window
        if not self.create_main_window():
            return 1
            
        try:
            # Start the GUI event loop
            self.logger.info("Starting GUI event loop...")
            self.main_window.run()
            
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
            
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            return 1
            
        finally:
            # Cleanup
            self.cleanup()
            
        self.logger.info("SafeErase application terminated")
        return 0
        
    def cleanup(self):
        """Cleanup resources before exit"""
        self.logger.info("Cleaning up application resources...")
        
        if self.controller:
            self.controller.cleanup()
            
        if self.main_window:
            self.main_window.cleanup()

def main():
    """Main entry point"""
    app = SafeEraseApp()
    return app.run()

if __name__ == "__main__":
    sys.exit(main())
