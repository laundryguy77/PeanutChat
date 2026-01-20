# Claude Code Task: Verify, Test, and Complete the Unified Image Generation MCP Server

## Executive Summary

This is an MCP (Model Context Protocol) server providing comprehensive AI image generation via free Hugging Face Spaces:

| Capability | Description |
|------------|-------------|
| **text_to_image** | Generate images from text descriptions |
| **image_to_image** | Transform/restyle existing images (img2img) |
| **inpaint_image** | Edit specific regions using masks |
| **upscale_image** | Enhance image resolution |

Since HuggingFace Spaces have no official API, this uses **Playwright browser automation** to control Gradio-based web interfaces.

---

## Project Files

| File | Purpose | Lines |
|------|---------|-------|
| `server.py` | MCP server - JSON-RPC protocol, 6 tools defined | ~350 |
| `image_backends.py` | 4 backend classes + unified generator | ~550 |
| `gradio_automation.py` | Base Playwright automation for Gradio UIs | ~300 |
| `requirements.txt` | Just `playwright>=1.40.0` | 1 |
| `README.md` | Documentation | ~250 |

---

## Target Hugging Face Spaces

### Text-to-Image
```
Primary:   https://huggingface.co/spaces/black-forest-labs/FLUX.1-schnell
Fallback:  https://huggingface.co/spaces/stabilityai/stable-diffusion-3.5-large
Fallback:  https://huggingface.co/spaces/multimodalart/FLUX.1-merged
```

### Image-to-Image
```
Primary:   https://huggingface.co/spaces/diffusers/stable-diffusion-xl-img2img
Fallback:  https://huggingface.co/spaces/multimodalart/cosxl
```

### Inpainting
```
Primary:   https://huggingface.co/spaces/diffusers/stable-diffusion-xl-inpainting
Fallback:  https://huggingface.co/spaces/runwayml/stable-diffusion-inpainting
```

### Upscaling
```
Primary:   https://huggingface.co/spaces/finegrain/finegrain-image-enhancer
Fallback:  https://huggingface.co/spaces/Kwai-Kolors/SUPIR
```

---

## Your Tasks - Use Subagents for Parallel Execution

### STREAM 1: Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Verify
python -c "from playwright.async_api import async_playwright; print('✓ Playwright OK')"
python -m py_compile server.py image_backends.py gradio_automation.py && echo "✓ Syntax OK"
```

---

### STREAM 2: Inspect Text-to-Image Space (CRITICAL)

Visit `https://huggingface.co/spaces/black-forest-labs/FLUX.1-schnell`

Document the following:
1. **Prompt input selector** - What element takes the text prompt?
2. **Negative prompt field** - Does it exist? What selector?
3. **Dimension controls** - Width/height sliders or dropdowns?
4. **Generate button** - Exact text and selector
5. **Output image element** - Where does the generated image appear?
6. **Loading indicators** - CSS classes for generation progress

**Deliverable:** Update `TextToImageBackend` class in `image_backends.py` with verified selectors.

---

### STREAM 3: Inspect Image-to-Image Space (CRITICAL)

Visit `https://huggingface.co/spaces/diffusers/stable-diffusion-xl-img2img` (or `multimodalart/cosxl`)

Document:
1. **Image upload component** - File input selector
2. **Prompt input** - Where to enter transformation prompt
3. **Strength slider** - How to set transformation strength
4. **Generate button** - Selector
5. **Output image** - Where result appears

**Deliverable:** Update `ImageToImageBackend` class with verified selectors.

---

### STREAM 4: Inspect Inpainting Space

Visit `https://huggingface.co/spaces/diffusers/stable-diffusion-xl-inpainting`

Document:
1. **Image upload** - First file input (source image)
2. **Mask upload** - Second file input (or drawing tool?)
3. **Prompt input** - Selector
4. **Generate button** - Selector
5. **Output** - Where result appears

**Note:** Some inpainting spaces have a built-in mask drawing tool instead of file upload. Document which type this is.

**Deliverable:** Update `InpaintingBackend` class with verified selectors.

---

### STREAM 5: Inspect Upscale Space

Visit `https://huggingface.co/spaces/finegrain/finegrain-image-enhancer`

Document:
1. **Image upload** - Selector
2. **Scale selector** - Dropdown or slider?
3. **Process button** - Selector
4. **Output image** - Selector

**Deliverable:** Update `UpscaleBackend` class with verified selectors.

---

### STREAM 6: Test Gradio Base Automation

```bash
python -c "
import asyncio
from gradio_automation import GradioAutomation

async def test():
    auto = GradioAutomation('https://huggingface.co/spaces/black-forest-labs/FLUX.1-schnell')
    await auto.start()
    context = await auto.new_context()
    page = await context.new_page()
    
    print('Loading FLUX.1-schnell space...')
    await page.goto(auto.space_url, wait_until='networkidle', timeout=60000)
    await auto.wait_for_gradio_load(page)
    await auto.dismiss_popups(page)
    
    # Screenshot for inspection
    await page.screenshot(path='/tmp/flux_loaded.png')
    print('✓ Screenshot: /tmp/flux_loaded.png')
    
    # Inventory page elements
    textareas = await page.query_selector_all('textarea')
    buttons = await page.query_selector_all('button')
    inputs = await page.query_selector_all('input')
    
    print(f'Found: {len(textareas)} textareas, {len(buttons)} buttons, {len(inputs)} inputs')
    
    for i, btn in enumerate(buttons[:10]):
        text = await btn.inner_text()
        classes = await btn.get_attribute('class') or ''
        print(f'  Button {i}: \"{text[:30]}\" class=\"{classes[:50]}\"')
    
    await context.close()
    await auto.close()
    print('✓ Base automation test passed')

asyncio.run(test())
"
```

---

### STREAM 7: Create Test Images

```bash
# Create test images for img2img and inpainting tests
python -c "
try:
    from PIL import Image, ImageDraw
    
    # Test image - simple scene
    img = Image.new('RGB', (512, 512), color='skyblue')
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 300, 400, 500], fill='green')  # Grass
    draw.ellipse([200, 100, 350, 250], fill='yellow')   # Sun
    img.save('/tmp/test_scene.png')
    print('✓ Created /tmp/test_scene.png')
    
    # Mask for inpainting (white circle in center)
    mask = Image.new('RGB', (512, 512), color='black')
    draw = ImageDraw.Draw(mask)
    draw.ellipse([156, 156, 356, 356], fill='white')
    mask.save('/tmp/test_mask.png')
    print('✓ Created /tmp/test_mask.png')
    
except ImportError:
    # Fallback without PIL
    print('PIL not available, creating minimal PNG files...')
    
    # Minimal valid PNG (1x1 blue pixel)
    import struct, zlib
    def make_png(filename, r, g, b):
        def chunk(t, d):
            return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
        ihdr = struct.pack('>IIBBBBB', 512, 512, 8, 2, 0, 0, 0)
        raw = b''.join([b'\\x00' + bytes([r, g, b]) * 512 for _ in range(512)])
        with open(filename, 'wb') as f:
            f.write(b'\\x89PNG\\r\\n\\x1a\\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))
    
    make_png('/tmp/test_scene.png', 135, 206, 235)  # Sky blue
    make_png('/tmp/test_mask.png', 255, 255, 255)   # White
    print('✓ Created test images (fallback method)')
"

ls -la /tmp/test_scene.png /tmp/test_mask.png
```

---

### STREAM 8: Test Text-to-Image End-to-End

```bash
python -c "
import asyncio
from image_backends import UnifiedImageGenerator

async def test():
    print('Testing text_to_image...')
    async with UnifiedImageGenerator() as gen:
        result = await gen.text_to_image(
            prompt='a simple red apple on a white background, studio lighting',
            negative_prompt='blurry, watermark',
            output_path='/tmp/test_txt2img.png'
        )
        print(f'Result: {result}')
        
        if result.get('success'):
            import os
            size = os.path.getsize('/tmp/test_txt2img.png')
            print(f'✓ SUCCESS: Generated {size:,} byte image')
            assert size > 10000, f'Image too small ({size} bytes)'
        else:
            print(f'✗ FAILED: {result.get(\"error\")}')
            print('Check /tmp/txt2img_error.png for debug screenshot')

asyncio.run(test())
" 2>&1 | tee /tmp/txt2img_test.log
```

---

### STREAM 9: Test Image-to-Image End-to-End

```bash
python -c "
import asyncio
from image_backends import UnifiedImageGenerator

async def test():
    print('Testing image_to_image...')
    async with UnifiedImageGenerator() as gen:
        result = await gen.image_to_image(
            image_path='/tmp/test_scene.png',
            prompt='oil painting style, impressionist brushstrokes',
            strength=0.6,
            output_path='/tmp/test_img2img.png'
        )
        print(f'Result: {result}')
        
        if result.get('success'):
            import os
            size = os.path.getsize('/tmp/test_img2img.png')
            print(f'✓ SUCCESS: Generated {size:,} byte image')
        else:
            print(f'✗ FAILED: {result.get(\"error\")}')
            print('Check /tmp/img2img_error.png for debug screenshot')

asyncio.run(test())
" 2>&1 | tee /tmp/img2img_test.log
```

---

### STREAM 10: Test Inpainting End-to-End

```bash
python -c "
import asyncio
from image_backends import UnifiedImageGenerator

async def test():
    print('Testing inpaint...')
    async with UnifiedImageGenerator() as gen:
        result = await gen.inpaint(
            image_path='/tmp/test_scene.png',
            mask_path='/tmp/test_mask.png',
            prompt='a red balloon floating',
            output_path='/tmp/test_inpaint.png'
        )
        print(f'Result: {result}')
        
        if result.get('success'):
            import os
            size = os.path.getsize('/tmp/test_inpaint.png')
            print(f'✓ SUCCESS: Generated {size:,} byte image')
        else:
            print(f'✗ FAILED: {result.get(\"error\")}')
            print('Check /tmp/inpaint_error.png for debug screenshot')

asyncio.run(test())
" 2>&1 | tee /tmp/inpaint_test.log
```

---

### STREAM 11: Test Upscaling End-to-End

```bash
python -c "
import asyncio
from image_backends import UnifiedImageGenerator

async def test():
    print('Testing upscale...')
    async with UnifiedImageGenerator() as gen:
        result = await gen.upscale(
            image_path='/tmp/test_scene.png',
            scale=2.0,
            output_path='/tmp/test_upscale.png'
        )
        print(f'Result: {result}')
        
        if result.get('success'):
            import os
            size = os.path.getsize('/tmp/test_upscale.png')
            print(f'✓ SUCCESS: Generated {size:,} byte image')
        else:
            print(f'✗ FAILED: {result.get(\"error\")}')
            print('Check /tmp/upscale_error.png for debug screenshot')

asyncio.run(test())
" 2>&1 | tee /tmp/upscale_test.log
```

---

### STREAM 12: Test MCP Protocol

```bash
# Test initialize
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","clientInfo":{"name":"test"}}}' | python server.py | python -c "
import sys, json
r = json.loads(sys.stdin.readline())
assert 'result' in r and 'capabilities' in r['result'], f'Bad response: {r}'
print('✓ MCP initialize OK')
print(f'  Server: {r[\"result\"][\"serverInfo\"]}')"

# Test tools/list
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | python server.py | tail -1 | python -c "
import sys, json
r = json.loads(sys.stdin.readline())
tools = [t['name'] for t in r['result']['tools']]
print(f'✓ MCP tools/list OK')
print(f'  Tools: {tools}')
for t in ['text_to_image', 'image_to_image', 'inpaint_image', 'upscale_image']:
    assert t in tools, f'Missing {t}'"
```

---

## Validation Checklist (ALL MUST PASS)

```bash
# 1. Syntax
python -m py_compile server.py image_backends.py gradio_automation.py && echo "✓ 1/8 Syntax OK"

# 2. Imports
python -c "from server import TOOLS; from image_backends import UnifiedImageGenerator; print('✓ 2/8 Imports OK')"

# 3. Playwright
python -c "from playwright.async_api import async_playwright; print('✓ 3/8 Playwright OK')"

# 4. Browser launch
python -c "
import asyncio
from playwright.async_api import async_playwright
async def t():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        await b.close()
        print('✓ 4/8 Browser OK')
asyncio.run(t())"

# 5. MCP protocol
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python server.py | grep -q 'capabilities' && echo "✓ 5/8 MCP Protocol OK"

# 6. Tool count
python -c "from server import TOOLS; assert len(TOOLS) == 6, f'Expected 6 tools, got {len(TOOLS)}'; print('✓ 6/8 Tool count OK (6 tools)')"

# 7. Backend classes
python -c "
from image_backends import TextToImageBackend, ImageToImageBackend, InpaintingBackend, UpscaleBackend
print(f'  Text2Img spaces: {len(TextToImageBackend.SPACE_URLS)}')
print(f'  Img2Img spaces: {len(ImageToImageBackend.SPACE_URLS)}')
print(f'  Inpaint spaces: {len(InpaintingBackend.SPACE_URLS)}')
print(f'  Upscale spaces: {len(UpscaleBackend.SPACE_URLS)}')
print('✓ 7/8 Backend classes OK')"

# 8. HuggingFace reachable
python -c "
import asyncio
from playwright.async_api import async_playwright
async def t():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        pg = await b.new_page()
        await pg.goto('https://huggingface.co/spaces/black-forest-labs/FLUX.1-schnell', timeout=60000)
        await pg.wait_for_selector('.gradio-container', timeout=30000)
        await b.close()
        print('✓ 8/8 HuggingFace reachable')
asyncio.run(t())"
```

---

## Known Issues to Investigate

1. **Selectors are educated guesses** - Based on common Gradio patterns but need verification
2. **Some spaces use canvas drawing** - Inpainting might have a mask drawing tool instead of file upload
3. **Spaces can change UI** - HuggingFace spaces update frequently
4. **Rate limiting** - Some spaces queue requests during high traffic
5. **Download method varies** - Some use blob URLs, some data URLs, some download buttons

---

## Deliverables

1. **Working `gradio_automation.py`** with verified base selectors
2. **Working `image_backends.py`** with correct space-specific selectors for all 4 backends
3. **Working `server.py`** passing all MCP protocol tests
4. **All 8 validation checks passing**
5. **At least 2 successful generations** from different backends (e.g., text_to_image + img2img)
6. **Brief report** documenting selector changes and any spaces that needed fallbacks

---

## Tips

- Screenshot liberally with `await page.screenshot(path='/tmp/debug.png')`
- Check `/tmp/*_error.png` files when generation fails
- Use browser DevTools (non-headless mode) to find selectors: set `headless=False` in backend init
- If a primary space doesn't work, try URLs from the `SPACE_URLS` list
- Gradio elements often have predictable classes: `.gradio-textbox`, `.gradio-image`, `.gradio-button`
- Generation timeouts are set to 3 minutes - may need adjustment for slow spaces
