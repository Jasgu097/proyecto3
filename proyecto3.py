import tkinter as tk
from tkinter import filedialog, messagebox
import heapq
import os
from PIL import Image
import wave
from collections import Counter
import pickle


class HuffmanCoder:
    """Implementa compresión/descompresión Huffman para texto"""

    def __init__(self):
        self.codes = {}
        self.reverse_codes = {}

    def _build_tree(self, frequencies):
        heap = [[freq, [char, ""]] for char, freq in frequencies.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            lo = heapq.heappop(heap)
            hi = heapq.heappop(heap)
            for pair in lo[1:]:
                pair[1] = '0' + pair[1]
            for pair in hi[1:]:
                pair[1] = '1' + pair[1]
            heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

        return sorted(heapq.heappop(heap)[1:], key=lambda p: (len(p[-1]), p))

    def encode(self, text):
        if not text:
            return "", {}

        frequencies = Counter(text)
        tree = self._build_tree(frequencies)
        self.codes = {char: code for char, code in tree}

        bitstring = ''.join(self.codes[char] for char in text)
        return bitstring, self.codes

    def decode(self, bitstring, codes):
        reverse_codes = {v: k for k, v in codes.items()}
        result = []
        i = 0
        while i < len(bitstring):
            for length in range(1, len(bitstring) - i + 1):
                code = bitstring[i:i + length]
                if code in reverse_codes:
                    result.append(reverse_codes[code])
                    i += length
                    break
        return ''.join(result)


class RLECoder:
    """Implementa compresión/descompresión Run Length Encoding"""

    @staticmethod
    def encode(data):
        if not data:
            return b''

        encoded = []
        i = 0
        while i < len(data):
            count = 1
            while i + count < len(data) and data[i] == data[i + count] and count < 255:
                count += 1
            encoded.append(count)
            encoded.append(data[i] if isinstance(data[i], int) else ord(data[i]))
            i += count

        return bytes(encoded)

    @staticmethod
    def decode(data):
        decoded = []
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                count = data[i]
                value = data[i + 1]
                decoded.extend([value] * count)

        return bytes(decoded)


class CompressionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicación de Compresión de Datos")
        self.root.geometry("500x450")
        self.root.configure(bg="#f0f0f0")

        self.setup_main_menu()

    def setup_main_menu(self):
        """Crea el menú principal"""
        self.clear_window()

        title = tk.Label(self.root, text="Compresión de Datos",
                         font=("Arial", 20, "bold"), bg="#f0f0f0")
        title.pack(pady=20)

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=20)

        buttons_config = [
            ("Comprimir/Descomprimir Texto", self.text_compression_window),
            ("Comprimir/Descomprimir Imágenes", self.image_compression_window),
            ("Comprimir/Descomprimir Audio", self.audio_compression_window)
        ]

        for text, command in buttons_config:
            btn = tk.Button(frame, text=text, font=("Arial", 12),
                            width=30, height=2, command=command,
                            bg="#4CAF50", fg="white")
            btn.pack(pady=10)

    def clear_window(self):
        """Limpia todos los widgets de la ventana"""
        for widget in self.root.winfo_children():
            widget.destroy()

    # ---------- TEXTO ----------
    def text_compression_window(self):
        self.clear_window()

        tk.Label(self.root, text="Compresión/Descompresión de Texto (Huffman)",
                 font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)

        self.text_file_path = tk.StringVar()

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=10)

        tk.Button(frame, text="Seleccionar archivo (.txt/.bin)",
                  command=self.select_text_file).pack(pady=5)
        tk.Label(frame, textvariable=self.text_file_path,
                 bg="#f0f0f0", wraplength=400).pack(pady=5)

        tk.Button(frame, text="Comprimir",
                  command=self.compress_text, bg="#2196F3", fg="white").pack(pady=5)
        tk.Button(frame, text="Descomprimir",
                  command=self.decompress_text, bg="#9C27B0", fg="white").pack(pady=5)
        tk.Button(frame, text="Volver",
                  command=self.setup_main_menu).pack(pady=5)

    def select_text_file(self):
        file = filedialog.askopenfilename(filetypes=[("Text or Binary files", "*.txt *.bin")])
        if file:
            self.text_file_path.set(file)

    def compress_text(self):
        path = self.text_file_path.get()
        if not path:
            messagebox.showerror("Error", "Selecciona un archivo")
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            huffman = HuffmanCoder()
            bitstring, codes = huffman.encode(text)

            # Empaquetar bits a bytes
            padding = 8 - len(bitstring) % 8
            bitstring += '0' * padding
            b = bytearray()
            for i in range(0, len(bitstring), 8):
                b.append(int(bitstring[i:i + 8], 2))

            output_path = path.replace('.txt', '_compressed.bin')
            with open(output_path, 'wb') as f:
                pickle.dump((bytes(b), codes, padding), f)

            original_size = os.path.getsize(path)
            compressed_size = os.path.getsize(output_path)
            ratio = (1 - compressed_size / original_size) * 100

            messagebox.showinfo("Éxito",
                                f"Compresión completada\n\n"
                                f"Original: {original_size} bytes\n"
                                f"Comprimido: {compressed_size} bytes\n"
                                f"Ratio: {ratio:.2f}%")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def decompress_text(self):
        path = self.text_file_path.get()
        if not path:
            messagebox.showerror("Error", "Selecciona un archivo comprimido (.bin)")
            return
        try:
            with open(path, 'rb') as f:
                bit_bytes, codes, padding = pickle.load(f)

            # Convertir bytes a cadena de bits
            bitstring = ''.join(f'{byte:08b}' for byte in bit_bytes)
            bitstring = bitstring[:-padding]  # quitar padding

            huffman = HuffmanCoder()
            decoded = huffman.decode(bitstring, codes)

            output_path = path.replace('_compressed.bin', '_decompressed.txt')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(decoded)

            messagebox.showinfo("Éxito", f"Archivo descomprimido guardado en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- IMAGEN ----------
    def image_compression_window(self):
        self.clear_window()

        tk.Label(self.root, text="Compresión/Descompresión de Imágenes (RLE)",
                 font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)

        self.image_file_path = tk.StringVar()

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=10)

        tk.Button(frame, text="Seleccionar imagen (.png/.bmp/.rle)",
                  command=self.select_image_file).pack(pady=5)
        tk.Label(frame, textvariable=self.image_file_path,
                 bg="#f0f0f0", wraplength=400).pack(pady=5)

        tk.Button(frame, text="Comprimir",
                  command=self.compress_image, bg="#2196F3", fg="white").pack(pady=5)
        tk.Button(frame, text="Descomprimir",
                  command=self.decompress_image, bg="#9C27B0", fg="white").pack(pady=5)
        tk.Button(frame, text="Volver",
                  command=self.setup_main_menu).pack(pady=5)

    def select_image_file(self):
        file = filedialog.askopenfilename(filetypes=[("Image or RLE files", "*.png *.bmp *.rle")])
        if file:
            self.image_file_path.set(file)

    def compress_image(self):
        path = self.image_file_path.get()
        if not path:
            messagebox.showerror("Error", "Selecciona una imagen")
            return
        try:
            img = Image.open(path).convert("RGB")  # ✅ convierte a RGB
            pixels = list(img.getdata())

            # Cada pixel es una tupla (R, G, B)
            pixel_bytes = b''.join(bytes(p) for p in pixels)

            compressed = RLECoder.encode(pixel_bytes)
            output_path = path.rsplit('.', 1)[0] + '_compressed.rle'

            with open(output_path, 'wb') as f:
                f.write(img.size[0].to_bytes(4, 'big'))
                f.write(img.size[1].to_bytes(4, 'big'))
                f.write(compressed)

            original_size = os.path.getsize(path)
            compressed_size = os.path.getsize(output_path)
            ratio = (1 - compressed_size / original_size) * 100

            messagebox.showinfo("Éxito",
                                f"Compresión completada\n\n"
                                f"Original: {original_size} bytes\n"
                                f"Comprimido: {compressed_size} bytes\n"
                                f"Ratio: {ratio:.2f}%")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")

    def decompress_image(self):
        path = self.image_file_path.get()
        if not path.endswith('.rle'):
            messagebox.showerror("Error", "Selecciona un archivo .rle")
            return
        try:
            with open(path, 'rb') as f:
                width = int.from_bytes(f.read(4), 'big')
                height = int.from_bytes(f.read(4), 'big')
                compressed_data = f.read()
            decoded = RLECoder.decode(compressed_data)
            img = Image.frombytes('RGB', (width, height), decoded)
            output_path = path.replace('_compressed.rle', '_decompressed.png')
            img.save(output_path)
            messagebox.showinfo("Éxito", f"Imagen descomprimida guardada en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- AUDIO ----------
    def audio_compression_window(self):
        self.clear_window()

        tk.Label(self.root, text="Compresión/Descompresión de Audio (RLE)",
                 font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)

        self.audio_file_path = tk.StringVar()

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=10)

        tk.Button(frame, text="Seleccionar archivo (.wav/.rle)",
                  command=self.select_audio_file).pack(pady=5)
        tk.Label(frame, textvariable=self.audio_file_path,
                 bg="#f0f0f0", wraplength=400).pack(pady=5)

        tk.Button(frame, text="Comprimir",
                  command=self.compress_audio, bg="#2196F3", fg="white").pack(pady=5)
        tk.Button(frame, text="Descomprimir",
                  command=self.decompress_audio, bg="#9C27B0", fg="white").pack(pady=5)
        tk.Button(frame, text="Volver",
                  command=self.setup_main_menu).pack(pady=5)

    def select_audio_file(self):
        file = filedialog.askopenfilename(filetypes=[("Audio or RLE files", "*.wav *.rle")])
        if file:
            self.audio_file_path.set(file)

    def compress_audio(self):
        path = self.audio_file_path.get()
        if not path:
            messagebox.showerror("Error", "Selecciona un archivo .wav")
            return
        try:
            with wave.open(path, 'rb') as f:
                params = f.getparams()
                frames = f.readframes(f.getnframes())
            compressed = RLECoder.encode(frames)
            output_path = path.replace('.wav', '_compressed.rle')
            with open(output_path, 'wb') as f:
                f.write(params.nchannels.to_bytes(2, 'big'))
                f.write(params.sampwidth.to_bytes(2, 'big'))
                f.write(params.framerate.to_bytes(4, 'big'))
                f.write(compressed)
            messagebox.showinfo("Éxito", f"Audio comprimido guardado en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def decompress_audio(self):
        path = self.audio_file_path.get()
        if not path.endswith('.rle'):
            messagebox.showerror("Error", "Selecciona un archivo .rle")
            return
        try:
            with open(path, 'rb') as f:
                nchannels = int.from_bytes(f.read(2), 'big')
                sampwidth = int.from_bytes(f.read(2), 'big')
                framerate = int.from_bytes(f.read(4), 'big')
                compressed_data = f.read()
            decoded = RLECoder.decode(compressed_data)
            output_path = path.replace('_compressed.rle', '_decompressed.wav')
            with wave.open(output_path, 'wb') as f:
                f.setnchannels(nchannels)
                f.setsampwidth(sampwidth)
                f.setframerate(framerate)
                f.writeframes(decoded)
            messagebox.showinfo("Éxito", f"Audio descomprimido guardado en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = CompressionApp(root)
    root.mainloop()
