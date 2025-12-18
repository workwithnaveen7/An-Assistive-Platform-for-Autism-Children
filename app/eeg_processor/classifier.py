import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
from config import Config

class EEGClassifier:
    """
    Classifies EEG frequency data into brain state bands
    """
    
    def __init__(self):
        self.brain_states = Config.BRAIN_STATES
        self.sampling_rate = Config.EEG_SAMPLING_RATE
    
    def classify_frequency(self, frequency):
        """
        Classify a single frequency value into a brain state
        
        Args:
            frequency (float): Frequency in Hz
            
        Returns:
            str: Brain state name (delta, theta, alpha, beta, gamma)
        """
        for state_name, state_info in self.brain_states.items():
            min_freq, max_freq = state_info['range']
            if min_freq <= frequency < max_freq:
                return state_name
        
        # Default to gamma if frequency is very high
        return 'gamma'
    
    def process_eeg_signal(self, raw_signal, sampling_rate=None):
        """
        Process raw EEG signal and extract dominant frequency
        
        Args:
            raw_signal (list or np.array): Raw EEG amplitude values
            sampling_rate (int): Sampling rate in Hz
            
        Returns:
            dict: {
                'dominant_frequency': float,
                'brain_state': str,
                'band_powers': dict
            }
        """
        if sampling_rate is None:
            sampling_rate = self.sampling_rate
        
        signal_array = np.array(raw_signal)
        
        # Apply bandpass filter (0.5-50 Hz) to remove noise
        nyquist = sampling_rate / 2
        low = 0.5 / nyquist
        high = 50 / nyquist
        b, a = signal.butter(4, [low, high], btype='band')
        filtered_signal = signal.filtfilt(b, a, signal_array)
        
        # Compute FFT
        n = len(filtered_signal)
        yf = fft(filtered_signal)
        xf = fftfreq(n, 1 / sampling_rate)
        
        # Get positive frequencies only
        positive_freq_idx = xf > 0
        frequencies = xf[positive_freq_idx]
        power = np.abs(yf[positive_freq_idx]) ** 2
        
        # Find dominant frequency
        dominant_idx = np.argmax(power)
        dominant_frequency = frequencies[dominant_idx]
        
        # Calculate band powers
        band_powers = self.calculate_band_powers(frequencies, power)
        
        # Classify brain state
        brain_state = self.classify_frequency(dominant_frequency)
        
        return {
            'dominant_frequency': float(dominant_frequency),
            'brain_state': brain_state,
            'band_powers': band_powers
        }
    
    def calculate_band_powers(self, frequencies, power):
        """
        Calculate power in each frequency band
        
        Returns:
            dict: Band powers for each brain state
        """
        band_powers = {}
        
        for state_name, state_info in self.brain_states.items():
            min_freq, max_freq = state_info['range']
            band_mask = (frequencies >= min_freq) & (frequencies < max_freq)
            band_powers[state_name] = float(np.sum(power[band_mask]))
        
        # Normalize
        total_power = sum(band_powers.values())
        if total_power > 0:
            band_powers = {k: (v / total_power) * 100 for k, v in band_powers.items()}
        
        return band_powers
    
    def get_state_info(self, brain_state):
        """Get detailed information about a brain state"""
        return self.brain_states.get(brain_state, {})
