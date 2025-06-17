import asyncio
import sounddevice as sd
import numpy as np
import websockets

SAMPLE_RATE = 44100
WINDOW_SIZE = 512
CHANNELS = 1
BOOST_FACTOR = 5

HOST = "localhost"
PORT = 6789

clients = set()

# estimate BPM from audio signal and return it
def estimate_bpm(signal, sr):

    # Boost by a factor if needed (if signal is too weak)
    #signal = signal * BOOST_FACTOR

    signal = np.abs(signal - np.mean(signal))
    smoothed = np.convolve(signal, np.ones(512) / 512, mode='same')

    # adaptive threshold
    dynamic_thresh = 0.8 * np.max(smoothed)
    if dynamic_thresh < 0.001:
        return None

    # Peak detection
    peaks = (smoothed[1:-1] > smoothed[:-2]) & (smoothed[1:-1] > smoothed[2:])
    peak_indices = np.where(peaks)[0]

    dynamic_thresh = 0.8 * np.max(smoothed)
    peak_indices = [i for i in peak_indices if smoothed[i] > dynamic_thresh]

    if len(peak_indices) < 5:
        return None

    peak_times = np.array(peak_indices) / sr
    valid_peaks = [peak_times[0]]
    for t in peak_times[1:]:
        if t - valid_peaks[-1] > 0.3:
            valid_peaks.append(t)

    if len(valid_peaks) < 2:
        return None

    intervals = np.diff(valid_peaks)
    bpm = 60 / np.median(intervals)

    print(f"BPM: {bpm}, Peaks: {len(valid_peaks)}, Max: {np.max(smoothed):.4f}")

    return round(bpm)

# Stream audio from BlackHole and estimate BPM in real-time
async def stream_bpm():
    buffer = []

    def callback(indata, frames, time_info, status):
        mono = indata[:, 0]
        buffer.extend(mono.tolist())

    if len(buffer) > SAMPLE_RATE * 4:
            del buffer[:len(buffer) - SAMPLE_RATE * 4]

    # Find BlackHole device
    device = next(i for i, d in enumerate(sd.query_devices()) if "BlackHole" in d["name"] and d["max_input_channels"] > 0)
    with sd.InputStream(callback=callback, samplerate=SAMPLE_RATE, blocksize=WINDOW_SIZE, channels=CHANNELS, device=device):
        while True:
            await asyncio.sleep(1.5)
            if len(buffer) < SAMPLE_RATE:
                continue
            signal = np.array(buffer[-SAMPLE_RATE * 3:])
            bpm = estimate_bpm(signal, SAMPLE_RATE)
            if bpm:
                for ws in clients.copy():
                    try:
                        await ws.send(str(bpm))
                    except:
                        clients.remove(ws)

# WebSocket handler to manage client connections
async def handler(ws):
    clients.add(ws)
    print("Client connected")
    try:
        await ws.wait_closed()
    finally:
        clients.remove(ws)
        print("Client disconnected")

# create websocket server and start streaming
async def main():
    asyncio.create_task(stream_bpm())
    async with websockets.serve(handler, HOST, PORT):
        print(f"Listening on ws://{HOST}:{PORT}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
