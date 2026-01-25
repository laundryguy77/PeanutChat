# PeanutChat Memory & Knowledge Base - UI Testing Findings

**Test User:** testuser_memory2_1769372258625
**Test Date:** 2026-01-25T20:23:09.024Z
**App URL:** http://localhost:8080

---

## Setup

- Successfully created test user: testuser_memory2_1769372258625

## Settings

- Settings panel opens via gear icon button (#settings-btn)

## Memory

- Memory count element (#memory-count): displays "0"
- Categories count element (#memory-categories): displays "0"
- Memory list is expandable via <details> with "View all memories" summary

## Memory Stats Structure

```
[
  {
    "id": "memory-count",
    "text": "0",
    "classes": "text-2xl font-bold text-primary"
  },
  {
    "id": "memory-categories",
    "text": "0",
    "classes": "text-2xl font-bold text-primary"
  }
]
```


## Memory Cards

- Empty state shows: "No memories yet. The AI will learn about you over time."

## Memory Card Structure (from source)

```
Expected card components:
- Container: .flex.items-start.gap-2.p-2.bg-background-dark/50.rounded-lg.group
- Content: p.text-sm.text-gray-300.break-words (memory content)
- Metadata: p.text-xs.text-gray-500 (source + date)
- Source types: "You asked" (explicit) or "Learned" (inferred)
- Importance indicator: text-yellow-500 "Important" for importance >= 8
- Delete button: opacity-0 group-hover:opacity-100, trash icon
```


## Memory Category Icons

```
Category icons (material-symbols-outlined):
- personal: "person"
- preference: "favorite"
- topic: "topic"
- instruction: "rule"
- general: "memory"
```


## Memory Operations

- Clear all button exists with delete_forever icon and red text styling

## Clear All Button HTML

```
<button onclick="memoryManager.clearAllMemories()" class="flex items-center gap-2 text-xs text-red-400 hover:text-red-300 transition-colors">
                        <span class="material-symbols-outlined text-sm">delete_forever</span>
                        Clear all memories
                    </button>
```


## Memory Confirmation Dialogs

```
Confirmation dialogs (window.confirm):
- Delete single: "Delete this memory?"
- Clear all: "Clear ALL memories? This cannot be undone."
```


## KB Upload Area

```
{
  "classes": "border-2 border-dashed border-gray-700 rounded-xl p-6 text-center hover:border-primary/50 transition-colors cursor-pointer mb-4",
  "innerHTML": "<span class=\"material-symbols-outlined text-4xl text-gray-500 mb-2\">upload_file</span>\n                        <p class=\"text-sm text-gray-400\">Drop files here or click to upload</p>\n                        <p class=\"text-xs text-gray-500 mt-1\">Max 150MB per file</p>\n                        <input type=\"file\" id=\"kb-file-input\" class=\"hidden\" multiple=\"\" accept=\".pdf,.txt,.md,.py,.js,.ts,.json,.html,.css,.java,.go,.rs,.c,.cpp,.h,.yaml,.yml,.toml,.csv,.xml,.log\" style=\"\">",
  "computedBorder": "2px dashed rgb(55, 65, 81)",
  "computedBackground": "rgba(0, 0, 0, 0) none repeat scroll 0% 0% / auto padding-box border-box"
}
```


## KB Drag-Drop Styling

```
Drag-drop zone (#kb-upload-area):
- Default: border-2 border-dashed border-gray-700 rounded-xl p-6 text-center hover:border-primary/50
- On dragover: adds border-primary bg-primary/10
- On dragleave/drop: removes those classes
- Contains upload_file icon (text-4xl text-gray-500)
- Text: "Drop files here or click to upload"
- Subtext: "Max 150MB per file"
```


## KB Stats

- Document count: 0, Chunk count: 0

## KB Upload

- File upload successful - test_kb.txt appears in document list

## KB File Type Icons

```
File type icons (material-symbols-outlined):
- pdf: "picture_as_pdf"
- text: "description"
- code: "code"
- default: "description"
```


## KB File Type Mappings (Backend)

```
File extension to type:
- pdf: 'pdf'
- txt, md, markdown, csv, log, ini, cfg: 'text'
- py, js, ts, jsx, tsx, java, go, rs, c, cpp, h, rb, php, sh, html, css, json, xml, yaml, yml, toml: 'code'
- default: 'text'
```


## KB Upload Progress

- Progress element exists, hidden: true

## KB Delete Confirmation

- Confirmation dialog: "Delete this document from the knowledge base?"

## KB Operations

- Delete button appears on hover (.kb-delete-btn) with trash icon

## KB Integration

- No response received within timeout (may need longer)

## Memory API Endpoints

```

- GET /api/memory - List all memories with stats
- POST /api/memory - Add memory (content, category, importance)
- DELETE /api/memory/{memory_id} - Delete specific memory
- DELETE /api/memory - Clear all memories
- GET /api/memory/stats - Get memory statistics
```


## Knowledge Base API Endpoints

```

- POST /api/knowledge/upload - Upload document (multipart form)
- POST /api/knowledge/search - Search KB (query, top_k, threshold)
- GET /api/knowledge/documents - List all documents
- DELETE /api/knowledge/documents/{document_id} - Delete document
- GET /api/knowledge/stats - Get KB statistics
```


## Screenshots Captured

- `01_landing_page.png`
- `02_create_account_tab.png`
- `02_registration_form.png`
- `03_after_login.png`
- `04_settings_panel_open.png`
- `05_memory_section_stats.png`
- `06_memory_list_expanded.png`
- `07_clear_all_memories_button.png`
- `08_knowledge_base_section.png`
- `09_kb_upload_area.png`
- `10_kb_stats.png`
- `11_after_file_upload.png`
- `12_kb_document_list.png`
- `13_kb_delete_button_visible.png`
- `14_kb_document_hover.png`
- `15_settings_closed.png`
- `16_message_with_kb_query.png`
- `17_kb_query_response.png`
- `18_final_state.png`
- `error_state.png`
