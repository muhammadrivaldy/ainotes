# AI Notes - Project Requirements

## 1. Project Overview

"AI Notes" is a personal knowledge base application designed to function as a "Second Brain." It adopts a conversational AI interface (similar to ChatGPT or Gemini) where users can store and retrieve information naturally. The goal is to reduce cognitive load by offloading memory tasks to the system.

- **Platform:** Web-based (Single Page Application)
- **Tech Stack:** ReactJS (Vite), Tailwind CSS
- **Backend:** Decoupled (API-based, handled in a separate project)

## 2. Core Features & Functional Requirements

### 2.1 Interaction Model

- **"Life Stream" Concept:** The interface is a continuous, infinite-scroll timeline of notes and interactions, rather than disjointed chat sessions.
- **Implicit Storage & Retrieval:** The user does not need to tag or categorize notes manually. The intent to save or find information is inferred from natural language (handled by the backend).
- **Conversational Editing:** Users modify stored knowledge by simply telling the AI to "update the last note" or "change that fact" (Edit-by-prompt), rather than a GUI edit button.

### 2.2 Chat Interface

- **Rich Text Support (Markdown):**
  - Messages support Bold, Italics, Lists, and Code Blocks.
  - **Syntax Highlighting:** Code snippets are properly formatted.
  - **Smart Spacing:** Single "Enter" creates a new line. Multiple "Enters" create visible vertical gaps.
- **Input Area:**
  - Auto-expanding text box (starts at 1 line, grows with content).
  - **Alignment:** Buttons (Delete, Send) remain vertically centered relative to the input box regardless of height.
  - **Focus State:** No default browser outline/border on focus.
- **Clear Conversation:** A specific button (trash icon) to visually clear the current view and start a fresh topic, without deleting the actual history from the backend.

### 2.3 Layout & Navigation

- **Sidebar:**
  - **Content:** Contains navigation to Settings, Profile, and Theme Toggle.
  - **Collapsible:** The sidebar can be completely hidden to focus on the notes.
  - **Toggle Animation:** Smooth transition when opening/closing.
- **Theme:**
  - **Dark/Light Mode:** Full support for both themes.
  - **Default:** Light mode is the default for new users.

## 3. Technical Requirements

### 3.1 Frontend Architecture

- **Framework:** React 19+ (via Vite)
- **Styling:** Tailwind CSS v4
- **Icons:** Lucide React
- **Markdown Processing:** `react-markdown`, `remark-gfm` (for GitHub flavor), `remark-breaks` (for hard line breaks).

### 3.2 Component Structure

- `AppLayout`: Manages the global layout and Sidebar toggle state.
- `Sidebar`: Handles navigation links and theme switching.
- `StreamFeed`: The visual container for the chat history.
- `MessageBubble`: Renders individual messages with Markdown processing.
- `InputArea`: Handles user input, auto-resizing, and submission events.

### 3.3 State Management

- **Theme Context:** Persists user preference (Light/Dark) in LocalStorage.
- **Local State:** React `useState` handles the current conversation view, sidebar visibility, and input content.

## 4. Future Considerations (Backend)

- The frontend mocks the AI response for now (0.6s delay).
- Future integration will connect to an API endpoint to send user prompts and receive AI-generated storage confirmations or retrieved answers.
