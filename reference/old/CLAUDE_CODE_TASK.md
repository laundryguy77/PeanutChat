# Claude Code Task: Verify, Test, and Complete the Video Generation MCP Server

## Executive Summary

This is an MCP (Model Context Protocol) server that enables AI chat agents to generate videos using free Hugging Face Spaces. It supports:
- **Text-to-Video**: Generate video from text descriptions (e.g., "a cat playing piano")
- **Image-to-Video**: Animate a still image into a video clip

Since these services have no official API, the system uses **Playwright browser automation** to control Gradio-based web interfaces.

---

## Project Files (in project root)

| File | Purpose | Size |
|------|---------|------|
| `server.py` | MCP server - JSON-RPC protocol over stdio, defines tools | ~6KB |
| `video_backends.py` | Video generation classes for different HF Spaces | ~12KB |
| `gradio_automation.py` | Base class for automating Gradio UIs | ~8KB |
| `requirements.txt` | Dependencies (just `playwright>=1.40.0`) | <1KB |
| `README.md` | Documentation | ~4KB |

---

## Business Purpose

Chat agents (Claude, etc.) need the ability to generate videos on demand. This MCP server exposes four tools:
1. `text_to_video` - Generate video from text prompt
2. `image_to_video` - Animate an image into video  
3. `generate_video_batch` - Batch generation
4. `list_supported_spaces` - Show available backends

---

## Target Hugging Face Spaces

### Text-to-Video
```
Primary:   https://huggingface.co/spaces/Lightricks/LTX-Video-Distilled
Fallback:  https://huggingface.co/spaces/Wan-AI/Wan2.1-T2V-1.3B
Fallback:  https://huggingface.co/spaces/multimodalart/LTX-Video
```

### Image-to-Video
```
Primary:   https://huggingface.co/spaces/Heartsync/NSFW-Uncensored-video
Fallback:  https://huggingface.co/spaces/Justforailolomg/NSFW-Uncensored-video-duplicate
```

---

## Your Tasks - Use Subagents for Parallel Execution

### STREAM 1: Environment Setup & Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Verify installation
python -c "from playwright.async_api import async_playwright; print('✓ Playwright installed')"
playwright --version
```

**Validation checkpoint:**
```bash
python -m py_compile server.py video_backends.py gradio_automation.py && echo "✓ All files have valid syntax"
```

---

### STREAM 2: Inspect Text-to-Video Space (CRITICAL)

Visit `https://huggingface.co/spaces/Lightricks/LTX-Video-Distilled` and document:

1. **Exact selector for prompt input field**
   - Is it `textarea`, `input[type="text"]`, or something else?
   - What's its class, id, placeholder text, or aria-label?

2. **Exact selector for generate/submit button**
   - Button text ("Generate", "Create", "Run", "Submit")?
   - CSS class?

3. **Exact selector for output video element**
   - How is the video displayed? `<video>`, download link, or something else?
   - How to extract the video file?

4. **Any configuration options**
   - Duration selector?
   - Resolution options?
   - Negative prompt field?

5. **Loading/progress indicators**
   - What CSS classes indicate generation in progress?
   - What indicates completion?

**Deliverable:** Update `HuggingFaceTextToVideo` class in `video_backends.py` with correct selectors.

---

### STREAM 3: Inspect Image-to-Video Space (CRITICAL)

Visit `https://huggingface.co/spaces/Heartsync/NSFW-Uncensored-video` and document:

1. **Image upload component**
   - File input selector
   - Drag-drop zone selector
   - How to verify upload completed

2. **Prompt/motion input field** (if exists)
   - Selector for motion description

3. **Generate button**
   - Exact selector

4. **Output video**
   - How to locate generated video
   - How to download it

5. **Any popup dialogs**
   - Cookie consent?
   - Age verification?
   - NSFW warning?

**Deliverable:** Update `HuggingFaceImageToVideo` class in `video_backends.py` with correct selectors.

---

### STREAM 4: Test Gradio Base Automation

```bash
# Test that base Gradio automation can load a space
python -c "
import asyncio
from gradio_automation import GradioAutomation

async def test():
    auto = GradioAutomation('https://huggingface.co/spaces/Lightricks/LTX-Video-Distilled')
    await auto.start()
    context = await auto.new_context()
    page = await context.new_page()
    
    print('Loading space...')
    await page.goto(auto.space_url, wait_until='networkidle')
    await auto.wait_for_gradio_load(page)
    
    # Take screenshot for visual verification
    await page.screenshot(path='/tmp/gradio_test.png')
    print('✓ Screenshot saved to /tmp/gradio_test.png')
    
    # List all visible textareas and buttons
    textareas = await page.query_selector_all('textarea')
    buttons = await page.query_selector_all('button')
    print(f'Found {len(textareas)} textareas, {len(buttons)} buttons')
    
    for i, btn in enumerate(buttons[:5]):
        text = await btn.inner_text()
        print(f'  Button {i}: \"{text}\"')
    
    await context.close()
    await auto.close()
    print('✓ Base automation test passed')

asyncio.run(test())
"
```

---

### STREAM 5: Test Text-to-Video Generation (End-to-End)

```bash
# Test text-to-video with a simple prompt
python -c "
import asyncio
from video_backends import VideoGenerator

async def test():
    print('Starting text-to-video test...')
    async with VideoGenerator() as gen:
        result = await gen.text_to_video(
            prompt='a red ball bouncing on a white floor',
            output_path='/tmp/test_t2v.mp4'
        )
        print(f'Result: {result}')
        
        if result.get('success'):
            import os
            size = os.path.getsize('/tmp/test_t2v.mp4')
            print(f'✓ Video generated: {size:,} bytes')
            assert size > 10000, f'Video too small ({size} bytes)'
        else:
            print(f'✗ FAILED: {result.get(\"error\")}')
            # Check for debug screenshot
            if os.path.exists('/tmp/video_gen_error.png'):
                print('  Debug screenshot at /tmp/video_gen_error.png')

asyncio.run(test())
"
```

**Expected output:** A valid MP4 file > 10KB at `/tmp/test_t2v.mp4`

---

### STREAM 6: Test Image-to-Video Generation (End-to-End)

First, create a test image:
```bash
# Create a simple test image using Python
python -c "
from PIL import Image
img = Image.new('RGB', (512, 512), color='blue')
img.save('/tmp/test_image.png')
print('✓ Test image created at /tmp/test_image.png')
" 2>/dev/null || python -c "
# Fallback: create with pure Python (no PIL)
import struct
import zlib

def create_png(width, height, color, filename):
    def png_chunk(chunk_type, data):
        chunk_len = struct.pack('>I', len(data))
        chunk_crc = struct.pack('>I', zlib.crc32(chunk_type + data) & 0xffffffff)
        return chunk_len + chunk_type + data + chunk_crc

    header = b'\\x89PNG\\r\\n\\x1a\\n'
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    
    raw_data = b''
    for y in range(height):
        raw_data += b'\\x00' + bytes(color) * width
    
    compressed = zlib.compress(raw_data)
    
    with open(filename, 'wb') as f:
        f.write(header)
        f.write(png_chunk(b'IHDR', ihdr))
        f.write(png_chunk(b'IDAT', compressed))
        f.write(png_chunk(b'IEND', b''))

create_png(512, 512, (0, 0, 255), '/tmp/test_image.png')
print('✓ Test image created at /tmp/test_image.png')
"
```

Then test image-to-video:
```bash
python -c "
import asyncio
from video_backends import VideoGenerator

async def test():
    print('Starting image-to-video test...')
    async with VideoGenerator() as gen:
        result = await gen.image_to_video(
            image_path='/tmp/test_image.png',
            prompt='slow zoom in',
            output_path='/tmp/test_i2v.mp4'
        )
        print(f'Result: {result}')
        
        if result.get('success'):
            import os
            size = os.path.getsize('/tmp/test_i2v.mp4')
            print(f'✓ Video generated: {size:,} bytes')
            assert size > 10000, f'Video too small ({size} bytes)'
        else:
            print(f'✗ FAILED: {result.get(\"error\")}')

asyncio.run(test())
"
```

---

### STREAM 7: Test MCP Protocol Compliance

```bash
# Test MCP initialization
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","clientInfo":{"name":"test"}}}' | python server.py | python -c "
import sys, json
response = json.loads(sys.stdin.readline())
assert 'result' in response, f'No result in response: {response}'
assert 'capabilities' in response['result'], 'Missing capabilities'
assert 'serverInfo' in response['result'], 'Missing serverInfo'
print('✓ MCP initialize OK')
print(f'  Server: {response[\"result\"][\"serverInfo\"]}')"

# Test tools/list
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | python server.py | tail -1 | python -c "
import sys, json
response = json.loads(sys.stdin.readline())
assert 'result' in response, f'No result: {response}'
tools = response['result']['tools']
tool_names = [t['name'] for t in tools]
print(f'✓ MCP tools/list OK')
print(f'  Tools: {tool_names}')
assert 'text_to_video' in tool_names, 'Missing text_to_video'
assert 'image_to_video' in tool_names, 'Missing image_to_video'"
```

---

### STREAM 8: Full MCP Tool Call Test

```bash
# Test calling text_to_video through MCP (timeout 5 minutes)
timeout 300 bash -c 'echo "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{}}
{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/call\",\"params\":{\"name\":\"text_to_video\",\"arguments\":{\"prompt\":\"a simple animation of a circle\",\"save_path\":\"/tmp/mcp_test_video.mp4\"}}}" | python server.py'

# Verify output
ls -la /tmp/mcp_test_video.mp4 && file /tmp/mcp_test_video.mp4
```

---

## Validation Checklist (ALL MUST PASS)

Run each of these and ensure they pass:

```bash
# 1. Syntax check
python -m py_compile server.py video_backends.py gradio_automation.py
echo "✓ 1/6 Syntax OK"

# 2. Import check  
python -c "from server import TOOLS; from video_backends import VideoGenerator; from gradio_automation import GradioAutomation; print('✓ 2/6 Imports OK')"

# 3. Playwright check
python -c "from playwright.async_api import async_playwright; print('✓ 3/6 Playwright OK')"

# 4. MCP protocol check
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python server.py | grep -q '"capabilities"' && echo "✓ 4/6 MCP Protocol OK"

# 5. Browser can launch
python -c "
import asyncio
from playwright.async_api import async_playwright
async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        await browser.close()
        print('✓ 5/6 Browser launch OK')
asyncio.run(test())
"

# 6. Can load Hugging Face Space
python -c "
import asyncio
from playwright.async_api import async_playwright
async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://huggingface.co/spaces/Lightricks/LTX-Video-Distilled', timeout=60000)
        await page.wait_for_selector('.gradio-container', timeout=30000)
        await browser.close()
        print('✓ 6/6 HuggingFace Space loads OK')
asyncio.run(test())
"
```

---

## Known Issues That Need Investigation

1. **Selectors are generic guesses** - The CSS selectors in `gradio_automation.py` and `video_backends.py` are based on common Gradio patterns but need verification against actual page structure

2. **Space availability** - Hugging Face Spaces can go offline, get rate-limited, or change their UI

3. **Video download method** - Different spaces serve videos differently (blob URL, data URL, direct link, download button)

4. **Popup handling** - Cookie consent, age verification, or NSFW warnings may block automation

5. **Timeouts** - Video generation can take 1-5+ minutes; adjust timeouts if needed

---

## Deliverables

1. **Working `gradio_automation.py`** with verified base selectors
2. **Working `video_backends.py`** with correct space-specific selectors
3. **Working `server.py`** that passes all MCP protocol tests
4. **All 6 validation checks passing**
5. **At least one successful video generation** (either text-to-video or image-to-video)
6. **Brief report** documenting any selectors or logic that needed changing

---

## Tips

- Use `page.screenshot()` liberally for debugging
- Check `/tmp/video_gen_error.png` when generation fails
- Gradio elements often have classes like `.gradio-textbox`, `.gradio-button`, `.gradio-video`
- Use browser DevTools to find exact selectors
- If one space doesn't work, try the fallback URLs listed in `video_backends.py`
- Video generation is slow - be patient and set appropriate timeouts
