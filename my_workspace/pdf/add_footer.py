import fitz  # PyMuPDF
import glob
import os
import tomllib
import sys
import io
from PIL import Image

def add_images_to_pdf(pdf_path, images_config, output_path):
    """
    แทรกรูปภาพหลายๆ รูปตามตำแหน่ง x, y ของทุกหน้าใน PDF พร้อมรองรับการปรับขนาดและ Opacity
    """
    try:
        # เปิดไฟล์ PDF
        doc = fitz.open(pdf_path)
        
        # เตรียมข้อมูลรูปภาพทั้งหมด
        prepared_images = []
        for img_cfg in images_config:
            img_path = img_cfg.get("path")
            if not img_path or not os.path.exists(img_path):
                print(f"Warning: ไม่พบไฟล์รูปภาพที่ {img_path} ข้ามการประมวลผลรูปนี้")
                continue
                
            try:
                # เปิดรูปด้วย Pillow เพื่อจัดการ Opacity
                pil_img = Image.open(img_path).convert("RGBA")
                
                opacity = img_cfg.get("opacity", 1.0)
                if opacity < 1.0:
                    # ดึง Alpha channel ออกมาปรับค่าตามเปอร์เซ็นต์ opacity
                    alpha = pil_img.split()[3]
                    alpha = alpha.point(lambda p: p * opacity)
                    pil_img.putalpha(alpha)
                
                # แปลงรูปที่ปรับแล้วกลับเป็น Bytes (Memory)
                img_byte_arr = io.BytesIO()
                pil_img.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                
                # คำนวณขนาดภาพ
                img_width, img_height = pil_img.size
                aspect_ratio = img_width / img_height
                
                if "scale_percent" in img_cfg:
                    scale = img_cfg["scale_percent"] / 100.0
                    target_width = img_width * scale
                    target_height = img_height * scale
                else:
                    target_height = img_cfg.get("target_height", 50)
                    target_width = target_height * aspect_ratio
                
                pos_x = img_cfg.get("pos_x", 0)
                pos_y = img_cfg.get("pos_y", 0)
                
                prepared_images.append({
                    "stream": img_bytes,
                    "x0": pos_x,
                    "y0": pos_y,
                    "x1": pos_x + target_width,
                    "y1": pos_y + target_height
                })
            except Exception as img_e:
                print(f"Error processing image {img_path}: {img_e}")
            
        if not prepared_images:
            print(f"Error: ไม่พบรูปภาพที่สามารถใช้ได้เลยสำหรับ {pdf_path}")
            return
        
        # วนลูปทีละหน้าใน PDF
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # วางรูปภาพทั้งหมดลงในหน้านี้
            for p_img in prepared_images:
                image_rect = fitz.Rect(p_img["x0"], p_img["y0"], p_img["x1"], p_img["y1"])
                # วางรูปโดยอ่านจาก Memory (stream)
                page.insert_image(image_rect, stream=p_img["stream"])
            
        # บันทึกไฟล์ใหม่
        doc.save(output_path)
        doc.close()
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการประมวลผล {pdf_path}: {e}")

def main():
    # โหลด config file
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.toml")
    
    if not os.path.exists(config_path):
        print(f"Error: ไม่พบไฟล์ config ที่ {config_path}")
        sys.exit(1)
        
    with open(config_path, "rb") as f:
        config = tomllib.load(f)
        
    source_dir = config["paths"]["source_dir"]
    output_dir = config["paths"]["output_dir"]
    images_config = config.get("images", [])
    
    if not images_config:
        print("Error: ไม่มีการตั้งค่ารูปภาพใน config.toml (ส่วนของ [[images]])")
        sys.exit(1)
    
    # สร้างโฟลเดอร์ output หากยังไม่มี
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # ค้นหาไฟล์ PDF ทั้งหมดในโฟลเดอร์ source
    pdf_files = glob.glob(os.path.join(source_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"ไม่พบไฟล์ PDF ในโฟลเดอร์ต้นทาง: {source_dir}")
    else:
        print(f"พบไฟล์ PDF จำนวน {len(pdf_files)} ไฟล์ กำลังเริ่มประมวลผล...\n")
        
    for pdf_file in pdf_files:
        filename = os.path.basename(pdf_file)
        output_file = os.path.join(output_dir, filename)
        
        print(f"กำลังประมวลผล: {filename}...")
        add_images_to_pdf(pdf_file, images_config, output_file)
        print(f"  -> บันทึกเรียบร้อยที่: {output_file}\n")
        
    print("เสร็จสิ้นการทำงานทั้งหมด!")

if __name__ == "__main__":
    main()
