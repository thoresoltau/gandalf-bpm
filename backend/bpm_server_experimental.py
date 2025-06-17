import numpy as np
import sounddevice as sd
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
import asyncio
import websockets

SAMPLE_RATE = 44100
WINDOW_SIZE = 512
CHANNELS = 1
BUFFER_SECONDS = 3

HOST = "localhost"
PORT = 6789

buffer = []
history_bpm = set()
bpm_current = 0
clients = set()

# Audioanalysis
def analyze_signal(signal):
    envelope = np.abs(signal)
    smoothed = gaussian_filter1d(envelope, sigma=3)

    max_val = np.max(smoothed)
    threshold = 0.6 * max_val
    peak_indices, _ = find_peaks(smoothed, height=threshold, distance=int(0.2 * SAMPLE_RATE))

    print(f"Max value: {max_val:.6f} | Peaks: {len(peak_indices)}")

    if len(peak_indices) >= 2:
        peak_times = np.array(peak_indices) / SAMPLE_RATE
        intervals = np.diff(peak_times)
        avg_interval = np.mean(intervals)
        if avg_interval > 0:
            bpm = 60 / avg_interval
            return round(bpm, 2)
    return 0

def audio_callback(indata, frames, time_info, status):
    mono = indata[:, 0]
    buffer.extend(mono.tolist())

    # run every BUFFER_SECONDS seconds
    if len(buffer) >= SAMPLE_RATE * BUFFER_SECONDS:
        segment = np.array(buffer[-SAMPLE_RATE * BUFFER_SECONDS:])
        bpm = analyze_signal(segment)
        global bpm_current
        bpm_current = bpm
        buffer.clear()

# WebSocket-Server
async def broadcast_bpm(websocket):
    clients.add(websocket)
    print("🛰️ Client connected")

    try:
        while True:
            await websocket.send(str(bpm_current))
            await asyncio.sleep(1)
    except websockets.exceptions.ConnectionClosed:
        print("❌ Client disconnected")
    finally:
        clients.remove(websocket)

async def main():
    print(f"🎧 Starting stream and WebSocket on ws://{HOST}:{PORT}")
    with sd.InputStream(callback=audio_callback, channels=CHANNELS, samplerate=SAMPLE_RATE, blocksize=WINDOW_SIZE):
        async with websockets.serve(broadcast_bpm, HOST, PORT):
            await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
