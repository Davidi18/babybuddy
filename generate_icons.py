#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate all icons and favicons from the logo
"""
from PIL import Image
import os

# Source logo
SOURCE_LOGO = "final_logo.png"
OUTPUT_DIR = "babybuddy/static_src/root"

# Icon sizes to generate
ICON_SIZES = {
    "favicon.ico": [(16, 16), (32, 32), (48, 48)],  # ICO with multiple sizes
    "apple-touch-icon.png": (180, 180),
    "android-chrome-192x192.png": (192, 192),
    "android-chrome-512x512.png": (512, 512),
    "mstile-150x150.png": (150, 150),
}

# Also update the main logo files
LOGO_SIZES = {
    "icon-brand.png": (512, 512),  # Used in navbar
    "icon.png": (512, 512),
}

def create_icon(img, size, output_path):
    """Create a resized icon"""
    # Create a copy and resize with high quality
    icon = img.copy()
    icon.thumbnail(size, Image.Resampling.LANCZOS)

    # If the image is smaller than requested size, create a new image and paste
    if icon.size != size:
        new_icon = Image.new('RGBA', size, (0, 0, 0, 0))
        offset = ((size[0] - icon.size[0]) // 2, (size[1] - icon.size[1]) // 2)
        new_icon.paste(icon, offset)
        icon = new_icon

    return icon

def main():
    print("🎨 Creating icons from logo...")

    # Load the source logo
    if not os.path.exists(SOURCE_LOGO):
        print(f"❌ Error: {SOURCE_LOGO} not found!")
        return

    print(f"📂 Loading {SOURCE_LOGO}...")
    logo = Image.open(SOURCE_LOGO)

    # Ensure it has an alpha channel
    if logo.mode != 'RGBA':
        logo = logo.convert('RGBA')

    print(f"✅ Logo loaded: {logo.size[0]}x{logo.size[1]}")

    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate icons for root directory
    print(f"\n📱 Generating icons for {OUTPUT_DIR}...")
    for filename, size in ICON_SIZES.items():
        output_path = os.path.join(OUTPUT_DIR, filename)

        if filename.endswith('.ico'):
            # For ICO files, create multiple sizes
            print(f"  🔸 Creating {filename} with sizes: {size}")
            icon_images = []
            for ico_size in size:
                icon = create_icon(logo, ico_size, output_path)
                icon_images.append(icon)

            # Save as ICO with multiple sizes
            icon_images[0].save(output_path, format='ICO', sizes=size)
        else:
            # For PNG files
            print(f"  🔸 Creating {filename} ({size[0]}x{size[1]})")
            icon = create_icon(logo, size, output_path)
            icon.save(output_path, 'PNG', optimize=True)

    # Generate logo files for logo directory
    logo_dir = "babybuddy/static_src/logo"
    print(f"\n🖼️  Generating logos for {logo_dir}...")
    for filename, size in LOGO_SIZES.items():
        output_path = os.path.join(logo_dir, filename)
        print(f"  🔸 Creating {filename} ({size[0]}x{size[1]})")
        icon = create_icon(logo, size, output_path)
        icon.save(output_path, 'PNG', optimize=True)

    # Special: create apple-touch-startup-image (splash screen)
    startup_path = os.path.join(OUTPUT_DIR, "apple-touch-startup-image.png")
    print(f"\n📱 Creating startup image: {startup_path}")
    startup_size = (2048, 2732)  # iPad Pro 12.9" portrait
    startup_img = Image.new('RGBA', startup_size, (33, 37, 41, 255))  # Bootstrap dark bg

    # Place logo in center
    logo_for_startup = create_icon(logo, (800, 800), startup_path)
    offset = ((startup_size[0] - 800) // 2, (startup_size[1] - 800) // 2)
    startup_img.paste(logo_for_startup, offset, logo_for_startup)
    startup_img.save(startup_path, 'PNG', optimize=True)

    print("\n✅ All icons created successfully!")
    print("\n📋 Next steps:")
    print("  1. Run: python manage.py collectstatic --noinput")
    print("  2. Restart your server")
    print("  3. Clear browser cache to see the new icons")

if __name__ == "__main__":
    main()
