
import pywt
import numpy as np
from PIL import Image

def calculate_psnr(original, stego):
    """
    Calculate PSNR (Peak Signal-to-Noise Ratio) between two images.
    
    Parameters:
        original: 2D numpy array of the original image.
        stego: 2D numpy array of the stego image.
    
    Returns:
        PSNR value in dB.
    """
    mse = np.mean((original - stego) ** 2)
    if mse == 0:  # No error
        return float('inf')
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr

def message_to_bits(message):
    bits = []
    for char in message:
        char_code = ord(char)
        bits.extend([int(b) for b in format(char_code, '08b')])
    return bits

def bits_to_message(bits):
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        byte_str = ''.join(str(bit) for bit in byte)
        chars.append(chr(int(byte_str, 2)))
    return ''.join(chars)

def embed_bits_in_coefficients(coeffs, bits):
    flat_coeffs = coeffs.flatten()
    if len(bits) > len(flat_coeffs):
        raise ValueError("Message too large to fit in the given coefficients.")
    for i, bit in enumerate(bits):
        val = int(round(flat_coeffs[i]))
        if (val % 2) != bit:
            val = val - 1 if (val % 2 == 1) else val + 1
        flat_coeffs[i] = val
    return flat_coeffs.reshape(coeffs.shape)

def extract_bits_from_coefficients(coeffs, num_bits):
    flat_coeffs = coeffs.flatten()
    bits = []
    for i in range(num_bits):
        val = int(round(flat_coeffs[i]))
        bits.append(val % 2)
    return bits

def embed_message_in_image(cover_image_path, secret_message, stego_image_path):
    cover = Image.open(cover_image_path).convert('L')
    cover_arr = np.array(cover, dtype=np.float32)
    coeffs2 = pywt.dwt2(cover_arr, 'haar')
    LL, (LH, HL, HH) = coeffs2
    msg_bits = message_to_bits(secret_message)
    LH_modified = embed_bits_in_coefficients(LH, msg_bits)
    new_coeffs = (LL, (LH_modified, HL, HH))
    stego_arr = pywt.idwt2(new_coeffs, 'haar')
    stego_arr = np.clip(stego_arr, 0, 255).astype(np.uint8)
    stego_img = Image.fromarray(stego_arr)
    stego_img.save(stego_image_path)
    print("Message embedded and stego image saved at:", stego_image_path)
    
    psnr = calculate_psnr(cover_arr.astype(np.uint8), stego_arr)
    print(f"PSNR between cover and stego image: {psnr:.2f} dB")

def extract_message_from_image(stego_image_path, message_length):
    stego = Image.open(stego_image_path).convert('L')
    stego_arr = np.array(stego, dtype=np.float32)
    coeffs2 = pywt.dwt2(stego_arr, 'haar')
    LL, (LH, HL, HH) = coeffs2
    num_bits = message_length * 8
    extracted_bits = extract_bits_from_coefficients(LH, num_bits)
    extracted_message = bits_to_message(extracted_bits)
    return extracted_message


# if __name__ == "__main__":
#    
#     cover_path = "lenna.png"   # 
#     stego_path = "stego_image_with_secret_text.png" 
#     message = "Hello, this is a secret!"
#     embed_message_in_image(cover_path, message, stego_path)
    

