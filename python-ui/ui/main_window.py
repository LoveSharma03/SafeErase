"""
Main Window - Primary GUI interface for SafeErase
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, ttk
from typing import Dict, List, Optional
import threading
import asyncio

from python_ui.ui.device_panel import DevicePanel
from python_ui.ui.operation_panel import OperationPanel
from python_ui.ui.certificate_panel import CertificatePanel
from python_ui.ui.settings_panel import SettingsPanel
from python_ui.ui.status_bar import StatusBar
from python_ui.utils.logger import get_logger

class MainWindow:
    """Main application window"""
    
    def __init__(self, controller, config):
        self.controller = controller
        self.config = config
        self.logger = get_logger("MainWindow")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("SafeErase - Secure Data Wiping Solution")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass  # Icon file not found
            
        # Initialize UI components
        self.setup_ui()
        self.setup_callbacks()
        
        # Start background thread for controller
        self.controller.start_background_thread()
        
        self.logger.info("Main window initialized")
        
    def setup_ui(self):
        """Set up the user interface"""
        # Configure grid weights
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create main menu
        self.create_menu()
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
        
    def create_menu(self):
        """Create the main menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Discover Devices", command=self.discover_devices)
        file_menu.add_separator()
        file_menu.add_command(label="Export Settings", command=self.export_settings)
        file_menu.add_command(label="Import Settings", command=self.import_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="System Information", command=self.show_system_info)
        tools_menu.add_command(label="View Logs", command=self.show_logs)
        tools_menu.add_separator()
        tools_menu.add_command(label="Verify Certificate", command=self.verify_certificate)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Manual", command=self.show_user_manual)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_sidebar(self):
        """Create the sidebar navigation"""
        self.sidebar = ctk.CTkFrame(self.root, width=200)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.sidebar.grid_propagate(False)
        
        # Logo/Title
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="🔒 SafeErase",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Navigation buttons
        self.nav_buttons = {}
        
        nav_items = [
            ("Devices", "🖥️", self.show_devices),
            ("Operations", "⚙️", self.show_operations),
            ("Certificates", "📜", self.show_certificates),
            ("Settings", "⚙️", self.show_settings),
        ]
        
        for name, icon, command in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{icon} {name}",
                command=command,
                width=160,
                height=40,
                font=ctk.CTkFont(size=14)
            )
            btn.pack(pady=5)
            self.nav_buttons[name] = btn
            
        # Set initial active button
        self.set_active_nav_button("Devices")
        
        # System status section
        status_frame = ctk.CTkFrame(self.sidebar)
        status_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        status_title = ctk.CTkLabel(
            status_frame,
            text="System Status",
            font=ctk.CTkFont(weight="bold")
        )
        status_title.pack(pady=(10, 5))
        
        self.admin_status = ctk.CTkLabel(status_frame, text="Admin: Checking...")
        self.admin_status.pack()
        
        self.device_count = ctk.CTkLabel(status_frame, text="Devices: 0")
        self.device_count.pack()
        
        # Update system status
        self.update_system_status()
        
    def create_main_content(self):
        """Create the main content area"""
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Create panels
        self.device_panel = DevicePanel(self.main_frame, self.controller)
        self.operation_panel = OperationPanel(self.main_frame, self.controller)
        self.certificate_panel = CertificatePanel(self.main_frame, self.controller)
        self.settings_panel = SettingsPanel(self.main_frame, self.config)
        
        # Show devices panel by default
        self.current_panel = self.device_panel
        self.device_panel.show()
        
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = StatusBar(self.root)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        
    def setup_callbacks(self):
        """Set up controller callbacks"""
        self.controller.set_device_discovered_callback(self.on_device_discovered)
        self.controller.set_operation_progress_callback(self.on_operation_progress)
        self.controller.set_operation_completed_callback(self.on_operation_completed)
        
        # Window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def set_active_nav_button(self, active_name: str):
        """Set the active navigation button"""
        for name, button in self.nav_buttons.items():
            if name == active_name:
                button.configure(fg_color=("gray75", "gray25"))
            else:
                button.configure(fg_color=("gray85", "gray15"))
                
    def show_panel(self, panel):
        """Show a specific panel"""
        if self.current_panel:
            self.current_panel.hide()
            
        self.current_panel = panel
        panel.show()
        
    # Navigation methods
    def show_devices(self):
        """Show devices panel"""
        self.set_active_nav_button("Devices")
        self.show_panel(self.device_panel)
        
    def show_operations(self):
        """Show operations panel"""
        self.set_active_nav_button("Operations")
        self.show_panel(self.operation_panel)
        
    def show_certificates(self):
        """Show certificates panel"""
        self.set_active_nav_button("Certificates")
        self.show_panel(self.certificate_panel)
        
    def show_settings(self):
        """Show settings panel"""
        self.set_active_nav_button("Settings")
        self.show_panel(self.settings_panel)
        
    # Menu command methods
    def discover_devices(self):
        """Discover storage devices"""
        def discover_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                devices = loop.run_until_complete(self.controller.discover_devices())
                
                # Update UI in main thread
                self.root.after(0, lambda: self.device_panel.update_devices(devices))
                self.root.after(0, self.update_system_status)
                
            except Exception as e:
                self.logger.error(f"Device discovery failed: {e}")
                self.root.after(0, lambda: messagebox.showerror(
                    "Discovery Error",
                    f"Failed to discover devices:\n{e}"
                ))
                
        # Run in background thread
        threading.Thread(target=discover_async, daemon=True).start()
        
    def export_settings(self):
        """Export application settings"""
        # TODO: Implement settings export
        messagebox.showinfo("Export Settings", "Settings export not yet implemented")
        
    def import_settings(self):
        """Import application settings"""
        # TODO: Implement settings import
        messagebox.showinfo("Import Settings", "Settings import not yet implemented")
        
    def show_system_info(self):
        """Show system information dialog"""
        status = self.controller.get_system_status()
        
        info_text = f"""System Information:
        
Platform: {status['platform']['platform']} {status['platform']['version']}
Architecture: {status['platform']['architecture']}
Admin Privileges: {'Yes' if status['admin_privileges'] else 'No'}

Devices: {status['devices_count']}
Active Operations: {status['active_operations']}
Completed Operations: {status['completed_operations']}
"""
        
        messagebox.showinfo("System Information", info_text)
        
    def show_logs(self):
        """Show application logs"""
        # TODO: Implement log viewer
        messagebox.showinfo("View Logs", "Log viewer not yet implemented")
        
    def verify_certificate(self):
        """Verify a certificate file"""
        # TODO: Implement certificate verification dialog
        messagebox.showinfo("Verify Certificate", "Certificate verification not yet implemented")
        
    def show_user_manual(self):
        """Show user manual"""
        # TODO: Open user manual
        messagebox.showinfo("User Manual", "User manual will open in browser")
        
    def show_about(self):
        """Show about dialog"""
        about_text = """SafeErase - Secure Data Wiping Solution

Version: 1.0.0
Platform: Python/Tkinter

A professional-grade secure data wiping solution for IT asset recyclers
and organizations requiring certified data destruction.

Features:
• Military-grade data destruction
• Tamper-proof certificates
• Cross-platform support
• Industry compliance

© 2024 SafeErase Project
"""
        messagebox.showinfo("About SafeErase", about_text)
        
    # Callback methods
    def on_device_discovered(self, device):
        """Handle device discovery event"""
        self.root.after(0, lambda: self.device_panel.add_device(device))
        self.root.after(0, self.update_system_status)
        
    def on_operation_progress(self, operation):
        """Handle operation progress update"""
        self.root.after(0, lambda: self.operation_panel.update_operation(operation))
        self.root.after(0, lambda: self.status_bar.set_status(
            f"Operation {operation.id[:8]}: {operation.progress:.1f}%"
        ))
        
    def on_operation_completed(self, operation):
        """Handle operation completion"""
        self.root.after(0, lambda: self.operation_panel.operation_completed(operation))
        self.root.after(0, lambda: self.status_bar.set_status(
            f"Operation {operation.id[:8]} completed: {operation.status}"
        ))
        
        if operation.status == 'completed':
            self.root.after(0, lambda: messagebox.showinfo(
                "Operation Complete",
                f"Wipe operation completed successfully!\n"
                f"Device: {operation.device_id}\n"
                f"Algorithm: {operation.algorithm}\n"
                f"Certificate generated."
            ))
        elif operation.status == 'failed':
            self.root.after(0, lambda: messagebox.showerror(
                "Operation Failed",
                f"Wipe operation failed:\n{operation.error_message}"
            ))
            
    def update_system_status(self):
        """Update system status display"""
        try:
            status = self.controller.get_system_status()
            
            # Update admin status
            admin_text = "Admin: Yes" if status['admin_privileges'] else "Admin: No"
            admin_color = "green" if status['admin_privileges'] else "red"
            self.admin_status.configure(text=admin_text, text_color=admin_color)
            
            # Update device count
            self.device_count.configure(text=f"Devices: {status['devices_count']}")
            
        except Exception as e:
            self.logger.error(f"Error updating system status: {e}")
            
    def on_closing(self):
        """Handle window closing event"""
        if messagebox.askokcancel("Quit", "Do you want to quit SafeErase?"):
            self.cleanup()
            self.root.destroy()
            
    def cleanup(self):
        """Cleanup window resources"""
        self.logger.info("Cleaning up main window...")
        
        # Cleanup panels
        if hasattr(self, 'device_panel'):
            self.device_panel.cleanup()
        if hasattr(self, 'operation_panel'):
            self.operation_panel.cleanup()
        if hasattr(self, 'certificate_panel'):
            self.certificate_panel.cleanup()
        if hasattr(self, 'settings_panel'):
            self.settings_panel.cleanup()
            
    def run(self):
        """Start the GUI event loop"""
        self.logger.info("Starting GUI event loop...")
        
        # Initial device discovery
        self.discover_devices()
        
        # Start the main loop
        self.root.mainloop()
