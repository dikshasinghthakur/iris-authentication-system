"""
Iris Authentication System - Desktop GUI with Tkinter
Cross-platform graphical interface with visualizations
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import numpy as np
import requests
import base64
import threading
from datetime import datetime
import json
import sqlite3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Configuration
API_URL = "http://localhost:5000"
DB_PATH = "../database/iris_auth.db"

class IrisAuthGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Iris Authentication System")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e1e")
        
        # Configure style
        self.setup_styles()
        
        # Camera variables
        self.camera = None
        self.is_capturing = False
        self.captured_frame = None
        
        # Main container
        self.create_main_layout()
        
    def setup_styles(self):
        """Setup ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Color scheme
        style.configure('TButton', font=('Arial', 10), padding=10)
        style.configure('TLabel', background='#1e1e1e', foreground='#ffffff', font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), foreground='#00d4ff')
        style.configure('Title.TLabel', font=('Arial', 24, 'bold'), foreground='#00d4ff')
        
    def create_main_layout(self):
        """Create main layout with navigation"""
        # Top header
        self.header_frame = tk.Frame(self.root, bg="#0a0a0a", height=80)
        self.header_frame.pack(fill=tk.X, padx=0, pady=0)
        self.header_frame.pack_propagate(False)
        
        header_title = ttk.Label(self.header_frame, text="🔐 Iris Authentication System", style='Title.TLabel')
        header_title.pack(pady=15)
        
        # Main content area with notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_enroll_tab()
        self.create_verify_tab()
        self.create_identify_tab()
        self.create_manage_tab()
        self.create_analytics_tab()
        
    def create_enroll_tab(self):
        """Create enrollment tab with camera and form"""
        enroll_frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(enroll_frame, text="📝 Enroll")
        
        # Left side - Camera
        left_frame = tk.Frame(enroll_frame, bg="#2a2a2a", width=500, height=600)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        ttk.Label(left_frame, text="Camera Feed", style='Header.TLabel').pack(pady=10)
        
        self.enroll_canvas = tk.Canvas(left_frame, bg='#000000', width=400, height=400, highlightthickness=2, highlightbackground='#00d4ff')
        self.enroll_canvas.pack(pady=20)
        
        button_frame = tk.Frame(left_frame, bg="#2a2a2a")
        button_frame.pack(fill=tk.X, pady=10)
        
        self.enroll_start_btn = ttk.Button(button_frame, text="📷 Start Camera", command=self.start_enroll_camera)
        self.enroll_start_btn.pack(side=tk.LEFT, padx=5)
        
        self.enroll_capture_btn = ttk.Button(button_frame, text="📸 Capture", command=self.capture_enroll_image)
        self.enroll_capture_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="⏹️ Stop", command=self.stop_enroll_camera).pack(side=tk.LEFT, padx=5)
        
        # Right side - Form
        right_frame = tk.Frame(enroll_frame, bg="#2a2a2a", width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        ttk.Label(right_frame, text="User Information", style='Header.TLabel').pack(pady=10)
        
        # Username
        ttk.Label(right_frame, text="Username:").pack(anchor=tk.W, pady=(10, 5))
        self.enroll_username = ttk.Entry(right_frame, width=30)
        self.enroll_username.pack(anchor=tk.W, padx=10, pady=(0, 10))
        
        # Email
        ttk.Label(right_frame, text="Email:").pack(anchor=tk.W, pady=(10, 5))
        self.enroll_email = ttk.Entry(right_frame, width=30)
        self.enroll_email.pack(anchor=tk.W, padx=10, pady=(0, 10))
        
        # Status label
        ttk.Label(right_frame, text="Status: Ready", style='Header.TLabel').pack(pady=20)
        self.enroll_status = tk.Label(right_frame, text="", bg="#2a2a2a", fg="#00d4ff", wraplength=350, justify=tk.LEFT)
        self.enroll_status.pack(pady=10)
        
        # Enrollment info
        ttk.Label(right_frame, text="Enrollment Steps:", style='Header.TLabel').pack(pady=(20, 10))
        steps_text = """1. Enter your username and email
2. Click "Start Camera"
3. Position your eye in center
4. Click "Capture" to take photo
5. Click "Enroll" to register
        
⚠️ Requirements:
• Good lighting
• Direct eye to camera
• 200×200 pixel iris
• Clear focus"""
        
        steps_label = tk.Label(right_frame, text=steps_text, bg="#2a2a2a", fg="#ffffff", justify=tk.LEFT, font=('Courier', 9))
        steps_label.pack(pady=10, padx=10)
        
        ttk.Button(right_frame, text="✅ Enroll User", command=self.enroll_user).pack(pady=20)
        
    def create_verify_tab(self):
        """Create verification/authentication tab"""
        verify_frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(verify_frame, text="🔑 Verify")
        
        # Left - Camera
        left_frame = tk.Frame(verify_frame, bg="#2a2a2a", width=500)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        ttk.Label(left_frame, text="Camera Feed", style='Header.TLabel').pack(pady=10)
        
        self.verify_canvas = tk.Canvas(left_frame, bg='#000000', width=400, height=400, highlightthickness=2, highlightbackground='#00d4ff')
        self.verify_canvas.pack(pady=20)
        
        button_frame = tk.Frame(left_frame, bg="#2a2a2a")
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="📷 Start Camera", command=self.start_verify_camera).pack(side=tk.LEFT, padx=5)
        self.verify_capture_btn = ttk.Button(button_frame, text="📸 Capture", command=self.capture_verify_image)
        self.verify_capture_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⏹️ Stop", command=self.stop_verify_camera).pack(side=tk.LEFT, padx=5)
        
        # Right - Form
        right_frame = tk.Frame(verify_frame, bg="#2a2a2a", width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        ttk.Label(right_frame, text="User Verification", style='Header.TLabel').pack(pady=10)
        
        ttk.Label(right_frame, text="Username:").pack(anchor=tk.W, pady=(10, 5))
        self.verify_username = ttk.Entry(right_frame, width=30)
        self.verify_username.pack(anchor=tk.W, padx=10, pady=(0, 20))
        
        # Confidence bar
        ttk.Label(right_frame, text="Match Confidence:", style='Header.TLabel').pack(pady=(20, 10))
        
        self.verify_progress = ttk.Progressbar(right_frame, length=300, mode='determinate')
        self.verify_progress.pack(pady=10)
        
        self.verify_score_label = tk.Label(right_frame, text="Score: --", bg="#2a2a2a", fg="#00d4ff", font=('Courier', 12))
        self.verify_score_label.pack(pady=10)
        
        # Result display
        self.verify_result = tk.Label(right_frame, text="", bg="#2a2a2a", fg="#00ff00", font=('Arial', 14, 'bold'), wraplength=350)
        self.verify_result.pack(pady=20)
        
        ttk.Button(right_frame, text="🔐 Verify User", command=self.verify_user).pack(pady=20)
        
    def create_identify_tab(self):
        """Create identification tab (1:N matching)"""
        identify_frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(identify_frame, text="🔍 Identify")
        
        # Left - Camera
        left_frame = tk.Frame(identify_frame, bg="#2a2a2a", width=500)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        ttk.Label(left_frame, text="Camera Feed", style='Header.TLabel').pack(pady=10)
        
        self.identify_canvas = tk.Canvas(left_frame, bg='#000000', width=400, height=400, highlightthickness=2, highlightbackground='#00d4ff')
        self.identify_canvas.pack(pady=20)
        
        button_frame = tk.Frame(left_frame, bg="#2a2a2a")
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="📷 Start Camera", command=self.start_identify_camera).pack(side=tk.LEFT, padx=5)
        self.identify_capture_btn = ttk.Button(button_frame, text="📸 Capture", command=self.capture_identify_image)
        self.identify_capture_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⏹️ Stop", command=self.stop_identify_camera).pack(side=tk.LEFT, padx=5)
        
        # Right - Results
        right_frame = tk.Frame(identify_frame, bg="#2a2a2a", width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        ttk.Label(right_frame, text="User Identification", style='Header.TLabel').pack(pady=10)
        
        ttk.Label(right_frame, text="Search Mode: 1:N Database Matching", style='Header.TLabel').pack(pady=10)
        
        # Result display
        self.identify_result = tk.Label(right_frame, text="", bg="#2a2a2a", fg="#00ff00", font=('Arial', 12), wraplength=350, justify=tk.LEFT)
        self.identify_result.pack(pady=20, padx=10)
        
        # Matches list
        ttk.Label(right_frame, text="Top Matches:", style='Header.TLabel').pack(pady=(20, 10))
        
        self.identify_listbox = tk.Listbox(right_frame, height=8, bg="#1a1a1a", fg="#00d4ff", font=('Courier', 9))
        self.identify_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Button(right_frame, text="🔍 Identify", command=self.identify_user).pack(pady=20)
        
    def create_manage_tab(self):
        """Create user management tab"""
        manage_frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(manage_frame, text="👥 Manage")
        
        # Title
        ttk.Label(manage_frame, text="User Management", style='Header.TLabel').pack(pady=10)
        
        # User list
        list_frame = tk.Frame(manage_frame, bg="#2a2a2a")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(list_frame, text="Enrolled Users:", style='Header.TLabel').pack(anchor=tk.W, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.manage_listbox = tk.Listbox(list_frame, height=15, bg="#1a1a1a", fg="#00d4ff", font=('Courier', 9), yscrollcommand=scrollbar.set)
        self.manage_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.manage_listbox.yview)
        
        # Buttons
        button_frame = tk.Frame(manage_frame, bg="#1e1e1e")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="🔄 Refresh", command=self.refresh_user_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="👤 View Details", command=self.view_user_details).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Delete User", command=self.delete_selected_user).pack(side=tk.LEFT, padx=5)
        
        # Load initial data
        self.refresh_user_list()
        
    def create_analytics_tab(self):
        """Create analytics and statistics tab"""
        analytics_frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(analytics_frame, text="📊 Analytics")
        
        # Title
        ttk.Label(analytics_frame, text="System Analytics & Statistics", style='Header.TLabel').pack(pady=10)
        
        # Stats frame
        stats_frame = tk.Frame(analytics_frame, bg="#2a2a2a")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(stats_frame, text="System Statistics", style='Header.TLabel').pack(pady=10)
        
        self.stats_label = tk.Label(stats_frame, text="Loading...", bg="#2a2a2a", fg="#00d4ff", font=('Courier', 10), justify=tk.LEFT)
        self.stats_label.pack(pady=10, padx=10)
        
        # Charts frame
        charts_frame = tk.Frame(analytics_frame, bg="#2a2a2a")
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.figure = Figure(figsize=(12, 4), dpi=100, facecolor='#2a2a2a')
        self.canvas = FigureCanvasTkAgg(self.figure, master=charts_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(analytics_frame, text="🔄 Refresh Analytics", command=self.refresh_analytics).pack(pady=10)
        
        # Initial load
        self.refresh_analytics()
        
    # ===================== CAMERA OPERATIONS =====================
    
    def start_camera(self, canvas_widget):
        """Start camera capture"""
        self.camera = cv2.VideoCapture(0)
        self.is_capturing = True
        self.update_camera_feed(canvas_widget)
        
    def stop_camera(self):
        """Stop camera capture"""
        self.is_capturing = False
        if self.camera:
            self.camera.release()
            
    def update_camera_feed(self, canvas_widget):
        """Update camera feed on canvas"""
        if self.is_capturing and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                # Resize and process
                frame = cv2.resize(frame, (400, 400))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Add center guide
                h, w = frame.shape[:2]
                cv2.circle(frame, (w//2, h//2), 100, (0, 255, 0), 2)
                cv2.circle(frame, (w//2, h//2), 120, (0, 255, 0), 2)
                
                # Convert to PIL and display
                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image)
                canvas_widget.create_image(0, 0, anchor=tk.NW, image=photo)
                canvas_widget.photo = photo
                
            self.root.after(30, lambda: self.update_camera_feed(canvas_widget))
    
    def start_enroll_camera(self):
        """Start enrollment camera"""
        threading.Thread(target=lambda: self.start_camera(self.enroll_canvas), daemon=True).start()
        
    def stop_enroll_camera(self):
        """Stop enrollment camera"""
        self.stop_camera()
        
    def capture_enroll_image(self):
        """Capture enrollment image"""
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                self.captured_frame = frame
                self.enroll_status.config(text="✓ Image captured! Click 'Enroll User' to register.", fg="#00ff00")
    
    def start_verify_camera(self):
        """Start verification camera"""
        threading.Thread(target=lambda: self.start_camera(self.verify_canvas), daemon=True).start()
        
    def stop_verify_camera(self):
        """Stop verification camera"""
        self.stop_camera()
        
    def capture_verify_image(self):
        """Capture verification image"""
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                self.captured_frame = frame
                self.verify_score_label.config(text="Score: Image captured!")
    
    def start_identify_camera(self):
        """Start identification camera"""
        threading.Thread(target=lambda: self.start_camera(self.identify_canvas), daemon=True).start()
        
    def stop_identify_camera(self):
        """Stop identification camera"""
        self.stop_camera()
        
    def capture_identify_image(self):
        """Capture identification image"""
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                self.captured_frame = frame
                self.identify_result.config(text="✓ Image captured! Click 'Identify' to search.", fg="#00ff00")
    
    # ===================== API OPERATIONS =====================
    
    def enroll_user(self):
        """Enroll new user via API"""
        username = self.enroll_username.get()
        email = self.enroll_email.get()
        
        if not username or not email:
            messagebox.showerror("Error", "Please enter username and email")
            return
            
        if self.captured_frame is None:
            messagebox.showerror("Error", "Please capture an iris image first")
            return
        
        # Convert image to base64
        _, buffer = cv2.imencode('.jpg', self.captured_frame)
        image_base64 = base64.b64encode(buffer).decode()
        
        # Send to API
        self.enroll_status.config(text="⏳ Enrolling user...", fg="#ffaa00")
        self.root.update()
        
        def send_request():
            try:
                response = requests.post(f"{API_URL}/enroll", json={
                    'username': username,
                    'email': email,
                    'image': image_base64
                })
                
                if response.status_code == 200:
                    result = response.json()
                    self.enroll_status.config(text=f"✓ {result['message']}\nFeatures: {result['features_extracted']}", fg="#00ff00")
                    messagebox.showinfo("Success", f"User {username} enrolled successfully!")
                    self.enroll_username.delete(0, tk.END)
                    self.enroll_email.delete(0, tk.END)
                    self.captured_frame = None
                else:
                    error = response.json().get('error', 'Unknown error')
                    self.enroll_status.config(text=f"✗ Error: {error}", fg="#ff0000")
                    messagebox.showerror("Error", error)
            except Exception as e:
                self.enroll_status.config(text=f"✗ Connection error: {str(e)}", fg="#ff0000")
                messagebox.showerror("Error", f"Connection error: {str(e)}")
        
        threading.Thread(target=send_request, daemon=True).start()
    
    def verify_user(self):
        """Verify user via API"""
        username = self.verify_username.get()
        
        if not username:
            messagebox.showerror("Error", "Please enter username")
            return
            
        if self.captured_frame is None:
            messagebox.showerror("Error", "Please capture an iris image first")
            return
        
        # Convert image to base64
        _, buffer = cv2.imencode('.jpg', self.captured_frame)
        image_base64 = base64.b64encode(buffer).decode()
        
        # Send to API
        self.verify_score_label.config(text="⏳ Verifying...")
        self.verify_result.config(text="Processing...", fg="#ffaa00")
        self.root.update()
        
        def send_request():
            try:
                response = requests.post(f"{API_URL}/verify", json={
                    'username': username,
                    'image': image_base64
                })
                
                if response.status_code == 200:
                    result = response.json()
                    similarity = result['similarity']
                    success = result['success']
                    
                    self.verify_progress.config(value=similarity * 100)
                    self.verify_score_label.config(text=f"Score: {similarity:.4f} / {result['threshold']}", fg="#00d4ff")
                    
                    if success:
                        self.verify_result.config(text="✓ ACCESS GRANTED\nAuthentication successful!", fg="#00ff00")
                    else:
                        self.verify_result.config(text="✗ ACCESS DENIED\nAuthentication failed!", fg="#ff0000")
                else:
                    error = response.json().get('error', 'Unknown error')
                    self.verify_result.config(text=f"✗ Error: {error}", fg="#ff0000")
            except Exception as e:
                self.verify_result.config(text=f"✗ Error: {str(e)}", fg="#ff0000")
        
        threading.Thread(target=send_request, daemon=True).start()
    
    def identify_user(self):
        """Identify user via API"""
        if self.captured_frame is None:
            messagebox.showerror("Error", "Please capture an iris image first")
            return
        
        # Convert image to base64
        _, buffer = cv2.imencode('.jpg', self.captured_frame)
        image_base64 = base64.b64encode(buffer).decode()
        
        # Send to API
        self.identify_result.config(text="⏳ Searching database...", fg="#ffaa00")
        self.identify_listbox.delete(0, tk.END)
        self.root.update()
        
        def send_request():
            try:
                response = requests.post(f"{API_URL}/identify", json={
                    'image': image_base64
                })
                
                if response.status_code == 200:
                    result = response.json()
                    best_match = result['best_match']
                    success = result['success']
                    
                    if success:
                        self.identify_result.config(
                            text=f"✓ IDENTIFIED\n\nUser: {best_match['username']}\nEmail: {best_match['email']}\nConfidence: {best_match['similarity']:.4f}",
                            fg="#00ff00"
                        )
                    else:
                        self.identify_result.config(
                            text=f"? NO MATCH\n\nClosest: {best_match['username']}\nConfidence: {best_match['similarity']:.4f}\n(Below threshold)",
                            fg="#ffaa00"
                        )
                    
                    # Show all matches
                    for i, match in enumerate(result['all_matches'][:5], 1):
                        self.identify_listbox.insert(tk.END, f"{i}. {match['username']}: {match['similarity']:.4f}")
                        
                else:
                    error = response.json().get('error', 'Unknown error')
                    self.identify_result.config(text=f"✗ Error: {error}", fg="#ff0000")
            except Exception as e:
                self.identify_result.config(text=f"✗ Error: {str(e)}", fg="#ff0000")
        
        threading.Thread(target=send_request, daemon=True).start()
    
    # ===================== MANAGEMENT OPERATIONS =====================
    
    def refresh_user_list(self):
        """Refresh enrolled users list"""
        self.manage_listbox.delete(0, tk.END)
        
        def fetch_users():
            try:
                response = requests.get(f"{API_URL}/users")
                if response.status_code == 200:
                    users = response.json()['users']
                    for user in users:
                        self.manage_listbox.insert(tk.END, f"{user['username']} ({user['email']}) - {user['access_count']} accesses")
            except Exception as e:
                self.manage_listbox.insert(tk.END, f"Error: {str(e)}")
        
        threading.Thread(target=fetch_users, daemon=True).start()
    
    def view_user_details(self):
        """View selected user details"""
        selection = self.manage_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        # Get username from selection
        selected_text = self.manage_listbox.get(selection[0])
        username = selected_text.split(' (')[0]
        
        # Fetch and display details
        try:
            response = requests.get(f"{API_URL}/users")
            if response.status_code == 200:
                users = response.json()['users']
                user = next((u for u in users if u['username'] == username), None)
                if user:
                    details = f"Username: {user['username']}\nEmail: {user['email']}\nEnrolled: {user['enrollment_date']}\nLast Access: {user['last_access']}\nAccess Count: {user['access_count']}\nStatus: {user['status']}"
                    messagebox.showinfo("User Details", details)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def delete_selected_user(self):
        """Delete selected user"""
        selection = self.manage_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        selected_text = self.manage_listbox.get(selection[0])
        username = selected_text.split(' (')[0]
        
        if messagebox.askyesno("Confirm", f"Delete user '{username}'?"):
            try:
                response = requests.get(f"{API_URL}/users")
                users = response.json()['users']
                user = next((u for u in users if u['username'] == username), None)
                
                if user:
                    delete_response = requests.delete(f"{API_URL}/delete/{user['user_id']}")
                    if delete_response.status_code == 200:
                        messagebox.showinfo("Success", f"User {username} deleted")
                        self.refresh_user_list()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    # ===================== ANALYTICS OPERATIONS =====================
    
    def refresh_analytics(self):
        """Refresh analytics and statistics"""
        def fetch_stats():
            try:
                response = requests.get(f"{API_URL}/stats")
                if response.status_code == 200:
                    stats = response.json()
                    
                    # Update stats label
                    stats_text = f"""
Total Users: {stats['total_users']}
Total Authentications: {stats['total_authentications']}
Authentication Success Rate: {stats['authentication_success_rate']:.1f}%
Total Identifications: {stats['total_identifications']}
Identification Success Rate: {stats['identification_success_rate']:.1f}%
Average Similarity Score: {stats['average_similarity']:.4f}
                    """
                    self.stats_label.config(text=stats_text.strip())
                    
                    # Create charts
                    self.create_charts(stats)
            except Exception as e:
                self.stats_label.config(text=f"Error: {str(e)}")
        
        threading.Thread(target=fetch_stats, daemon=True).start()
    
    def create_charts(self, stats):
        """Create analytics charts"""
        self.figure.clear()
        
        # Chart 1: Success rates
        ax1 = self.figure.add_subplot(131)
        categories = ['Auth', 'ID']
        rates = [stats['authentication_success_rate'], stats['identification_success_rate']]
        colors = ['#00ff00', '#00d4ff']
        ax1.bar(categories, rates, color=colors)
        ax1.set_ylabel('Success Rate (%)', color='#00d4ff')
        ax1.set_title('Success Rates', color='#00d4ff')
        ax1.set_ylim(0, 100)
        ax1.set_facecolor('#2a2a2a')
        ax1.tick_params(colors='#00d4ff')
        
        # Chart 2: Activity breakdown
        ax2 = self.figure.add_subplot(132)
        activities = [stats['total_authentications'], stats['total_identifications']]
        ax2.pie(activities, labels=['Authentications', 'Identifications'], autopct='%1.1f%%', colors=['#00d4ff', '#00ff00'])
        ax2.set_title('Activity Breakdown', color='#00d4ff')
        ax2.set_facecolor('#2a2a2a')
        
        # Chart 3: User stats
        ax3 = self.figure.add_subplot(133)
        ax3.barh(['Enrolled Users'], [stats['total_users']], color='#ff00ff')
        ax3.set_xlabel('Count', color='#00d4ff')
        ax3.set_title('User Statistics', color='#00d4ff')
        ax3.set_facecolor('#2a2a2a')
        ax3.tick_params(colors='#00d4ff')
        
        self.figure.tight_layout()
        self.canvas.draw()


if __name__ == '__main__':
    root = tk.Tk()
    app = IrisAuthGUI(root)
    root.mainloop()
