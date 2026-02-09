#!/usr/bin/env python3
"""
Interactive Shell for AI-Assisted Linux Server Health & Log Analyzer
Allows users to query system health and logs using natural language.
"""

import sys
import time
import subprocess
import psutil
import socket
import json
import smtplib
from email.mime.text import MIMEText
from sna.utils.command_runner import CommandRunner
from sna.core.logs import LogAnalyzer
from sna.baseline.baseline_manager import BaselineManager
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import importlib
import matplotlib.pyplot as plt
import random
import shutil

class LogMonitorHandler(FileSystemEventHandler):
    def __init__(self, log_file):
        self.log_file = log_file

    def on_modified(self, event):
        if event.src_path == self.log_file:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                print("".join(lines[-10:]))  # Display the last 10 lines

class InteractiveShell:
    def __init__(self):
        self.command_runner = CommandRunner()
        self.log_analyzer = LogAnalyzer(self.command_runner)
        self.baseline_manager = BaselineManager()
        self.commands = {
            "show cpu usage": self.get_cpu_usage,
            "show system logs": self.get_system_logs,
            "help": self.show_help,
            "exit": self.exit_shell,
            "monitor logs": self.monitor_logs,
            "show memory usage": self.get_memory_usage,
            "show disk usage": self.get_disk_usage,
            "show network activity": self.get_network_activity,
            "check firewall": self.check_firewall,
            "scan vulnerabilities": self.scan_vulnerabilities,
            "export report": self.export_report,
            "send alert": self.send_alert,
            "switch user": self.switch_user,
            "show user roles": self.show_user_roles,
            "load plugin": self.load_plugin,
            "list plugins": self.list_plugins,
            "visualize cpu usage": self.visualize_cpu_usage,
            "set language": self.set_language,
            "backup config": self.backup_config,
            "restore config": self.restore_config,
            "add user": self.add_user,
            "remove user": self.remove_user,
            "list users": self.list_users,
            "run health check": self.run_health_check,
            "unload plugin": self.unload_plugin,
            "update plugin": self.update_plugin,
            "list backups": self.list_backups,
            "delete backup": self.delete_backup
        }
        self.user_roles = {"admin": ["all"], "viewer": ["show"]}
        self.current_user = "admin"  # Default user
        self.plugins = {}
        self.language = "en"  # Default language

    def start(self):
        print("Welcome to the Interactive Shell! Type 'help' for available commands.")
        while True:
            try:
                query = input("\n> ").strip().lower()
                self.handle_query(query)
            except KeyboardInterrupt:
                print("\nExiting... Goodbye!")
                break

    def handle_query(self, query):
        if query in self.commands:
            self.commands[query]()
        else:
            print("Unrecognized command. Type 'help' for a list of available commands.")

    def get_cpu_usage(self):
        print("Fetching CPU usage...")
        # Example: Replace with actual CPU usage logic
        output = self.command_runner.run_bash_script("system_health.sh")
        print(output or "No data available.")

    def get_system_logs(self):
        print("Fetching system logs...")
        logs = self.log_analyzer.collect_logs()
        print(logs or "No logs available.")

    def get_baseline(self):
        print("Fetching baseline data...")
        # Example: Replace with actual baseline logic
        print("Baseline data not implemented yet.")

    def show_help(self):
        print("Available commands:")
        for cmd in self.commands:
            print(f"  - {cmd}")

    def exit_shell(self):
        print("Exiting... Goodbye!")
        sys.exit(0)

    def monitor_logs(self):
        log_file = input("Enter the path to the log file to monitor: ").strip()
        print(f"Monitoring log file: {log_file}")
        event_handler = LogMonitorHandler(log_file)
        observer = Observer()
        observer.schedule(event_handler, path=log_file, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def get_memory_usage(self):
        print("Fetching memory usage...")
        # Example: Replace with actual memory usage logic
        output = self.command_runner.run_bash_script("system_health.sh")
        print(output or "No data available.")

    def get_disk_usage(self):
        print("Fetching disk usage...")
        # Example: Replace with actual disk usage logic
        output = self.command_runner.run_bash_script("system_health.sh")
        print(output or "No data available.")

    def get_network_activity(self):
        print("Fetching network activity...")
        # Example: Replace with actual network activity logic
        output = self.command_runner.run_bash_script("system_health.sh")
        print(output or "No data available.")

    def check_firewall(self):
        print("Checking firewall rules...")
        try:
            output = subprocess.check_output(["sudo", "iptables", "-L"], text=True)
            print(output)
        except Exception as e:
            print(f"Error checking firewall: {e}")

    def scan_vulnerabilities(self):
        print("Scanning for vulnerabilities...")
        try:
            output = subprocess.check_output(["sudo", "nmap", "--script", "vuln", "127.0.0.1"], text=True)
            print(output)
        except Exception as e:
            print(f"Error scanning vulnerabilities: {e}")

    def export_report(self):
        print("Exporting report...")
        # Example: Replace with actual report generation logic
        report = {
            "cpu_usage": "Normal",
            "memory_usage": "High",
            "disk_usage": "Normal",
            "logs": "No anomalies detected"
        }
        with open("report.json", "w") as f:
            json.dump(report, f, indent=4)
        print("Report exported to report.json")

    def send_alert(self):
        print("Sending alert...")
        # Example: Replace with actual alerting logic
        try:
            msg = MIMEText("System alert: High memory usage detected.")
            msg["Subject"] = "System Alert"
            msg["From"] = "admin@example.com"
            msg["To"] = "user@example.com"

            with smtplib.SMTP("smtp.example.com", 587) as server:
                server.starttls()
                server.login("admin@example.com", "password")
                server.send_message(msg)

            print("Alert sent successfully.")
        except Exception as e:
            print(f"Failed to send alert: {e}")

    def switch_user(self):
        user = input("Enter username (admin/viewer): ").strip()
        if user in self.user_roles:
            self.current_user = user
            print(f"Switched to user: {user}")
        else:
            print("Invalid user.")

    def show_user_roles(self):
        print(f"Current user: {self.current_user}")
        print(f"Roles: {self.user_roles.get(self.current_user, [])}")

    def load_plugin(self):
        plugin_name = input("Enter plugin name: ").strip()
        try:
            module = importlib.import_module(plugin_name)
            self.plugins[plugin_name] = module
            print(f"Plugin '{plugin_name}' loaded successfully.")
        except Exception as e:
            print(f"Failed to load plugin '{plugin_name}': {e}")

    def list_plugins(self):
        print("Loaded plugins:")
        for plugin in self.plugins:
            print(f"- {plugin}")

    def visualize_cpu_usage(self):
        print("Visualizing CPU usage...")
        # Example: Replace with actual real-time data
        cpu_usage = [random.randint(10, 90) for _ in range(10)]
        plt.plot(cpu_usage, label="CPU Usage (%)")
        plt.xlabel("Time")
        plt.ylabel("Usage (%)")
        plt.title("Real-Time CPU Usage")
        plt.legend()
        plt.show()

    def set_language(self):
        lang = input("Enter language code (en/es/fr): ").strip()
        if lang in ["en", "es", "fr"]:
            self.language = lang
            print(f"Language set to: {lang}")
        else:
            print("Unsupported language.")

    def backup_config(self):
        print("Backing up configuration...")
        try:
            shutil.copy("config.json", "config_backup.json")
            print("Configuration backed up successfully.")
        except Exception as e:
            print(f"Failed to back up configuration: {e}")

    def restore_config(self):
        print("Restoring configuration...")
        try:
            shutil.copy("config_backup.json", "config.json")
            print("Configuration restored successfully.")
        except Exception as e:
            print(f"Failed to restore configuration: {e}")

    def add_user(self):
        username = input("Enter the username to add: ").strip()
        if username in self.user_roles:
            print(f"User '{username}' already exists.")
        else:
            self.user_roles[username] = []
            print(f"User '{username}' added successfully.")

    def remove_user(self):
        username = input("Enter the username to remove: ").strip()
        if username in self.user_roles:
            del self.user_roles[username]
            print(f"User '{username}' removed successfully.")
        else:
            print(f"User '{username}' does not exist.")

    def list_users(self):
        print("Listing all users:")
        for user in self.user_roles:
            print(f"- {user}")

    def run_health_check(self):
        print("Running system health check...")
        health_report = {
            "cpu": self.get_cpu_usage(),
            "memory": self.get_memory_usage(),
            "disk": self.get_disk_usage(),
            "network": self.get_network_activity()
        }
        print("System Health Report:")
        for key, value in health_report.items():
            print(f"{key.capitalize()}: {value}")

    def unload_plugin(self):
        plugin_name = input("Enter the plugin name to unload: ").strip()
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            print(f"Plugin '{plugin_name}' unloaded successfully.")
        else:
            print(f"Plugin '{plugin_name}' is not loaded.")

    def update_plugin(self):
        plugin_name = input("Enter the plugin name to update: ").strip()
        if plugin_name in self.plugins:
            try:
                importlib.reload(self.plugins[plugin_name])
                print(f"Plugin '{plugin_name}' updated successfully.")
            except Exception as e:
                print(f"Failed to update plugin '{plugin_name}': {e}")
        else:
            print(f"Plugin '{plugin_name}' is not loaded.")

    def list_backups(self):
        print("Listing all backups:")
        backups = ["config_backup.json"]  # Example: Replace with dynamic listing
        for backup in backups:
            print(f"- {backup}")

    def delete_backup(self):
        backup_name = input("Enter the backup name to delete: ").strip()
        if backup_name == "config_backup.json":  # Example: Replace with dynamic check
            print(f"Backup '{backup_name}' deleted successfully.")
        else:
            print(f"Backup '{backup_name}' does not exist.")

    def get_ai_recommendations(self):
        print("Fetching AI-powered recommendations...")
        # Example: Replace with actual AI integration logic
        print("Recommendations:")
        print("- Optimize CPU-intensive processes.")
        print("- Schedule regular system audits.")

if __name__ == "__main__":
    shell = InteractiveShell()
    shell.start()