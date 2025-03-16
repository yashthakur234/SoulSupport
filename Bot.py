import os
import random
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, filedialog
from PIL import Image, ImageDraw, ImageFont, ImageTk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import webbrowser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fpdf import FPDF
import speech_recognition as sr
import threading

# Suppress macOS warnings
os.environ['XPC_SERVICE_NAME'] = '0'

class MentalHealthAIBot:
    def __init__(self, root):
        self.root = root
        self.root.title("SoulSupport – A digital friend for mental wellness")
        self.root.geometry("1400x900")
        self.style = ttk.Style(theme='minty')
        self.depression_score = 0
        self.current_question = 0
        self.diagnosis_active = False
        self.user_responses = []
        self.recognizer = sr.Recognizer()
        
        # Hospital Database
        self.hospitals = [
            {
                "name": "Fortis Hospital",
                "address": "B-22, Sector 62, Gautam Budh Nagar, Greater Noida",
                "phone": "0120-240-2100",
                "specialty": "Psychiatry & Mental Health"
            },
            {
                "name": "Kailash Hospital",
                "address": "Gamma-I, Greater Noida, Uttar Pradesh 201310",
                "phone": "0120-232-6021",
                "specialty": "Mental Health Services"
            }
        ]

        # Relaxation Exercises
        self.relaxation_exercises = {
            "4-7-8 Breathing": self.guide_478_breathing,
            "Progressive Relaxation": self.guide_progressive_relaxation,
            "5-4-3-2-1 Grounding": self.guide_54321_grounding
        }

        # Healing Music
        self.healing_music = [
            {"title": "Weightless", "url": "https://youtu.be/UfcAVejslrU"},
            {"title": "Clair de Lune", "url": "https://youtu.be/CvFH_6DNRCY"}
        ]

        # GUI Setup
        self.create_widgets()
        self.show_typing_indicator("Welcome to SoulSupport – A digital friend for mental wellness 🤖\nHow can I assist you today?")
        
        # Diagnosis questions
        self.diagnosis_questions = [
            "How often do you feel sad or hopeless? (1: Never - 5: Always)",
            "How would you rate your sleep quality? (1: Excellent - 5: Very Poor)",
            "How is your appetite recently? (1: Normal - 5: No Appetite)",
            "Do you have trouble concentrating? (1: Never - 5: Always)",
            "How often do you feel fatigued? (1: Never - 5: Always)"
        ]

    def load_image(self, emoji, size=40):
        """Create emoji image with proper font handling"""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("seguiemj.ttf", 32)
        except:
            try:
                font = ImageFont.truetype("Apple Color Emoji.ttf", 32)
            except:
                font = ImageFont.load_default()
        d.text((10, 0), emoji, font=font, fill="black")
        return ImageTk.PhotoImage(img)

    def create_widgets(self):
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)

        # Left Panel (Main Chat)
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=3)

        # Right Panel (Relaxation Exercises)
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)

        # Chat Components
        header_frame = ttk.Frame(left_frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        self.logo = self.load_image("🧠", size=40)
        ttk.Label(header_frame, image=self.logo).pack(side=tk.LEFT, padx=10)
        ttk.Label(header_frame, text="SoulSupport – A digital friend for mental wellness", 
                 font=('Arial', 18, 'bold')).pack(side=tk.LEFT)
        
        self.viz_frame = ttk.Frame(left_frame)
        self.viz_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.chat_history = scrolledtext.ScrolledText(
            left_frame, 
            wrap=tk.WORD, 
            state='disabled',
            font=('Arial', 12),
            background='#ffffff',
            padx=15,
            pady=15
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True, pady=10)

        input_frame = ttk.Frame(left_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        self.user_input = ttk.Entry(
            input_frame, 
            font=('Arial', 14),
            bootstyle='primary'
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.user_input.bind("<Return>", self.process_input)
        
        ttk.Button(
            input_frame,
            text="🎤 Speak",
            command=self.start_voice_recognition,
            bootstyle='info'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            input_frame, 
            text="Send", 
            command=self.process_input,
            bootstyle='success'
        ).pack(side=tk.LEFT, padx=5)

        self.create_action_buttons(left_frame)
        self.create_relaxation_panel(right_frame)

    def create_relaxation_panel(self, parent):
        exercise_frame = ttk.Labelframe(parent, text="Relaxation Exercises", padding=10)
        exercise_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for exercise in self.relaxation_exercises:
            ttk.Button(
                exercise_frame,
                text=exercise,
                command=lambda e=exercise: self.start_exercise(e),
                bootstyle="light",
                width=25
            ).pack(pady=5, fill=tk.X)

        ttk.Separator(exercise_frame).pack(fill=tk.X, pady=10)
        ttk.Label(exercise_frame, text="Quick Stress Relief:", font=('Arial', 10)).pack()
        ttk.Button(
            exercise_frame,
            text="Instant Calm",
            command=lambda: self.guided_exercise([
                ("🌬️ Take a deep breath", 2000),
                ("🤚 Hold for 3 seconds", 3000),
                ("😮💨 Exhale slowly", 4000),
                ("🔄 Repeat 3 times", 1000)
            ]),
            bootstyle="outline"
        ).pack(pady=5)

    def start_exercise(self, exercise_name):
        self.show_typing_indicator(f"Starting {exercise_name}...")
        self.root.after(1500, self.relaxation_exercises[exercise_name])

    def guide_478_breathing(self):
        steps = [
            ("🔄 Sit comfortably and relax your shoulders", 2000),
            ("🌬️ Empty your lungs completely", 1000),
            ("🫁 Inhale quietly through nose for 4 seconds...", 4000),
            ("⏳ Hold breath for 7 seconds...", 7000),
            ("😮💨 Exhale completely through mouth for 8 seconds...", 8000),
            ("✨ Repeat this cycle 3-4 times", 2000)
        ]
        self.guided_exercise(steps)

    def guide_progressive_relaxation(self):
        steps = [
            ("🪑 Sit or lie down comfortably", 2000),
            ("👊 Tense your hand muscles for 5 seconds...", 5000),
            ("✋ Release and relax for 30 seconds...", 30000),
            ("👣 Move to feet muscles: Tense...", 5000),
            ("🦶 Release and relax...", 30000),
            ("🔄 Continue through all muscle groups", 2000)
        ]
        self.guided_exercise(steps)

    def guide_54321_grounding(self):
        steps = [
            ("🌍 Notice 5 things you can see around you", 5000),
            ("✋ Name 4 things you can touch", 4000),
            ("👂 Identify 3 sounds you can hear", 3000),
            ("👃 Notice 2 things you can smell", 2000),
            ("💪 Name 1 thing you can do right now", 1000),
            ("🌈 Grounding complete. Feel more present?", 2000)
        ]
        self.guided_exercise(steps)

    def guided_exercise(self, steps):
        def next_step(index=0):
            if index < len(steps):
                text, delay = steps[index]
                self.show_message("Guide", text)
                self.root.after(delay, next_step, index+1)
            else:
                self.show_message("Guide", "Exercise complete! 🎉")
        
        threading.Thread(target=next_step, daemon=True).start()

    def create_action_buttons(self, parent):
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=10)
        
        buttons = [
            ("Start Diagnosis", self.start_diagnosis, 'primary'),
            ("View Report", self.generate_report, 'info'),
            ("Music Therapy", self.recommend_music, 'success'),
            ("Find Hospitals", self.show_hospitals, 'warning'),
            ("Exit", self.root.destroy, 'danger')
        ]
        
        for text, command, style in buttons:
            ttk.Button(
                action_frame,
                text=text,
                command=command,
                bootstyle=style
            ).pack(side=tk.LEFT, padx=5)

    def show_typing_indicator(self, message):
        self.chat_history.configure(state='normal')
        self.chat_history.insert(tk.END, "🤖 Bot is typing...\n")
        self.chat_history.see(tk.END)
        self.chat_history.configure(state='disabled')
        self.root.after(1500, lambda: self.update_message(message))

    def update_message(self, message):
        self.chat_history.configure(state='normal')
        self.chat_history.delete("end-2l", "end-1c")
        self.chat_history.insert(tk.END, f"🤖 Bot: {message}\n\n")
        self.chat_history.configure(state='disabled')
        self.chat_history.see(tk.END)

    def show_message(self, sender, message):
        self.chat_history.configure(state='normal')
        self.chat_history.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_history.configure(state='disabled')
        self.chat_history.see(tk.END)

    def process_input(self, event=None):
        user_text = self.user_input.get()
        if not user_text:
            return
        
        self.show_message("You", user_text)
        self.user_input.delete(0, tk.END)
        
        if self.diagnosis_active:
            self.handle_diagnosis(user_text)
        else:
            self.handle_basic_response(user_text)

    def handle_basic_response(self, user_input):
        responses = {
            'hello': "Hello! How can I help you today?",
            'help': "I'm here to listen. You can:\n- Start a diagnosis\n- Try relaxation exercises\n- Request music recommendations\n- Find local hospitals",
            'stress': "Let's try a quick breathing exercise! Check the relaxation panel →",
            'sad': "I'm sorry to hear that. Would you like to try the 5-4-3-2-1 grounding exercise?",
            'default': "I'm here to support you. Could you tell me more about how you're feeling?"
        }
        
        response = responses.get(user_input.lower(), responses['default'])
        self.show_typing_indicator(response)

    def start_diagnosis(self):
        self.diagnosis_active = True
        self.depression_score = 0
        self.current_question = 0
        self.user_responses = []
        self.show_typing_indicator(self.diagnosis_questions[self.current_question])

    def handle_diagnosis(self, answer):
        try:
            score = int(answer)
            if 1 <= score <= 5:
                self.user_responses.append(score)
                self.depression_score += score
                self.current_question += 1
                
                if self.current_question < len(self.diagnosis_questions):
                    self.show_typing_indicator(self.diagnosis_questions[self.current_question])
                else:
                    self.visualize_depression_level()
                    self.show_results()
            else:
                self.show_typing_indicator("Please enter a number between 1-5")
        except ValueError:
            self.show_typing_indicator("Please enter a valid number")

    def visualize_depression_level(self):
        fig = plt.figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        categories = ['Sadness', 'Sleep', 'Appetite', 'Concentration', 'Fatigue']
        values = self.user_responses[-5:]
        
        ax.bar(categories, values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD'])
        ax.set_ylim(0, 5)
        ax.set_title('Depression Level Analysis')
        
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
            
        canvas = FigureCanvasTkAgg(fig, master=self.viz_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_results(self):
        total = self.depression_score
        if total <= 10:
            msg = "🌼 Mild Symptoms: Practice self-care!"
        elif total <= 15:
            msg = "📞 Moderate Symptoms: Consider professional help"
        else:
            msg = "🚨 Severe Symptoms: Immediate consultation recommended"
            self.show_hospitals()
        
        msg += f"\n\nYour score: {total}/25"
        self.show_typing_indicator(msg)
        self.diagnosis_active = False

    def generate_report(self):
        if not self.user_responses:
            self.show_message("Bot", "⚠️ No assessment data available!")
            return
            
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        plt.savefig("temp_chart.png", bbox_inches='tight')
        
        pdf.cell(200, 10, txt="Mental Health Assessment Report", ln=1, align='C')
        pdf.ln(10)
        
        for idx, response in enumerate(self.user_responses):
            pdf.multi_cell(0, 10, 
                f"Q{idx+1}: {self.diagnosis_questions[idx]}\nScore: {response}\n")
        
        pdf.image("temp_chart.png", x=10, y=100, w=180)
        
        pdf.add_page()
        pdf.cell(200, 10, txt="Recommendations:", ln=1)
        recommendations = [
            "1. Practice mindfulness daily",
            "2. Maintain regular sleep schedule",
            "3. Engage in physical activity",
            "4. Consider professional counseling"
        ]
        for rec in recommendations:
            pdf.cell(200, 10, txt=rec, ln=1)
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if filename:
            pdf.output(filename)
            self.show_message("Bot", f"✅ Report saved: {filename}")

    def show_hospitals(self):
        hospital_info = "\n\n".join([
            f"🏥 {h['name']}\n📍 {h['address']}\n📞 {h['phone']}\nSpecialty: {h['specialty']}"
            for h in self.hospitals
        ])
        self.show_typing_indicator(f"Mental Health Hospitals in Greater Noida:\n\n{hospital_info}")

    def recommend_music(self):
        music_list = "\n".join([f"🎵 {song['title']}" for song in self.healing_music])
        self.show_typing_indicator(f"Recommended Music:\n{music_list}")
        webbrowser.open(self.healing_music[0]['url'])

    def start_voice_recognition(self):
        def recognition_thread():
            try:
                with sr.Microphone() as source:
                    self.show_message("Bot", "🎤 Listening... Speak now")
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=5)
                    
                    text = self.recognizer.recognize_google(audio)
                    self.user_input.delete(0, tk.END)
                    self.user_input.insert(0, text)
                    self.show_message("You", text)
                    
            except sr.WaitTimeoutError:
                self.show_message("Bot", "⏳ No speech detected")
            except sr.UnknownValueError:
                self.show_message("Bot", "🔇 Could not understand audio")
            except sr.RequestError as e:
                self.show_message("Bot", f"🚫 Speech service error: {str(e)}")
            except Exception as e:
                self.show_message("Bot", f"⚠️ Error: {str(e)}")

        threading.Thread(target=recognition_thread, daemon=True).start()

if __name__ == "__main__":
    root = ttk.Window()
    bot = MentalHealthAIBot(root)
    root.mainloop()
