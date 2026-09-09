from PIL import Image, ImageDraw, ImageFont
import os

os.makedirs("data/sample_records", exist_ok=True)

# 1. Clean Sample
img1 = Image.new('RGB', (800, 1000), color='#fcfbf7')
d1 = ImageDraw.Draw(img1)
d1.rectangle([20, 20, 780, 980], outline='#1e293b', width=3)
d1.text((250, 50), "FORM K-1: KHASRA KHATONI RECORD", fill='#0f172a')
d1.text((50, 120), "District: Bhopal    Tehsil: Sadar    Village: Rampur", fill='#1e293b')
d1.text((50, 170), "--------------------------------------------------------", fill='#64748b')
d1.text((50, 210), "Khasra Number: 142/1", fill='#0f172a')
d1.text((50, 250), "Khata Number: 88", fill='#0f172a')
d1.text((50, 290), "Survey Number: 504", fill='#0f172a')
d1.text((50, 330), "Land Owner Name: Ramesh Chandra Sharma", fill='#0f172a')
d1.text((50, 370), "Father/Husband Name: Suresh Sharma", fill='#0f172a')
d1.text((50, 410), "Land Area: 1.450 Hectares", fill='#0f172a')
d1.text((50, 450), "Land Classification: Agricultural (Irrigated)", fill='#0f172a')
d1.text((50, 490), "Mutation Details: Transferred via Inheritance 2021", fill='#0f172a')
img1.save("data/sample_records/khasra_sample_clean.png")

# 2. Handwritten / Poor Quality Sample
img2 = Image.new('RGB', (800, 1000), color='#f4efe6')
d2 = ImageDraw.Draw(img2)
d2.rectangle([15, 15, 785, 985], outline='#475569', width=2)
d2.text((200, 50), "RAAJASVA VIBHAAG - BHUMI ABHILEKH", fill='#334155')
d2.text((50, 130), "Zila: Indore    Tehsil: Sanwer    Gram: Vijaypur", fill='#334155')
d2.text((50, 200), "Khasra No: 58/3", fill='#1e293b')
d2.text((50, 240), "Khata Uni No: 104", fill='#1e293b')
d2.text((50, 280), "Swami Name: Sunita Devi W/o Rameshwar", fill='#1e293b')
d2.text((50, 320), "Area: 0.850 Hec", fill='#1e293b')
img2.save("data/sample_records/khasra_sample_handwritten.png")

print("Generated sample scanned document images in data/sample_records/")
