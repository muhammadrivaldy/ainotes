# Implementation Plan - Generic Memory System

## Goal
Refactor the current "specific memory" (notes) system to a "generic knowledge" system that seamlessly integrates two types of knowledge:
1.  **Chat Memories**: Direct text-to-text interactions, facts, and user preferences.
2.  **Document Knowledge**: Information extracted from uploaded files (PDFs), with the ability to reference back to the source file.

The system must support saving, retrieving, synthesizing, and managing both types of data in a unified "Second Brain".

## Tasks

### 1. Data Model & Storage Refactoring
- [ ] **Abstract Knowledge Storage**: 
    - Conceptually shift from "Notes" to "Knowledge Items".
    - Unified Vector Store: Both Chat Memories and Document Chunks reside in the same collection.
- [ ] **File Storage Structure**: 
    - Create `backend/uploads/` directory to persistently store original PDF files.
    - Files allow the user to download the original source later.
- [ ] **Enhance Metadata Schema**: 
    - Update ChromaDB insertion logic to include:
        - `source`: The origin of the info (e.g., "chat" for conversation, "specification_v1.pdf" for files).
        - `source_type`: Enum ["chat", "document"].
        - `source_path`: File path for documents (e.g., "uploads/specification_v1.pdf"), or null for chat.
        - `page`: Page number (for documents only).
        - `created_at`: Timestamp.

### 2. PDF Ingestion & Tools
- [ ] **Dependency Management**: Ensure `pypdf` or `langchain-community` document loaders are installed.
- [ ] **New Tool `add_document`**: 
    - Input: File path or UploadFile.
    - Process:
        1. Save file to `backend/uploads/`.
        2. Load PDF and extract text.
        3. Split text into semantic chunks (paragraphs).
        4. Generate tags for the document context.
        5. Save chunks to Vector Store with `source_type="document"` and page metadata.
    - Output: "Successfully imported [filename] and added [N] knowledge chunks."
- [ ] **Update `add_recall`**: 
    - Refactor to explicitly set `source_type="chat"` and `source="user"`.
    - Ensure it remains the default tool for conversational memories.
- [ ] **Update `query_recall`**: 
    - Return rich metadata in the search results.
    - Format output to cite sources (e.g., "Found in [spec.pdf] (Pg 3): ...").
    - Allow filtering by `source_type` (optional).
- [ ] **Rename/Refactor Retrieval Tools**: 
    - `get_all_notes` -> `get_all_knowledge`: List both chat memories and documents.
    - `get_tags`: Ensure tags from documents are included in the global tag list.

### 3. Agent Prompts & Fluency
- [ ] **Update `SYSTEM_PROMPT`**: 
    - **Persona**: Shift to "Knowledge Assistant" / "Second Brain".
    - **Reasoning**: Explicitly allow synthesizing information across sources (e.g., "Combine what I said about X with the PDF about Y").
    - **Citations**: Instruct the model to mention the source when answering from a document.
    - **Fluency**: Remove robotic "database" language; use natural conversational tone.
- [ ] **Improve `process_message`**: 
    - Ensure the graph flow allows for complex reasoning (not just retrieval -> regurgitation).

### 4. Codebase Cleanup
- [ ] **Refactor Terminology**: Replace "notes" with "memories" or "knowledge" in code comments and UI responses.
- [ ] **Verify Backward Compatibility**: 
    - Ensure existing "notes" (which lack new metadata) are treated as `source_type="chat"`.
    - Run migration or handle missing keys gracefully in code.

## Verification
- Test 1: Save a conversational memory ("My project deadline is Friday").
- Test 2: Upload a PDF and ingest it.
- Test 3: Ask a question that requires knowledge from the PDF.
- Test 4: Ask a question that combines chat memory + PDF knowledge.
- Test 5: Verify original PDF exists in `uploads/` and can be located.
