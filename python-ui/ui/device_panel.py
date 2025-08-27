"""
Device Panel - UI for device discovery and selection
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, ttk
from typing import List, Dict, Optional
import threading
import asyncio

from python_ui.utils.logger import get_logger

class DevicePanel:
    """Panel for device management and selection"""
    
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.logger = get_logger("DevicePanel")
        
        self.devices = {}
        self.selected_device = None
        
        self.create_ui()
        
    def create_ui(self):
        """Create the device panel UI"""
        # Main frame
        self.frame = ctk.CTkFrame(self.parent)
        
        # Title
        title = ctk.CTkLabel(
            self.frame,
            text="Storage Devices",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 10))
        
        # Toolbar
        toolbar = ctk.CTkFrame(self.frame)
        toolbar.pack(fill="x", padx=20, pady=(0, 10))
        
        refresh_btn = ctk.CTkButton(
            toolbar,
            text="🔄 Refresh Devices",
            command=self.refresh_devices,
            width=150
        )
        refresh_btn.pack(side="left", padx=(0, 10))
        
        self.device_count_label = ctk.CTkLabel(
            toolbar,
            text="Devices found: 0"
        )
        self.device_count_label.pack(side="left")
        
        # Filter options
        filter_frame = ctk.CTkFrame(toolbar)
        filter_frame.pack(side="right")
        
        self.show_system_var = tk.BooleanVar(value=False)
        system_check = ctk.CTkCheckBox(
            filter_frame,
            text="Show System Disks",
            variable=self.show_system_var,
            command=self.update_device_list
        )
        system_check.pack(side="left", padx=5)
        
        self.show_removable_var = tk.BooleanVar(value=True)
        removable_check = ctk.CTkCheckBox(
            filter_frame,
            text="Show Removable",
            variable=self.show_removable_var,
            command=self.update_device_list
        )
        removable_check.pack(side="left", padx=5)
        
        # Device list
        list_frame = ctk.CTkFrame(self.frame)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Create treeview for device list
        self.create_device_tree(list_frame)
        
        # Device details
        details_frame = ctk.CTkFrame(self.frame)
        details_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        details_title = ctk.CTkLabel(
            details_frame,
            text="Device Details",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        details_title.pack(pady=(10, 5))
        
        self.details_text = ctk.CTkTextbox(details_frame, height=150)
        self.details_text.pack(fill="x", padx=10, pady=(0, 10))
        
        # Action buttons
        action_frame = ctk.CTkFrame(self.frame)
        action_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.wipe_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ Start Wipe Operation",
            command=self.start_wipe_operation,
            state="disabled",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.wipe_btn.pack(side="right", padx=(10, 0))
        
        info_btn = ctk.CTkButton(
            action_frame,
            text="ℹ️ Device Information",
            command=self.show_device_info,
            state="disabled",
            width=150
        )
        info_btn.pack(side="right")
        self.info_btn = info_btn
        
    def create_device_tree(self, parent):
        """Create the device tree view"""
        # Create frame for treeview and scrollbar
        tree_frame = ctk.CTkFrame(parent)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create treeview
        columns = ("Name", "Size", "Type", "Interface", "Status")
        self.device_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.device_tree.heading("Name", text="Device Name")
        self.device_tree.heading("Size", text="Size")
        self.device_tree.heading("Type", text="Type")
        self.device_tree.heading("Interface", text="Interface")
        self.device_tree.heading("Status", text="Status")
        
        self.device_tree.column("Name", width=300)
        self.device_tree.column("Size", width=100)
        self.device_tree.column("Type", width=120)
        self.device_tree.column("Interface", width=100)
        self.device_tree.column("Status", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.device_tree.yview)
        self.device_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.device_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.device_tree.bind("<<TreeviewSelect>>", self.on_device_select)
        
    def refresh_devices(self):
        """Refresh the device list"""
        def discover_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                devices = loop.run_until_complete(self.controller.discover_devices())
                
                # Update UI in main thread
                self.parent.after(0, lambda: self.update_devices(devices))
                
            except Exception as e:
                self.logger.error(f"Device discovery failed: {e}")
                self.parent.after(0, lambda: messagebox.showerror(
                    "Discovery Error",
                    f"Failed to discover devices:\n{e}"
                ))
                
        # Run in background thread
        threading.Thread(target=discover_async, daemon=True).start()
        
    def update_devices(self, devices: List):
        """Update the device list"""
        self.devices = {device.id: device for device in devices}
        self.update_device_list()
        self.device_count_label.configure(text=f"Devices found: {len(devices)}")
        
    def update_device_list(self):
        """Update the device tree view"""
        # Clear existing items
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)
            
        # Filter devices
        filtered_devices = []
        for device in self.devices.values():
            if not self.show_system_var.get() and device.is_system_disk:
                continue
            if not self.show_removable_var.get() and device.is_removable:
                continue
            filtered_devices.append(device)
            
        # Add devices to tree
        for device in filtered_devices:
            status = self.get_device_status(device)
            
            item_id = self.device_tree.insert("", "end", values=(
                device.name,
                device.get_size_formatted(),
                device.device_type,
                device.interface,
                status
            ))
            
            # Store device ID with tree item
            self.device_tree.set(item_id, "device_id", device.id)
            
            # Color code based on status
            if device.is_system_disk:
                self.device_tree.item(item_id, tags=("system",))
            elif device.is_removable:
                self.device_tree.item(item_id, tags=("removable",))
            else:
                self.device_tree.item(item_id, tags=("normal",))
                
        # Configure tags
        self.device_tree.tag_configure("system", background="#ffcccc")
        self.device_tree.tag_configure("removable", background="#ffffcc")
        self.device_tree.tag_configure("normal", background="white")
        
    def get_device_status(self, device) -> str:
        """Get device status string"""
        status_parts = []
        
        if device.is_system_disk:
            status_parts.append("⚠️ SYSTEM")
        if device.is_removable:
            status_parts.append("🔌 REMOVABLE")
        if device.supports_secure_erase:
            status_parts.append("🔒 SECURE ERASE")
            
        return " | ".join(status_parts) if status_parts else "Ready"
        
    def on_device_select(self, event):
        """Handle device selection"""
        selection = self.device_tree.selection()
        if not selection:
            self.selected_device = None
            self.wipe_btn.configure(state="disabled")
            self.info_btn.configure(state="disabled")
            self.details_text.delete("1.0", "end")
            return
            
        # Get selected device
        item = selection[0]
        device_id = self.device_tree.item(item)["values"]
        
        # Find device by matching name (simplified)
        device_name = self.device_tree.item(item)["values"][0]
        self.selected_device = None
        for device in self.devices.values():
            if device.name == device_name:
                self.selected_device = device
                break
                
        if self.selected_device:
            self.wipe_btn.configure(state="normal")
            self.info_btn.configure(state="normal")
            self.update_device_details()
        else:
            self.wipe_btn.configure(state="disabled")
            self.info_btn.configure(state="disabled")
            
    def update_device_details(self):
        """Update device details display"""
        if not self.selected_device:
            return
            
        device = self.selected_device
        details = f"""Device Information:
Name: {device.name}
Path: {device.path}
Size: {device.get_size_formatted()} ({device.size:,} bytes)
Type: {device.device_type}
Interface: {device.interface}
Model: {device.model}
Serial: {device.serial_number}
Firmware: {device.firmware_version}

Capabilities:
• Removable: {'Yes' if device.is_removable else 'No'}
• System Disk: {'Yes' if device.is_system_disk else 'No'}
• Secure Erase: {'Yes' if device.supports_secure_erase else 'No'}
• HPA/DCO Support: {'Yes' if device.supports_hpa_dco else 'No'}

Health Status: {device.health_status}
"""
        
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", details)
        
    def show_device_info(self):
        """Show detailed device information dialog"""
        if not self.selected_device:
            return
            
        device = self.selected_device
        details = self.controller.get_device_details(device.id)
        
        if details:
            info_window = ctk.CTkToplevel(self.parent)
            info_window.title(f"Device Information - {device.name}")
            info_window.geometry("600x500")
            
            # Create scrollable text widget
            text_widget = ctk.CTkTextbox(info_window)
            text_widget.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Format detailed information
            info_text = f"""Device Information: {device.name}

Basic Information:
• ID: {details['basic_info']['id']}
• Name: {details['basic_info']['name']}
• Path: {details['basic_info']['path']}
• Size: {details['basic_info']['size_formatted']}
• Type: {details['basic_info']['type']}
• Interface: {details['basic_info']['interface']}

Capabilities:
• Removable: {'Yes' if details['capabilities']['is_removable'] else 'No'}
• System Disk: {'Yes' if details['capabilities']['is_system_disk'] else 'No'}
• Secure Erase: {'Yes' if details['capabilities']['supports_secure_erase'] else 'No'}
• HPA/DCO: {'Yes' if details['capabilities']['supports_hpa_dco'] else 'No'}

Hardware Information:
• Serial Number: {details['hardware_info']['serial_number']}
• Model: {details['hardware_info']['model']}
• Firmware: {details['hardware_info']['firmware_version']}
• Health: {details['hardware_info']['health_status']}
"""
            
            text_widget.insert("1.0", info_text)
            text_widget.configure(state="disabled")
            
    def start_wipe_operation(self):
        """Start wipe operation for selected device"""
        if not self.selected_device:
            return
            
        device = self.selected_device
        
        # Show warning for system disks
        if device.is_system_disk:
            result = messagebox.askyesno(
                "System Disk Warning",
                f"⚠️ WARNING: '{device.name}' appears to be a system disk!\n\n"
                "Wiping this device will destroy the operating system and all data.\n"
                "This action cannot be undone.\n\n"
                "Are you absolutely sure you want to continue?",
                icon="warning"
            )
            if not result:
                return
                
        # Import and show wipe configuration dialog
        from python_ui.ui.wipe_dialog import WipeConfigDialog
        
        dialog = WipeConfigDialog(self.parent, self.controller, device)
        result = dialog.show()
        
        if result:
            # Switch to operations panel to monitor progress
            # This would be handled by the main window
            pass
            
    def add_device(self, device):
        """Add a new device to the list"""
        self.devices[device.id] = device
        self.update_device_list()
        self.device_count_label.configure(text=f"Devices found: {len(self.devices)}")
        
    def show(self):
        """Show the device panel"""
        self.frame.pack(fill="both", expand=True)
        
    def hide(self):
        """Hide the device panel"""
        self.frame.pack_forget()
        
    def cleanup(self):
        """Cleanup panel resources"""
        self.logger.info("Cleaning up device panel...")
        self.devices.clear()
