import flet as ft
import asyncio
from typing import Optional
import os
import json
from datetime import datetime
from tts_engine import TTSEngine
from document_processor import DocumentProcessor

class SpeechEaseAppEnhanced:
    def __init__(self):
        self.page: Optional[ft.Page] = None
        self.current_view = "home"
        self.tts_engine = TTSEngine()
        self.settings = {
            "dark_mode": False,
            "auto_scroll": True,
            "font_size": 16,
            "high_contrast": False,
            "voice": "default",
            "language": "en",
            "speed": 1.0,
            "pitch": 1.0,
            "highlight_color": "yellow",
            "volume": 0.8
        }
        self.recent_documents = []
        self.is_playing = False
        self.current_text = ""
        self.current_document = None
        
    def main(self, page: ft.Page):
        self.page = page
        page.title = "SpeechEase - Text to Speech App"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 1200
        page.window_height = 800
        page.window_min_width = 800
        page.window_min_height = 600
        page.padding = 0
        
        # Load settings and apply TTS settings
        self.load_settings()
        self.apply_tts_settings()
        
        # Create file picker
        self.file_picker = ft.FilePicker(on_result=self.file_picker_result)
        page.overlay.append(self.file_picker)
        
        # Create navigation rail
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.HOME_OUTLINED,
                    selected_icon=ft.icons.HOME,
                    label="Home"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.DESCRIPTION_OUTLINED,
                    selected_icon=ft.icons.DESCRIPTION,
                    label="Document"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS_OUTLINED,
                    selected_icon=ft.icons.SETTINGS,
                    label="Settings"
                ),
            ],
            on_change=self.nav_change,
            bgcolor=ft.colors.WHITE if not self.settings["dark_mode"] else ft.colors.GREY_900,
        )
        
        # Create main content area
        self.content_area = ft.Container(
            content=self.create_home_view(),
            expand=True,
            padding=20,
            bgcolor=ft.colors.GREY_100 if not self.settings["dark_mode"] else ft.colors.GREY_800,
        )
        
        # Main layout
        page.add(
            ft.Row([
                self.nav_rail,
                ft.VerticalDivider(width=1),
                self.content_area,
            ], expand=True)
        )
        
        page.update()
    
    def apply_tts_settings(self):
        """Apply current settings to TTS engine"""
        self.tts_engine.set_voice(self.settings["voice"])
        self.tts_engine.set_rate(self.settings["speed"])
        self.tts_engine.set_volume(self.settings["volume"])
    
    def file_picker_result(self, e: ft.FilePickerResultEvent):
        """Handle file picker result"""
        if e.files:
            file_path = e.files[0].path
            text = DocumentProcessor.process_document(file_path)
            if text:
                self.current_text = text
                self.current_document = {
                    "name": os.path.basename(file_path),
                    "path": file_path,
                    "text": text,
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
                # Add to recent documents
                self.recent_documents.insert(0, self.current_document)
                if len(self.recent_documents) > 10:
                    self.recent_documents = self.recent_documents[:10]
                
                # Switch to document view
                self.nav_rail.selected_index = 1
                self.current_view = "document"
                self.content_area.content = self.create_document_view()
                self.page.update()
                self.show_snackbar(f"Loaded: {self.current_document['name']}")
            else:
                self.show_snackbar("Failed to load document")
    
    def nav_change(self, e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            self.current_view = "home"
            self.content_area.content = self.create_home_view()
        elif selected_index == 1:
            self.current_view = "document"
            self.content_area.content = self.create_document_view()
        elif selected_index == 2:
            self.current_view = "settings"
            self.content_area.content = self.create_settings_view()
        
        self.page.update()
    
    def create_home_view(self):
        return ft.Column([
            ft.Text(
                "Welcome to SpeechEase",
                size=32,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.GREY_800 if not self.settings["dark_mode"] else ft.colors.WHITE,
            ),
            ft.Container(height=20),
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.UPLOAD_FILE, size=64, color=ft.colors.BLUE_500),
                        ft.Container(height=10),
                        ft.Text("Upload Document", size=18, weight=ft.FontWeight.W_500),
                        ft.Text("PDF, DOCX, TXT", size=12, color=ft.colors.GREY_600),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=300,
                    height=200,
                    bgcolor=ft.colors.WHITE if not self.settings["dark_mode"] else ft.colors.GREY_700,
                    border_radius=10,
                    padding=20,
                    on_click=self.upload_document,
                    ink=True,
                ),
                ft.Container(width=20),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.CONTENT_PASTE, size=64, color=ft.colors.GREEN_500),
                        ft.Container(height=10),
                        ft.Text("Paste Text", size=18, weight=ft.FontWeight.W_500),
                        ft.Text("Quick text input", size=12, color=ft.colors.GREY_600),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=300,
                    height=200,
                    bgcolor=ft.colors.WHITE if not self.settings["dark_mode"] else ft.colors.GREY_700,
                    border_radius=10,
                    padding=20,
                    on_click=self.paste_text,
                    ink=True,
                ),
            ]),
            ft.Container(height=40),
            ft.Text(
                "Recent Documents",
                size=24,
                weight=ft.FontWeight.W_600,
                color=ft.colors.GREY_800 if not self.settings["dark_mode"] else ft.colors.WHITE,
            ),
            ft.Container(height=20),
            self.create_recent_documents_grid(),
        ], scroll=ft.ScrollMode.AUTO)
    
    def create_recent_documents_grid(self):
        if not self.recent_documents:
            return ft.Text(
                "No recent documents. Upload a document to get started!",
                size=16,
                color=ft.colors.GREY_600,
                text_align=ft.TextAlign.CENTER,
            )
        
        rows = []
        for i in range(0, len(self.recent_documents), 4):
            row_items = []
            for j in range(4):
                if i + j < len(self.recent_documents):
                    doc = self.recent_documents[i + j]
                    row_items.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Container(
                                    content=ft.Icon(
                                        ft.icons.DESCRIPTION,
                                        size=40,
                                        color=ft.colors.BLUE_500,
                                    ),
                                    width=120,
                                    height=80,
                                    bgcolor=ft.colors.GREY_200,
                                    border_radius=5,
                                    alignment=ft.alignment.center,
                                ),
                                ft.Container(height=5),
                                ft.Text(
                                    doc["name"],
                                    size=12,
                                    text_align=ft.TextAlign.CENTER,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    doc["date"],
                                    size=10,
                                    color=ft.colors.GREY_600,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            width=140,
                            height=140,
                            bgcolor=ft.colors.WHITE if not self.settings["dark_mode"] else ft.colors.GREY_700,
                            border_radius=8,
                            padding=10,
                            on_click=lambda e, doc=doc: self.open_document(doc),
                            ink=True,
                        )
                    )
                    if j < 3:
                        row_items.append(ft.Container(width=10))
            
            if row_items:
                rows.append(ft.Row(row_items))
                if i + 4 < len(self.recent_documents):
                    rows.append(ft.Container(height=10))
        
        return ft.Column(rows)
    
    def create_document_view(self):
        if not self.current_document:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.DESCRIPTION, size=100, color=ft.colors.GREY_400),
                    ft.Text("No document loaded", size=20, color=ft.colors.GREY_600),
                    ft.Text("Upload a document from the Home screen", size=14, color=ft.colors.GREY_500),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True,
            )
        
        # Document content area
        document_content = ft.Container(
            content=ft.Column([
                ft.Text(
                    self.current_document["name"],
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.GREY_800 if not self.settings["dark_mode"] else ft.colors.WHITE,
                ),
                ft.Container(height=20),
                ft.Text(
                    self.current_document["text"],
                    size=self.settings["font_size"],
                    selectable=True,
                    color=ft.colors.GREY_700 if not self.settings["dark_mode"] else ft.colors.GREY_300,
                ),
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
            bgcolor=ft.colors.WHITE if not self.settings["dark_mode"] else ft.colors.GREY_700,
            border_radius=10,
            padding=20,
        )
        
        # Control panel
        control_panel = ft.Container(
            content=ft.Column([
                # Playback controls
                ft.Row([
                    ft.IconButton(
                        icon=ft.icons.PAUSE if self.is_playing else ft.icons.PLAY_ARROW,
                        icon_size=32,
                        bgcolor=ft.colors.BLUE_500,
                        icon_color=ft.colors.WHITE,
                        on_click=self.toggle_playback,
                        tooltip="Play/Pause",
                    ),
                    ft.IconButton(
                        icon=ft.icons.STOP,
                        icon_size=32,
                        bgcolor=ft.colors.GREY_400,
                        icon_color=ft.colors.WHITE,
                        on_click=self.stop_playback,
                        tooltip="Stop",
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                
                ft.Container(height=20),
                
                # Speed control
                ft.Text("Speed", weight=ft.FontWeight.W_500),
                ft.Slider(
                    min=0.5,
                    max=2.0,
                    value=self.settings["speed"],
                    divisions=15,
                    label=f"{self.settings['speed']:.1f}x",
                    on_change=self.speed_changed,
                ),
                
                ft.Container(height=10),
                
                # Volume control
                ft.Text("Volume", weight=ft.FontWeight.W_500),
                ft.Slider(
                    min=0.0,
                    max=1.0,
                    value=self.settings["volume"],
                    divisions=10,
                    label=f"{int(self.settings['volume']*100)}%",
                    on_change=self.volume_changed,
                ),
                
                ft.Container(height=20),
                
                # Voice selection
                ft.Text("Voice", weight=ft.FontWeight.W_500),
                ft.Dropdown(
                    value=self.settings["voice"],
                    options=[
                        ft.dropdown.Option("default", "Default"),
                        ft.dropdown.Option("male", "Male"),
                        ft.dropdown.Option("female", "Female"),
                    ],
                    on_change=self.voice_changed,
                ),
                
                ft.Container(height=20),
                
                # Export button
                ft.ElevatedButton(
                    "Export Audio",
                    icon=ft.icons.DOWNLOAD,
                    on_click=self.export_audio,
                    bgcolor=ft.colors.GREEN_500,
                    color=ft.colors.WHITE,
                ),
                
            ]),
            width=250,
            bgcolor=ft.colors.WHITE if not self.settings["dark_mode"] else ft.colors.GREY_700,
            border_radius=10,
            padding=20,
        )
        
        return ft.Row([
            document_content,
            ft.Container(width=20),
            control_panel,
        ], expand=True)
    
    def create_settings_view(self):
        return ft.Column([
            ft.Text(
                "Settings",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.GREY_800 if not self.settings["dark_mode"] else ft.colors.WHITE,
            ),
            ft.Container(height=30),
            
            # Appearance section
            ft.Text("Appearance", size=20, weight=ft.FontWeight.W_600),
            ft.Container(height=10),
            ft.Row([
                ft.Text("Dark Mode", size=16),
                ft.Switch(
                    value=self.settings["dark_mode"],
                    on_change=self.toggle_dark_mode,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Container(height=20),
            
            # Reading preferences section
            ft.Text("Reading Preferences", size=20, weight=ft.FontWeight.W_600),
            ft.Container(height=10),
            ft.Row([
                ft.Text("Auto-scroll", size=16),
                ft.Switch(
                    value=self.settings["auto_scroll"],
                    on_change=self.toggle_auto_scroll,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Container(height=15),
            
            ft.Text("Font Size", size=16),
            ft.Slider(
                min=12,
                max=24,
                value=self.settings["font_size"],
                divisions=12,
                label=f"{self.settings['font_size']}px",
                on_change=self.font_size_changed,
            ),
            
            ft.Container(height=20),
            
            # Accessibility section
            ft.Text("Accessibility", size=20, weight=ft.FontWeight.W_600),
            ft.Container(height=10),
            ft.Row([
                ft.Text("High Contrast Mode", size=16),
                ft.Switch(
                    value=self.settings["high_contrast"],
                    on_change=self.toggle_high_contrast,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Container(height=15),
            
            ft.Text("Highlight Color", size=16),
            ft.Dropdown(
                value=self.settings["highlight_color"],
                options=[
                    ft.dropdown.Option("yellow", "Yellow"),
                    ft.dropdown.Option("blue", "Blue"),
                    ft.dropdown.Option("green", "Green"),
                    ft.dropdown.Option("pink", "Pink"),
                ],
                on_change=self.highlight_color_changed,
            ),
            
        ], scroll=ft.ScrollMode.AUTO)
    
    # Event handlers
    def upload_document(self, e):
        self.file_picker.pick_files(
            dialog_title="Select a document",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["pdf", "docx", "txt"],
        )
    
    def paste_text(self, e):
        # Create a dialog for pasting text
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        def paste_and_close(e):
            text = text_field.value.strip()
            if text:
                self.current_text = text
                self.current_document = {
                    "name": "Pasted Text",
                    "path": None,
                    "text": text,
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
                # Add to recent documents
                self.recent_documents.insert(0, self.current_document)
                if len(self.recent_documents) > 10:
                    self.recent_documents = self.recent_documents[:10]
                
                # Switch to document view
                self.nav_rail.selected_index = 1
                self.current_view = "document"
                self.content_area.content = self.create_document_view()
                self.show_snackbar("Text loaded successfully")
            
            dialog.open = False
            self.page.update()
        
        text_field = ft.TextField(
            label="Paste your text here",
            multiline=True,
            min_lines=5,
            max_lines=10,
            expand=True,
        )
        
        dialog = ft.AlertDialog(
            title=ft.Text("Paste Text"),
            content=ft.Container(
                content=text_field,
                width=500,
                height=300,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Load Text", on_click=paste_and_close),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def open_document(self, doc):
        self.current_document = doc
        self.current_text = doc["text"]
        self.nav_rail.selected_index = 1
        self.current_view = "document"
        self.content_area.content = self.create_document_view()
        self.page.update()
    
    def toggle_playback(self, e):
        if not self.current_document:
            self.show_snackbar("No document loaded")
            return
        
        if self.is_playing:
            self.tts_engine.stop()
            self.is_playing = False
        else:
            self.tts_engine.speak(self.current_document["text"])
            self.is_playing = True
        
        # Update the button icon
        if self.current_view == "document":
            self.content_area.content = self.create_document_view()
            self.page.update()
        
        status = "Playing..." if self.is_playing else "Paused"
        self.show_snackbar(status)
    
    def stop_playback(self, e):
        self.tts_engine.stop()
        self.is_playing = False
        
        # Update the view
        if self.current_view == "document":
            self.content_area.content = self.create_document_view()
            self.page.update()
        
        self.show_snackbar("Stopped")
    
    def speed_changed(self, e):
        self.settings["speed"] = e.control.value
        self.tts_engine.set_rate(self.settings["speed"])
        self.save_settings()
    
    def volume_changed(self, e):
        self.settings["volume"] = e.control.value
        self.tts_engine.set_volume(self.settings["volume"])
        self.save_settings()
    
    def voice_changed(self, e):
        self.settings["voice"] = e.control.value
        self.tts_engine.set_voice(self.settings["voice"])
        self.save_settings()
    
    def export_audio(self, e):
        self.show_snackbar("Audio export feature coming soon!")
    
    def toggle_dark_mode(self, e):
        self.settings["dark_mode"] = e.control.value
        self.page.theme_mode = ft.ThemeMode.DARK if self.settings["dark_mode"] else ft.ThemeMode.LIGHT
        self.save_settings()
        self.refresh_current_view()
    
    def toggle_auto_scroll(self, e):
        self.settings["auto_scroll"] = e.control.value
        self.save_settings()
    
    def font_size_changed(self, e):
        self.settings["font_size"] = int(e.control.value)
        self.save_settings()
        if self.current_view == "document":
            self.content_area.content = self.create_document_view()
            self.page.update()
    
    def toggle_high_contrast(self, e):
        self.settings["high_contrast"] = e.control.value
        self.save_settings()
    
    def highlight_color_changed(self, e):
        self.settings["highlight_color"] = e.control.value
        self.save_settings()
    
    def refresh_current_view(self):
        if self.current_view == "home":
            self.content_area.content = self.create_home_view()
        elif self.current_view == "document":
            self.content_area.content = self.create_document_view()
        elif self.current_view == "settings":
            self.content_area.content = self.create_settings_view()
        elif self.current_view == "profile":
            self.content_area.content = self.create_profile_view()
        
        # Update navigation rail theme
        self.nav_rail.bgcolor = ft.colors.WHITE if not self.settings["dark_mode"] else ft.colors.GREY_900
        self.content_area.bgcolor = ft.colors.GREY_100 if not self.settings["dark_mode"] else ft.colors.GREY_800
        
        self.page.update()
    
    def show_snackbar(self, message):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            action="OK",
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def load_settings(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        try:
            with open("settings.json", "w") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

def main(page: ft.Page):
    app = SpeechEaseAppEnhanced()
    app.main(page)

if __name__ == "__main__":
    ft.app(target=main ,view=ft.WEB_BROWSER)
