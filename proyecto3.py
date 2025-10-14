import tkinter as tk
from tkinter import filedialog, messagebox
import heapq
import os
from PIL import Image
import wave
from collections import Counter


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
                code = bitstring[i:i+length]
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
        self.root.geometry("500x400")
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
            ("Comprimir Texto", self.text_compression_window),
            ("Comprimir Imágenes", self.image_compression_window),
            ("Comprimir Audio", self.audio_compression_window)
        ]
        
        for text, command in buttons_config:
            btn = tk.Button(frame, text=text, font=("Arial", 12), 
                           width=25, height=2, command=command,
                           bg="#4CAF50", fg="white")
            btn.pack(pady=10)
    
    def clear_window(self):
        """Limpia todos los widgets de la ventana"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def text_compression_window(self):
        """Ventana para compresión de texto"""
        self.clear_window()
        
        tk.Label(self.root, text="Compresión de Texto (Huffman)", 
                font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)
        
        self.text_file_path = tk.StringVar()
        
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=10)
        
        tk.Button(frame, text="Seleccionar archivo .txt", 
                 command=self.select_text_file).pack(pady=5)
        tk.Label(frame, textvariable=self.text_file_path, 
                bg="#f0f0f0", wraplength=400).pack(pady=5)
        
        tk.Button(frame, text="Comprimir", 
                 command=self.compress_text, bg="#2196F3", fg="white").pack(pady=5)
        tk.Button(frame, text="Volver", 
                 command=self.setup_main_menu).pack(pady=5)
    
    def select_text_file(self):
        file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
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
            
            output_path = path.replace('.txt', '_compressed.bin')
            
            import pickle
            with open(output_path, 'wb') as f:
                pickle.dump((bitstring, codes), f)
            
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
    
    def image_compression_window(self):
        """Ventana para compresión de imágenes"""
        self.clear_window()
        
        tk.Label(self.root, text="Compresión de Imágenes (RLE)", 
                font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)
        
        self.image_file_path = tk.StringVar()
        
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=10)
        
        tk.Button(frame, text="Seleccionar imagen (.png/.bmp)", 
                 command=self.select_image_file).pack(pady=5)
        tk.Label(frame, textvariable=self.image_file_path, 
                bg="#f0f0f0", wraplength=400).pack(pady=5)
        
        tk.Button(frame, text="Comprimir", 
                 command=self.compress_image, bg="#2196F3", fg="white").pack(pady=5)
        tk.Button(frame, text="Volver", 
                 command=self.setup_main_menu).pack(pady=5)
    
    def select_image_file(self):
        file = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.bmp *.jpg")])
        if file:
            self.image_file_path.set(file)
    
    def compress_image(self):
        path = self.image_file_path.get()
        if not path:
            messagebox.showerror("Error", "Selecciona una imagen")
            return
        
        try:
            img = Image.open(path)
            pixels = list(img.getdata())
            pixel_bytes = b''.join(p.to_bytes(3, 'big') if isinstance(p, int) else 
                                  bytes(p[:3]) for p in pixels)
            
            compressed = RLECoder.encode(pixel_bytes)
            
            output_path = path.rsplit('.', 1)[0] + '_compressed.rle'
            
            with open(output_path, 'wb') as f:
                f.write(img.size[0].to_bytes(4, 'big'))
                f.write(img.size[1].to_bytes(4, 'big'))
                f.write(len(compressed).to_bytes(8, 'big'))
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
    
    def audio_compression_window(self):
        """Ventana para compresión de audio"""
        self.clear_window()
        
        tk.Label(self.root, text="Compresión de Audio (RLE)", 
                font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)
        
        self.audio_file_path = tk.StringVar()
        
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=10)
        
        tk.Button(frame, text="Seleccionar archivo (.wav/.mp3)", 
                 command=self.select_audio_file).pack(pady=5)
        tk.Label(frame, textvariable=self.audio_file_path, 
                bg="#f0f0f0", wraplength=400).pack(pady=5)
        
        tk.Button(frame, text="Comprimir", 
                 command=self.compress_audio, bg="#2196F3", fg="white").pack(pady=5)
        tk.Button(frame, text="Volver", 
                 command=self.setup_main_menu).pack(pady=5)
    
    def select_audio_file(self):
        file = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav *.mp3")])
        if file:
            self.audio_file_path.set(file)
    
    def compress_audio(self):
        path = self.audio_file_path.get()
        if not path:
            messagebox.showerror("Error", "Selecciona un archivo de audio")
            return
        
        try:
            if path.endswith('.wav'):
                with wave.open(path, 'rb') as f:
                    frames = f.readframes(f.getnframes())
                
                compressed = RLECoder.encode(frames)
                
                output_path = path.rsplit('.', 1)[0] + '_compressed.rle'
                with open(output_path, 'wb') as f:
                    f.write(compressed)
                
                original_size = os.path.getsize(path)
                compressed_size = os.path.getsize(output_path)
                ratio = (1 - compressed_size / original_size) * 100
                
                messagebox.showinfo("Éxito", 
                    f"Compresión completada\n\n"
                    f"Original: {original_size} bytes\n"
                    f"Comprimido: {compressed_size} bytes\n"
                    f"Ratio: {ratio:.2f}%")
            else:
                messagebox.showerror("Error", "Por ahora solo se soportan archivos .wav")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CompressionApp(root)
    root.mainloop()