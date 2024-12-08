import pywt
import numpy as np
from PIL import Image

def int_to_bits(x, bit_length):
    return [int(b) for b in format(x, '0{}b'.format(bit_length))]

def bits_to_int(bits):
    bit_str = ''.join(str(b) for b in bits)
    return int(bit_str, 2)

def image_to_bits(img_path):
    img = Image.open(img_path).convert('L')
    arr = np.array(img, dtype=np.uint8)
    h, w = arr.shape
    pixels = arr.flatten()
    bits = []
    for p in pixels:
        bits.extend(int_to_bits(p, 8))
    return w, h, bits

def bits_to_image(width, height, bits):
    if len(bits) < width * height * 8:
        raise ValueError("Not enough bits to reconstruct the image.")
    pixels = []
    for i in range(0, len(bits), 8):
        byte_bits = bits[i:i+8]
        p = bits_to_int(byte_bits)
        pixels.append(p)
    arr = np.array(pixels, dtype=np.uint8).reshape((height, width))
    return Image.fromarray(arr)

def embed_bits_in_coefficients(coeffs, bits):
    flat_coeffs = coeffs.flatten()
    if len(bits) > len(flat_coeffs):
        raise ValueError("Not enough capacity in coefficients to embed the data.")
    for i, bit in enumerate(bits):
        val = flat_coeffs[i]
        if (val % 2) != bit:
            val = val - 1 if (val % 2 == 1) else val + 1
        flat_coeffs[i] = val
    return flat_coeffs.reshape(coeffs.shape)

def embed_image_in_image(cover_image_path, secret_image_path, stego_image_path):
    cover = Image.open(cover_image_path).convert('L')
    cover_arr = np.array(cover, dtype=np.float32)
    
    coeffs2 = pywt.dwt2(cover_arr, 'haar')
    LL, (LH, HL, HH) = coeffs2

    LL_int = np.rint(LL).astype(np.int32)
    LH_int = np.rint(LH).astype(np.int32)
    HL_int = np.rint(HL).astype(np.int32)
    HH_int = np.rint(HH).astype(np.int32)

   
    w, h, secret_bits = image_to_bits(secret_image_path)
    
   
    width_bits = int_to_bits(w, 16)
    height_bits = int_to_bits(h, 16)
    all_bits = width_bits + height_bits + secret_bits

    
    LH_modified = embed_bits_in_coefficients(LH_int, all_bits)

    # LH_modified = embed_bits_in_coefficients(LH, msg_bits[:len(LH.flatten())])
    # HL_modified = embed_bits_in_coefficients(HL, msg_bits[len(LH.flatten()):len(LH.flatten()) + len(HL.flatten())])
    # HH_modified = embed_bits_in_coefficients(HH, msg_bits[len(LH.flatten()) + len(HL.flatten()):len(LH.flatten()) + len(HL.flatten()) + len(HH.flatten())])
    # new_coeffs = (LL, (LH_modified, HL_modified, HH_modified))


   
    LL_mod = LL_int.astype(np.float32)
    LH_mod = LH_modified.astype(np.float32)
    HL_mod = HL_int.astype(np.float32)
    HH_mod = HH_int.astype(np.float32)

    new_coeffs = (LL_mod, (LH_mod, HL_mod, HH_mod))
    stego_arr = pywt.idwt2(new_coeffs, 'haar')
    stego_arr = np.clip(stego_arr, 0, 255).astype(np.uint8)
    stego_img = Image.fromarray(stego_arr)
    stego_img.save(stego_image_path)
    print("Secret image embedded successfully into:", stego_image_path)

def extract_image_from_image(stego_image_path):
    
    stego = Image.open(stego_image_path).convert('L')
    stego_arr = np.array(stego, dtype=np.float32)

 
    coeffs2 = pywt.dwt2(stego_arr, 'haar')
    LL, (LH, HL, HH) = coeffs2

  
    LH_int = np.rint(LH).astype(np.int32)
    LH_flat = LH_int.flatten()

  
    width_bits = [(LH_flat[i] & 1) for i in range(16)]
    width = bits_to_int(width_bits)

    height_bits = [(LH_flat[i] & 1) for i in range(16, 32)]
    height = bits_to_int(height_bits)

    pixel_bits_needed = width * height * 8
    start = 32
    end = 32 + pixel_bits_needed
    if end > len(LH_flat):
        raise ValueError("Not enough data to extract secret image.")
    secret_bits = [(LH_flat[i] & 1) for i in range(start, end)]

    secret_img = bits_to_image(width, height, secret_bits)
    return secret_img

# if __name__ == "__main__":
#     cover_path = "lenna.png"   
#     secret_path = "delfin64.png" 
#     stego_path = "stego_image_with_secret_image.png"
#     embed_image_in_image(cover_path, secret_path, stego_path)
#     extracted_img = extract_image_from_image(stego_path)
#     extracted_img.save("extracted_secret_image.png")
#     print("Secret image extracted and saved as extracted_secret_image.png")