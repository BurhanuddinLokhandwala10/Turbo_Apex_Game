"""
Procedural Sound Synthesis System
=================================
Generates real-time procedural sound effects using NumPy wave arrays.
Guarantees 100% crash-free audio with zero external file dependencies.
Silently degrades to dummy no-op mode if no audio hardware is present.
"""

import math
import numpy as np
import pygame

class SoundManager:
    """Manages audio playback and procedural sound synthesis."""
    
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SoundManager()
        return cls._instance

    def __init__(self):
        self.enabled = False
        self.sample_rate = 44100
        self.sounds = {}
        self.engine_channel_p1 = None
        self.engine_channel_p2 = None

        try:
            # Pre-init mixer for low-latency audio
            if not pygame.mixer.get_init():
                pygame.mixer.pre_init(frequency=self.sample_rate, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
            self.enabled = True
            self._generate_procedural_sounds()
        except Exception as e:
            print(f"[SoundManager] Audio initialization disabled: {e}")
            self.enabled = False

    def _generate_procedural_sounds(self):
        """Synthesize sound waves using NumPy."""
        try:
            # 1. Countdown Warning Beep (440 Hz square-sine blend, 150ms)
            self.sounds["beep"] = self._create_beep_sound(freq=480, duration=0.15, vol=0.55)

            # 2. Countdown GO Chime (880 Hz pure bell tone, 400ms)
            self.sounds["go"] = self._create_beep_sound(freq=960, duration=0.45, vol=0.7)

            # 3. Collision Impact (White noise burst with exponential low-pass decay)
            self.sounds["crash"] = self._create_crash_sound(duration=0.35, vol=0.65)

            # 4. Fuel Can Pickup (Two-tone ascending bright chime)
            self.sounds["pickup"] = self._create_pickup_sound(duration=0.25, vol=0.6)

            # 5. UI Button Select Click
            self.sounds["click"] = self._create_beep_sound(freq=700, duration=0.06, vol=0.4)

            # 6. Tire Screech (Band-pass modulated noise)
            self.sounds["skid"] = self._create_skid_sound(duration=0.3, vol=0.4)

            # 7. Victory Fanfare (Triumphant triad chord)
            self.sounds["victory"] = self._create_fanfare_sound(duration=1.2, vol=0.7)

        except Exception as e:
            print(f"[SoundManager] Error generating sound samples: {e}")
            self.enabled = False

    def _create_beep_sound(self, freq=440.0, duration=0.2, vol=0.5):
        """Generates a clean sine/triangle tone with attack/decay envelope."""
        n_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)
        # Sine wave with slight harmonic
        wave = 0.8 * np.sin(2 * np.pi * freq * t) + 0.2 * np.sin(4 * np.pi * freq * t)
        # Linear fade out
        envelope = np.linspace(1.0, 0.0, n_samples) ** 1.5
        audio = (wave * envelope * vol * 32767).astype(np.int16)
        # Stereo duplication
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def _create_crash_sound(self, duration=0.35, vol=0.6):
        """Generates a percussive crash impact using decayed noise."""
        n_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)
        noise = np.random.uniform(-1.0, 1.0, n_samples)
        # Sub-bass punch (80 Hz exponential pitch drop)
        bass = np.sin(2 * np.pi * (90 * np.exp(-t * 12)) * t)
        envelope = np.exp(-t * 14.0)
        audio = ((0.6 * noise + 0.5 * bass) * envelope * vol * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def _create_pickup_sound(self, duration=0.28, vol=0.5):
        """Generates a cheerful ascending chime (D5 -> A5)."""
        n_samples = int(self.sample_rate * duration)
        half = n_samples // 2
        t1 = np.linspace(0, duration / 2, half, False)
        t2 = np.linspace(0, duration / 2, n_samples - half, False)
        wave1 = np.sin(2 * np.pi * 587.33 * t1) * np.linspace(0.2, 1.0, half)
        wave2 = np.sin(2 * np.pi * 880.00 * t2) * np.linspace(1.0, 0.0, n_samples - half)
        wave = np.concatenate((wave1, wave2))
        audio = (wave * vol * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def _create_skid_sound(self, duration=0.3, vol=0.4):
        """Generates a filtered screech noise."""
        n_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)
        noise = np.random.uniform(-0.8, 0.8, n_samples)
        modulation = np.sin(2 * np.pi * 35 * t)
        envelope = np.sin(np.pi * t / duration)
        audio = (noise * (0.6 + 0.4 * modulation) * envelope * vol * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def _create_fanfare_sound(self, duration=1.2, vol=0.7):
        """Generates a triumphant triad chord (C5 - E5 - G5)."""
        n_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)
        wave = (np.sin(2 * np.pi * 523.25 * t) +
                np.sin(2 * np.pi * 659.25 * t) +
                np.sin(2 * np.pi * 783.99 * t)) / 3.0
        envelope = np.exp(-t * 2.2)
        audio = (wave * envelope * vol * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def play(self, sound_name):
        """Plays a one-shot sound effect by key."""
        if not self.enabled:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass
