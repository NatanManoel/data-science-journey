import os
import zlib
import struct
import math

def create_svg():
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="50%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#0284c7"/>
    </linearGradient>
    <linearGradient id="glowGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="50%" stop-color="#818cf8"/>
      <stop offset="100%" stop-color="#34d399"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background with rounded rectangle for mobile app icon -->
  <rect width="512" height="512" rx="112" fill="url(#bgGrad)"/>
  <rect x="16" y="16" width="480" height="480" rx="98" fill="none" stroke="url(#glowGrad)" stroke-width="6" opacity="0.4"/>

  <!-- Pulse & Data Nodes Design -->
  <!-- Circuit / Synapse connections -->
  <path d="M 120 256 L 200 256 L 230 180 L 280 340 L 320 220 L 350 256 L 392 256" 
        fill="none" stroke="url(#glowGrad)" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)"/>

  <!-- Network Nodes -->
  <!-- Top Node -->
  <circle cx="256" cy="140" r="22" fill="#38bdf8" filter="url(#glow)"/>
  <line x1="256" y1="140" x2="230" y2="180" stroke="#38bdf8" stroke-width="8" opacity="0.7"/>
  <line x1="256" y1="140" x2="320" y2="220" stroke="#38bdf8" stroke-width="8" opacity="0.7"/>

  <!-- Bottom Node -->
  <circle cx="256" cy="380" r="22" fill="#34d399" filter="url(#glow)"/>
  <line x1="256" y1="380" x2="280" y2="340" stroke="#34d399" stroke-width="8" opacity="0.7"/>
  <line x1="256" y1="380" x2="200" y2="256" stroke="#34d399" stroke-width="8" opacity="0.7"/>

  <!-- Left / Right Nodes -->
  <circle cx="120" cy="256" r="18" fill="#818cf8"/>
  <circle cx="392" cy="256" r="18" fill="#34d399"/>

  <!-- Core Pulse Nodes -->
  <circle cx="230" cy="180" r="14" fill="#ffffff"/>
  <circle cx="280" cy="340" r="14" fill="#ffffff"/>
  <circle cx="320" cy="220" r="14" fill="#ffffff"/>

  <!-- Small Floating Data Sparks -->
  <circle cx="170" cy="170" r="6" fill="#38bdf8" opacity="0.8"/>
  <circle cx="350" cy="350" r="6" fill="#34d399" opacity="0.8"/>
  <circle cx="360" cy="160" r="8" fill="#818cf8" opacity="0.8"/>
</svg>"""

def make_png(width, height):
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    raw_data = bytearray()
    cx, cy = width / 2.0, height / 2.0
    r_max = width / 2.0

    for y in range(height):
        raw_data.append(0) # filter type 0
        for x in range(width):
            dx = (x - cx) / cx
            dy = (y - cy) / cy
            dist = math.sqrt(dx * dx + dy * dy)

            # Squircle / rounded box mask
            corner_power = (abs(dx)**4 + abs(dy)**4)
            if corner_power > 1.05:
                # Outside icon area (transparent)
                raw_data.extend([0, 0, 0, 0])
                continue

            # Background gradient from top-left (#0f172a) to bottom-right (#0369a1)
            t = (dx + dy + 2.0) / 4.0
            t = max(0.0, min(1.0, t))
            bg_r = int(15 * (1 - t) + 3 * t)
            bg_g = int(23 * (1 - t) + 105 * t)
            bg_b = int(42 * (1 - t) + 161 * t)

            # Center pulse / energy wave rendering
            py = cy + math.sin(x * 0.08) * (height * 0.18) if 0.2 * width < x < 0.8 * width else cy
            dist_to_pulse = abs(y - py)
            
            # Central core nodes
            dist_c1 = math.hypot(x - cx, y - cy)
            dist_c2 = math.hypot(x - cx * 0.7, y - cy * 0.8)
            dist_c3 = math.hypot(x - cx * 1.3, y - cy * 1.2)

            is_node = dist_c1 < width * 0.08 or dist_c2 < width * 0.06 or dist_c3 < width * 0.06
            is_pulse = dist_to_pulse < (width * 0.035) and (0.2 * width < x < 0.8 * width)

            if is_node:
                raw_data.extend([56, 189, 248, 255]) # Cyan glow node
            elif is_pulse:
                raw_data.extend([52, 211, 153, 255]) # Emerald wave
            elif corner_power > 0.95:
                # Border glow
                raw_data.extend([56, 189, 248, 200])
            else:
                raw_data.extend([bg_r, bg_g, bg_b, 255])

    compressed = zlib.compress(bytes(raw_data), 9)
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', compressed) + chunk(b'IEND', b'')

def main():
    svg_content = create_svg()
    
    # Salvar SVGs
    for path in ['icon.svg', 'public/icon.svg']:
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"Salvo: {path}")

    # Gerar PNG 192x192 e 512x512
    png_192 = make_png(192, 192)
    png_512 = make_png(512, 512)

    for p, size, data in [('icon-192.png', 192, png_192), ('icon-512.png', 512, png_512),
                          ('public/icon-192.png', 192, png_192), ('public/icon-512.png', 512, png_512)]:
        with open(p, 'wb') as f:
            f.write(data)
        print(f"Gerado PNG: {p}")

    # Gerar manifest.json
    manifest = """{
  "name": "Rotina & Data Science",
  "short_name": "Rotina DS",
  "description": "Acompanhamento de rotina, treinos e estudos do MBA Data Science USP",
  "start_url": "./index.html",
  "display": "standalone",
  "background_color": "#0f172a",
  "theme_color": "#0f172a",
  "icons": [
    {
      "src": "icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "icon.svg",
      "sizes": "512x512",
      "type": "image/svg+xml",
      "purpose": "any maskable"
    }
  ]
}"""
    for m_path in ['manifest.json', 'public/manifest.json']:
        with open(m_path, 'w', encoding='utf-8') as f:
            f.write(manifest)
        print(f"Salvo: {m_path}")

if __name__ == '__main__':
    main()

