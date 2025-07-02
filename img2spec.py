import numpy as np
from PIL import Image
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.signal import spectrogram

def img2spect(img_data, minfreq, maxfreq, dur, Fs, invert, color_channel='L'):
    if invert:
        img_data = 255 - img_data

    imd = np.flipud(img_data) / 255.0
    audio = np.zeros(int(dur * Fs))
    oldlin = np.linspace(0, dur, img_data.shape[1])
    newlin = np.linspace(0, dur, int(dur * Fs))

    np.random.seed(1)

    for row in range(img_data.shape[0]):
        amplitudes = np.interp(newlin, oldlin, imd[row, :], left=0, right=0)
        freq = minfreq * np.exp(row / img_data.shape[0] * np.log(maxfreq / minfreq))
        phase_offset = np.random.rand()
        signal = np.sin(2 * np.pi * freq * (newlin + phase_offset))
        audio += amplitudes * signal

    eps = 1e-10
    return audio / (np.max(np.abs(audio)) + eps)


def show_spectrogram(audio, sample_rate, title="Spectrogram"):
    f, t, Sxx = spectrogram(audio, sample_rate)
    plt.figure(figsize=(10, 5))
    plt.imshow(10 * np.log10(Sxx + 1e-10), aspect='auto', origin='lower',
               extent=[t.min(), t.max(), f.min(), f.max()], cmap='magma')
    plt.colorbar(label='dB')
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.tight_layout()
    plt.show()


def main():
    print("\nImage to Spectrogram Audio Generator (Interactive CLI)\n")

    image_path = input("Enter path to image (e.g., image.png): ").strip()
    output_audio_path = input("Output audio file name (e.g., out.wav): ").strip()
    if not output_audio_path.endswith(".wav"):
        output_audio_path += ".wav"

    min_freq = int(input("Min frequency in Hz (e.g., 500): ").strip())
    max_freq = int(input("Max frequency in Hz (e.g., 10000): ").strip())
    duration = float(input("Duration in seconds (e.g., 60): ").strip())
    sample_rate = int(input("Sample rate in Hz (e.g., 44100): ").strip())

    invert_colors = input("Invert image colors? (y/N): ").strip().lower() == 'y'

    print("\nChoose image channel to encode:")
    print("  1. Grayscale (average)")
    print("  2. Red")
    print("  3. Green")
    print("  4. Blue")
    channel_choice = input("Enter choice (1-4): ").strip()

    img = Image.open(image_path).convert('RGB')
    r, g, b = np.array(img).transpose(2, 0, 1)

    if channel_choice == '2':
        img_data = r
        channel = "Red"
    elif channel_choice == '3':
        img_data = g
        channel = "Green"
    elif channel_choice == '4':
        img_data = b
        channel = "Blue"
    else:
        img_data = np.mean([r, g, b], axis=0).astype(np.uint8)
        channel = "Grayscale"

    print(f"\nGenerating audio from {channel} channel...")
    audio = img2spect(img_data, min_freq, max_freq, duration, sample_rate, invert_colors)

    sf.write(output_audio_path, audio, sample_rate)
    print(f"Audio saved to {output_audio_path}")

    print("\nDisplaying spectrogram...")
    show_spectrogram(audio, sample_rate, title=f"Spectrogram of {image_path} ({channel})")

if __name__ == '__main__':
    main()
