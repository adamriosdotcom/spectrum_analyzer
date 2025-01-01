import subprocess
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Configuration
CONFIG = {
    "freq_min_mhz": 6000,       # Start frequency in MHz
    "freq_max_mhz": 6100,       # End frequency in MHz
    "bin_width_hz": 1_000_000,  # Bin width in Hz (1 MHz resolution)
    "plot_dB_min": -120,        # Minimum dB value for plot
    "plot_dB_max": 0,           # Maximum dB value for plot
    "update_interval_ms": .1,  # Update interval in milliseconds
}

# Extract configuration values
freq_min = CONFIG["freq_min_mhz"]
freq_max = CONFIG["freq_max_mhz"]
bin_width_hz = CONFIG["bin_width_hz"]
bin_width_mhz = bin_width_hz / 1e6  # Convert to MHz
plot_dB_min = CONFIG["plot_dB_min"]
plot_dB_max = CONFIG["plot_dB_max"]
update_interval_ms = CONFIG["update_interval_ms"]

# Frequency bins and amplitude array
freq_bins = np.arange(freq_min, freq_max, bin_width_mhz)  # Full frequency range
amplitudes = np.full(len(freq_bins), plot_dB_min)  # Initialize amplitudes to minimum dB value

# Define the hackrf_sweep command
cmd = [
    "hackrf_sweep",
    "-f", f"{freq_min}:{freq_max}",  # Frequency range in MHz
    "-w", str(bin_width_hz),        # Bin width in Hz
]

# Set up the plot
fig, ax = plt.subplots()
line, = ax.plot(freq_bins, amplitudes, label="Spectrum")
ax.set_xlim(freq_min, freq_max)
ax.set_ylim(plot_dB_min, plot_dB_max)
ax.set_xlabel("Frequency (MHz)")
ax.set_ylabel("Amplitude (dBFS)")
ax.set_title("Real-Time Spectrum Analyzer")
ax.legend()
ax.grid()

# Function to update the plot
def update(frame):
    global amplitudes
    try:
        # Read real-time output from hackrf_sweep
        output = sweep_process.stdout.readline().strip()
        
        # Parse sweep output
        if output and not output.startswith("#"):  # Ignore comments
            parts = output.split(",")
            hz_low = float(parts[2]) / 1e6  # Convert Hz to MHz
            hz_bin_width = float(parts[4]) / 1e6  # Convert Hz to MHz
            dB_values = list(map(float, parts[6:]))  # Amplitudes in dB

            # Calculate bin indices for this segment
            start_idx = int((hz_low - freq_min) / bin_width_mhz)
            end_idx = start_idx + len(dB_values)

            # Update amplitudes in the persistent array
            amplitudes[start_idx:end_idx] = dB_values

            # Update the plot with the full spectrum
            line.set_ydata(amplitudes)
    except Exception as e:
        print(f"Error parsing output: {e}")
    return line,

# Start the hackrf_sweep process
sweep_process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    universal_newlines=True,
    bufsize=1,
)

# Run the animation
ani = FuncAnimation(fig, update, interval=update_interval_ms)  # Update interval in milliseconds
plt.show()

# Clean up when the plot is closed
sweep_process.terminate()