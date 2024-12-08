import streamlit as st
from PIL import Image
import os


from steganography_text import embed_message_in_image, extract_message_from_image
from steganography_image import embed_image_in_image, extract_image_from_image

st.title("Steganography UI")


cover_file = st.file_uploader("Upload Cover Image:", type=["png", "jpg", "jpeg"])
if cover_file is not None:
    cover_image = Image.open(cover_file).convert('L')
    st.image(cover_image, caption="Cover Image")


option = st.radio("What do you want to hide?", ("Text", "Image"), index=0)


secret_text = None
secret_image_file = None
if option == "Text":
    secret_text = st.text_input("Enter the text you want to hide:")
else:  
    secret_image_file = st.file_uploader("Upload Secret Image:", type=["png", "jpg", "jpeg"])
    if secret_image_file is not None:
        secret_image_preview = Image.open(secret_image_file).convert('L')
        st.image(secret_image_preview, caption="Secret Image")

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)
cover_path = os.path.join(output_dir, "cover_temp.png")
stego_path = os.path.join(output_dir, "stego_temp.png")

if cover_file is not None:
    cover_image.save(cover_path)


if st.button("Embed"):
    if cover_file is None:
        st.warning("Please upload a cover image.")
    else:
        if option == "Text":
            if not secret_text:
                st.warning("Please enter some text to hide.")
            else:
               
                embed_message_in_image(cover_path, secret_text, stego_path)
                st.success("Text hidden in image!")
                stego_img = Image.open(stego_path)
                st.image(stego_img, caption="Stego Image")
        else:
            if secret_image_file is None:
                st.warning("Please upload a secret image.")
            else:
                
                secret_image_path = os.path.join(output_dir, "secret_temp.png")
                secret_image_preview.save(secret_image_path)
                embed_image_in_image(cover_path, secret_image_path, stego_path)
                st.success("Image hidden in image!")
                stego_img = Image.open(stego_path)
                st.image(stego_img, caption="Stego Image")


if st.button("Extract"):
    if cover_file is None:
        st.warning("Please upload a cover image and embed data first.")
    else:
        
        if option == "Text":
            if not secret_text:
                st.warning("We must have embedded text first.")
            else:
                
                extracted_message = extract_message_from_image(stego_path, len(secret_text))
                st.write("Extracted Text: ", extracted_message)
        else:
            if secret_image_file is None:
                st.warning("We must have embedded an image first.")
            else:
                
                extracted_img = extract_image_from_image(stego_path)
                extracted_path = os.path.join(output_dir, "extracted_secret.png")
                extracted_img.save(extracted_path)
                st.write("Extracted Secret Image:")
                st.image(extracted_img, caption="Extracted Secret Image")
