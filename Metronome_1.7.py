import tkinter as tk
from tkinter import ttk
import time
import threading
import pygame
import re
import os

class MetronomeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Metronome")

        # Default values
        self.bpm = tk.IntVar(value=60)
        self.beats_per_bar = tk.IntVar(value=4)
        self.subdivisions = tk.StringVar(value="1")
        self.running_event = threading.Event()

        # Initialize pygame mixer
        pygame.mixer.init()

        # Get the path of the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the path to the audio files
        strong_beat_path = os.path.join(current_dir, "strong_beat.wav")
        weak_beat_path = os.path.join(current_dir, "weak_beat.wav")
        nothing_path = os.path.join(current_dir, "nothing.mp3")
        self.strong_beat_sound = pygame.mixer.Sound(strong_beat_path)
        self.weak_beat_sound = pygame.mixer.Sound(weak_beat_path)
        self.nothing = pygame.mixer.Sound(nothing_path)

        self.create_widgets()
        self.metronome_thread = None

    def create_widgets(self):
        mainframe = ttk.Frame(self.root, padding="10 10 10 10")
        mainframe.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        bpm_label = ttk.Label(mainframe, text="BPM:")
        bpm_label.grid(column=1, row=1, sticky=tk.W)

        bpm_entry = ttk.Entry(mainframe, width=7, textvariable=self.bpm)
        bpm_entry.grid(column=2, row=1, sticky=(tk.W, tk.E))

        beats_per_bar_label = ttk.Label(mainframe, text="Beats per bar:")
        beats_per_bar_label.grid(column=1, row=2, sticky=tk.W)

        beats_per_bar_entry = ttk.Entry(mainframe, width=7, textvariable=self.beats_per_bar)
        beats_per_bar_entry.grid(column=2, row=2, sticky=(tk.W, tk.E))

        subdivisions_label = ttk.Label(mainframe, text="Subdivisions (e.g., '1,1,1,1'):")
        subdivisions_label.grid(column=1, row=3, sticky=tk.W)

        subdivisions_entry = ttk.Entry(mainframe, width=20, textvariable=self.subdivisions)
        subdivisions_entry.grid(column=2, row=3, sticky=(tk.W, tk.E))

        start_button = ttk.Button(mainframe, text="Start", command=self.start_metronome)
        start_button.grid(column=1, row=4, sticky=tk.W)

        stop_button = ttk.Button(mainframe, text="Stop", command=self.stop_metronome)
        stop_button.grid(column=2, row=4, sticky=tk.W)

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        # Bind the window closing event to stop the metronome
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

    def on_window_close(self):
        # Stop the metronome if it's running
        self.stop_metronome()
        self.root.destroy()

    def start_metronome(self):
        self.stop_metronome()  # Ensure any running metronome is stopped first
        self.running_event.set()
        self.metronome_thread = threading.Thread(target=self.run_metronome)
        self.metronome_thread.start()

    def stop_metronome(self):
        if self.running_event.is_set():
            self.running_event.clear()
            if self.metronome_thread:
                self.metronome_thread.join()
                self.metronome_thread = None
            self.subdivision_index = 0

    def parse_subdivisions(self):
        subdivisions_str = self.subdivisions.get()
        pattern = re.compile(r'(\d+)(?:/(\d+))?(?:\[(.*?)\])?')
        subdivisions = []

        for match in pattern.finditer(subdivisions_str):
            count = int(match.group(1))
            span = int(match.group(2)) if match.group(2) else 1
            if match.group(3):
                beats = list(map(int, match.group(3).split(',')))
            else:
                beats = [1] * count if count != 0 else [0]
            subdivisions.append((count, span, beats))

        # If only one subdivision pattern is provided, extrapolate it to all beats
        if len(subdivisions) == 1:
            subdivisions = subdivisions * self.beats_per_bar.get()

        return subdivisions

    def run_metronome(self):
        self.subdivision_index = 0
        bpm = self.bpm.get()
        beats_per_bar = self.beats_per_bar.get()
        subdivisions = self.parse_subdivisions()

        # Calculate the beat interval
        beat_interval = 60 / bpm

        # Start the sound player
        sound_thread = threading.Thread(target=self.play_sounds, args=(beat_interval, subdivisions, beats_per_bar))
        sound_thread.start()


    def play_sounds(self, beat_interval, subdivisions, beats_per_bar):
        beat_index = 0 
        subdivision_index = 0
        while self.running_event.is_set():
            while beat_index < beats_per_bar and self.running_event.is_set():
                # Get the subdivision info for this beat
                if subdivision_index < len(subdivisions): 
                    sub_count, span, sub_pattern = subdivisions[subdivision_index]
                else:
                    sub_count = 1
                    span = 1 
                    sub_pattern = [1] * sub_count

                # Calculate the time interval for this beat
                beat_interval_for_subdivision = ((beat_interval * span) / sub_count) if sub_count != 0 else beat_interval

                for sub_beat in range(max(1, sub_count)):
                    if not self.running_event.is_set():
                        return

                    # Play the appropriate sound based on the sub-beat
                    if sub_pattern[sub_beat % len(sub_pattern)] == 1:
                        if beat_index == 0 and sub_beat == 0:
                            self.strong_beat_sound.play()
                        else:
                            self.weak_beat_sound.play()
                    elif sub_pattern[sub_beat % len(sub_pattern)] == 0:
                        self.nothing.play()
                        # Do nothing for a silent beat

                    # Wait for the appropriate time interval for the subdivision
                    if sub_count != 0:
                        time.sleep(beat_interval_for_subdivision)
                    else:
                        time.sleep(beat_interval)

                beat_index += span # ensure the beat index will factor in the span to count to the desired next beat
                subdivision_index += 1 # ensure the next item in the Subdivisions Input will be read

                if beat_index >= beats_per_bar:
                    beat_index = 0
                    subdivision_index = 0


if __name__ == "__main__":
    root = tk.Tk()
    app = MetronomeApp(root)
    root.mainloop()
