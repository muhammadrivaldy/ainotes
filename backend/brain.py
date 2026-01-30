# AI Notes API
# Copyright (C) 2026 Rivaldy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Literal, TypedDict, Annotated
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
import constants

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database directory - now in database/ folder
DATABASE_DIR = os.path.join(os.path.dirname(__file__), "database")
CHROMA_DIR = os.path.join(DATABASE_DIR, "chroma")
UPLOADS_DIR = os.path.join(DATABASE_DIR, "uploads")
os.makedirs(CHROMA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Define Graph State
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

class SecondBrain:
    # System prompt is imported from constants.py as SYSTEM_PROMPT
    
    def __init__(self, user_id: int):
        self.user_id = user_id

        # Using OpenRouter for Embeddings
        self.embeddings = OpenAIEmbeddings(
            model=os.getenv("OPENROUTER_EMBEDDING_MODEL", "text-embedding-3-small"),
            openai_api_base=os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1"),
            openai_api_key=os.getenv("OPENROUTER_API_KEY")
        )

        # Single ChromaDB collection for all users
        # Data isolation is handled via metadata filtering
        self.vector_store = Chroma(
            collection_name="second_brain",
            embedding_function=self.embeddings,
            persist_directory=CHROMA_DIR
        )

        # Using OpenRouter for Chat
        self.llm = ChatOpenAI(
            model=os.getenv("OPENROUTER_AI_MODEL", "openai/gpt-4o-mini"),
            temperature=0,
            openai_api_base=os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1"),
            openai_api_key=os.getenv("OPENROUTER_API_KEY")
        )

        # Define Tools - capture vector_store and user_id for data isolation
        vector_store = self.vector_store
        user_id = self.user_id
        llm = self.llm

        def generate_tags(content: str, max_tags: int = 3) -> list:
            """Generate 1-3 semantic tags for content using LLM."""
            prompt = constants.TAG_GENERATION_PROMPT.format(content=content)

            try:
                response = llm.invoke(prompt)
                tags = [tag.strip().lower() for tag in response.content.split(',')]
                return [tag for tag in tags if tag][:max_tags]
            except Exception as e:
                print(f"Tag generation failed: {e}")
                return ["note"]  # Fallback tag

        @tool
        def provide_help() -> str:
            """
            Provide comprehensive help about the AI's capabilities when user is confused or asks for help.
            Use this IMMEDIATELY when detecting:
            - Confusion signals: "what can you do?", "help", "I don't understand", "confused"
            - Help requests: "how does this work?", "explain", "what is this?"
            - Vague intents: "how do I start?", "what now?"
            """
            # Log confusion detection event
            logger.info(f"Help provided to user {user_id} - confusion detected")
            
            # Check if user has any data stored
            try:
                results = vector_store.get(where={"user_id": user_id}, limit=1)
                has_data = bool(results and results.get('metadatas'))
            except:
                has_data = False

            help_message = constants.HELP_MESSAGE_BASE
            
            if has_data:
                return constants.HELP_RESPONSE_WITH_DATA
            else:
                return constants.HELP_RESPONSE_NO_DATA

        @tool
        def add_recall(content: str) -> str:
            """
            Useful for storing new information, facts, notes, or memories into the second brain.
            Use this when the user makes a statement, shares a fact, or asks to save something.
            """
            # Generate tags
            tags = generate_tags(content)

            # Add metadata with full attribution schema
            vector_store.add_texts(
                texts=[content],
                metadatas=[{
                    "user_id": user_id,
                    "tags": ",".join(tags),
                    "source_type": "chat",
                    "source": "user",
                    "source_path": "",
                    "page": "",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }]
            )
            return constants.ADD_RECALL_SUCCESS.format(tags=', '.join(tags))

        @tool
        def add_document(file_path: str) -> str:
            """
            Process an uploaded PDF file into knowledge chunks and store them in the knowledge base.
            Use this when a PDF file has been uploaded and needs to be ingested.
            The file_path should be the full path to the uploaded PDF file.
            """
            try:
                path = Path(file_path)
                if not path.exists():
                    return constants.ADD_DOCUMENT_ERROR_NOT_FOUND.format(path=file_path)
                if path.suffix.lower() != ".pdf":
                    return constants.ADD_DOCUMENT_ERROR_INVALID_TYPE.format(suffix=path.suffix)

                filename = path.name

                # Load PDF pages
                loader = PyPDFLoader(file_path)
                pages = loader.load()

                if not pages:
                    return constants.ADD_DOCUMENT_ERROR_NO_CONTENT.format(filename=filename)

                # Generate document-level tags from filename + first page content
                first_page_preview = pages[0].page_content[:500] if pages else ""
                tag_input = f"Document: {path.stem}. Content preview: {first_page_preview}"
                doc_tags = generate_tags(tag_input)

                # Collect all chunks across all pages first
                all_texts = []
                all_metadatas = []
                created_at = datetime.now(timezone.utc).isoformat()

                for page_doc in pages:
                    page_num = page_doc.metadata.get("page", 0) + 1  # 1-indexed
                    content = page_doc.page_content.strip()
                    if not content:
                        continue

                    # Split long pages into ~1000 char chunks at paragraph boundaries
                    chunks = _split_into_chunks(content, chunk_size=1000)

                    for chunk in chunks:
                        if not chunk.strip():
                            continue
                        all_texts.append(chunk)
                        all_metadatas.append({
                            "user_id": user_id,
                            "tags": ",".join(doc_tags),
                            "source_type": "document",
                            "source": filename,
                            "source_path": file_path,
                            "page": str(page_num),
                            "created_at": created_at
                        })

                # Single batched call — embedding model processes all chunks together
                if all_texts:
                    vector_store.add_texts(texts=all_texts, metadatas=all_metadatas)

                return constants.ADD_DOCUMENT_SUCCESS.format(filename=filename, count=len(all_texts), tags=', '.join(doc_tags))

            except Exception as e:
                logger.error(f"Error processing document: {e}")
                return constants.ADD_DOCUMENT_ERROR_GENERIC.format(error=str(e))

        def _split_into_chunks(text: str, chunk_size: int = 1000) -> list:
            """Split text into chunks at paragraph boundaries."""
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            if not paragraphs:
                paragraphs = [p.strip() for p in text.split('\n') if p.strip()]

            chunks = []
            current_chunk = ""

            for paragraph in paragraphs:
                if len(current_chunk) + len(paragraph) + 2 <= chunk_size:
                    current_chunk += ("\n\n" if current_chunk else "") + paragraph
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    # If a single paragraph exceeds chunk_size, split it
                    if len(paragraph) > chunk_size:
                        words = paragraph.split()
                        current_chunk = ""
                        for word in words:
                            # Handle words that exceed chunk_size
                            if len(word) > chunk_size:
                                # Log warning about data truncation
                                logger.warning(f"Word exceeds chunk_size ({len(word)} > {chunk_size}), truncating: {word[:50]}...")
                                word = word[:chunk_size]
                            
                            if len(current_chunk) + len(word) + 1 <= chunk_size:
                                current_chunk += (" " if current_chunk else "") + word
                            else:
                                if current_chunk:
                                    chunks.append(current_chunk)
                                current_chunk = word
                    else:
                        current_chunk = paragraph

            if current_chunk:
                chunks.append(current_chunk)

            return chunks if chunks else [text]

        @tool
        def query_recall(query: str) -> str:
            """
            Useful for retrieving information from the second brain.
            Use this when the user asks a personal question or tries to recall a fact.

            IMPORTANT: Always call this tool when the user asks a question. Do not answer from conversation history.
            The database is the source of truth, not your memory of previous responses.
            """
            # Filter by user_id to only retrieve current user's data
            # Increase k to 10 for broader search
            results = vector_store.similarity_search_with_score(
                query,
                k=10,
                filter={"user_id": user_id}
            )

            if not results:
                # Get available tags to help user
                try:
                    all_results = vector_store.get(where={"user_id": user_id})
                    if all_results and all_results.get('metadatas'):
                        tags = set()
                        for metadata in all_results['metadatas']:
                            tags_str = metadata.get('tags', '')
                            if tags_str:
                                tags.update(tag.strip() for tag in tags_str.split(',') if tag.strip())
                        if tags:
                            tags_list = sorted(list(tags))
                            return constants.QUERY_RECALL_NO_EXACT_TOPICS.format(topics=','.join(tags_list))
                except Exception as e:
                    print(f"Error getting topics: {e}")

                return constants.QUERY_RECALL_NO_DATA

            def format_result_with_source(doc) -> str:
                """Format a document result with source citation if applicable."""
                content = doc.page_content
                metadata = doc.metadata
                source_type = metadata.get("source_type", "")
                if source_type == "document":
                    source = metadata.get("source", "unknown")
                    page = metadata.get("page", "?")
                    return f"{content}\n\n[Source: {source}, Page {page}]"
                return content

            # Separate high-confidence vs related results
            # Lower distance = more similar (distance ranges from 0 to 2)
            high_confidence = []
            related = []

            for doc, distance in results:
                if distance < 0.8:  # High confidence match
                    high_confidence.append(format_result_with_source(doc))
                elif distance < 1.5:  # Related information
                    related.append(format_result_with_source(doc))

            if high_confidence:
                response = "\n\n".join(high_confidence)
                if related:
                    response += f"\n\n[RELATED_INFO]\n" + "\n\n".join(related[:3])
                return response
            elif related:
                # Only related info, no exact matches
                return "[RELATED_INFO]\n" + "\n\n".join(related[:5])
            else:
                # Results exist but too distant
                return constants.QUERY_RECALL_DISTANT

        @tool
        def delete_recall(content: str) -> str:
            """
            Delete information from the second brain by describing what to remove.
            Use this when the user wants to delete, remove, or forget previously stored information.
            """
            # Find the most similar document in current user's data only
            results = vector_store.similarity_search(
                content,
                k=1,
                filter={"user_id": user_id}
            )

            if not results:
                return constants.DELETE_RECALL_NO_MATCH

            doc = results[0]
            # Delete by document ID
            vector_store.delete(ids=[doc.id])

            preview = doc.page_content[:100]
            return constants.DELETE_RECALL_SUCCESS.format(preview=preview)

        def is_similar_tag(tag1: str, tag2: str, threshold: float = 0.85) -> bool:
            """Check if two tags are similar using simple string similarity."""
            from difflib import SequenceMatcher
            return SequenceMatcher(None, tag1.lower(), tag2.lower()).ratio() >= threshold

        @tool
        def get_tags() -> str:
            """
            Retrieve all tags/categories with document counts for the user's stored information.
            Automatically detects and fixes similar/misspelled tags.

            Use this tool ONLY when the user explicitly asks about tags/categories/topics:
            - "Show my tags", "What tags do I have?", "List all categories"
            - "What topics are there?", "Show categories"
            - Must contain the words: "tag", "category", "categories", "topic", "topics"

            IMPORTANT: Always call this tool when the user explicitly asks about tags.
            Do not list tags from memory. The database is the source of truth, not conversation history.
            """
            try:
                # Get all documents for this user
                results = vector_store.get(where={"user_id": user_id})

                if not results or not results.get('metadatas'):
                    return constants.GET_TAGS_NO_TAGS

                # First pass: collect all tags and their frequencies
                tag_counts = {}
                for metadata in results['metadatas']:
                    tags_str = metadata.get('tags', '')
                    if tags_str:
                        for tag in tags_str.split(','):
                            tag = tag.strip()
                            if tag:
                                tag_counts[tag] = tag_counts.get(tag, 0) + 1

                if not tag_counts:
                    return constants.GET_TAGS_NO_TAGS

                # Auto-fix: Find and merge similar tags
                fixed_tags = {}
                tags_to_merge = []
                processed_tags = set()

                for tag1 in tag_counts:
                    if tag1 in processed_tags:
                        continue

                    similar_group = [tag1]
                    for tag2 in tag_counts:
                        if tag1 != tag2 and tag2 not in processed_tags:
                            if is_similar_tag(tag1, tag2, threshold=0.85):
                                similar_group.append(tag2)

                    if len(similar_group) > 1:
                        # Choose the most common tag or the correctly spelled one
                        # Prefer longer, properly spelled tags (with more vowels typically)
                        canonical_tag = max(similar_group, key=lambda t: (tag_counts[t], len(t)))

                        # Merge all similar tags to canonical
                        for tag in similar_group:
                            if tag != canonical_tag:
                                tags_to_merge.append((tag, canonical_tag))
                            processed_tags.add(tag)
                    else:
                        processed_tags.add(tag1)

                # Apply fixes if needed
                fixes_applied = []
                if tags_to_merge:
                    for i, metadata in enumerate(results['metadatas']):
                        tags_str = metadata.get('tags', '')
                        tags_list = [t.strip() for t in tags_str.split(',') if t.strip()]

                        updated = False
                        new_tags = []
                        for tag in tags_list:
                            # Check if this tag needs to be fixed
                            replacement = next((to_tag for from_tag, to_tag in tags_to_merge if from_tag == tag), None)
                            if replacement:
                                new_tags.append(replacement)
                                updated = True
                            else:
                                new_tags.append(tag)

                        if updated:
                            # Remove duplicates while preserving order
                            new_tags = list(dict.fromkeys(new_tags))
                            doc_id = results['ids'][i]
                            vector_store._collection.update(
                                ids=[doc_id],
                                metadatas=[{
                                    "user_id": user_id,
                                    "tags": ','.join(new_tags)
                                }]
                            )

                    # Record fixes
                    for from_tag, to_tag in tags_to_merge:
                        count = tag_counts[from_tag]
                        fixes_applied.append(f"'{from_tag}' → '{to_tag}' ({count} note{'s' if count > 1 else ''})")

                # Recount after fixes
                results = vector_store.get(where={"user_id": user_id})
                tag_counts = {}
                for metadata in results['metadatas']:
                    tags_str = metadata.get('tags', '')
                    if tags_str:
                        for tag in tags_str.split(','):
                            tag = tag.strip()
                            if tag:
                                tag_counts[tag] = tag_counts.get(tag, 0) + 1

                # Format output
                sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
                tag_list = "\n".join([f"• {tag}: {count} note{'s' if count > 1 else ''}" for tag, count in sorted_tags])

                response = constants.GET_TAGS_RESPONSE_TEMPLATE.format(tag_list=tag_list)

                if fixes_applied:
                    fixes_report = "\n".join([f"  • {fix}" for fix in fixes_applied])
                    response += constants.GET_TAGS_AUTOFIX_TEMPLATE.format(fixes=fixes_report)

                return response

            except Exception as e:
                print(f"Error getting tags: {e}")
                import traceback
                traceback.print_exc()
                return constants.GET_TAGS_ERROR

        @tool
        def get_all_knowledge() -> str:
            """
            Retrieve ALL stored information for the user without filtering, grouped by source type.
            Use this when the user asks broad questions about what they have stored:
            - "What knowledge do you have?", "What do you know?", "Show me everything"
            - "What information do I have?", "List all my notes", "Show all stored info"

            IMPORTANT: This retrieves everything, not filtered by tags or semantic search.
            Results are grouped into Chat Memories and Documents sections.
            """
            try:
                # Get all documents for this user (no limit to retrieve everything)
                results = vector_store.get(
                    where={"user_id": user_id}
                )

                if not results or not results.get('documents'):
                    return constants.GET_ALL_KNOWLEDGE_EMPTY

                documents = results['documents']
                metadatas = results.get('metadatas', [{}] * len(documents))

                if len(documents) == 0:
                    return constants.GET_ALL_KNOWLEDGE_EMPTY

                # Group by source type
                chat_memories = []
                doc_chunks = {}  # filename -> {pages, chunks}

                for i, doc in enumerate(documents):
                    metadata = metadatas[i] if i < len(metadatas) else {}
                    source_type = metadata.get("source_type", "chat")

                    if source_type == "document":
                        filename = metadata.get("source", "unknown")
                        page = metadata.get("page", "?")
                        if filename not in doc_chunks:
                            doc_chunks[filename] = {"pages": set(), "count": 0}
                        doc_chunks[filename]["pages"].add(page)
                        doc_chunks[filename]["count"] += 1
                    else:
                        chat_memories.append(doc)

                # Format output
                sections = []

                if chat_memories:
                    formatted = "\n\n---\n\n".join(chat_memories)
                    sections.append(f"### Chat Memories ({len(chat_memories)})\n\n{formatted}")

                if doc_chunks:
                    doc_summaries = []
                    for filename, info in sorted(doc_chunks.items()):
                        # Separate numeric page labels from non-numeric ones to avoid misleading ranges
                        numeric_pages = sorted(
                            int(p) for p in info["pages"]
                            if isinstance(p, str) and p.isdigit()
                        )
                        if numeric_pages:
                            # Use a numeric range when we have valid numeric pages
                            if len(numeric_pages) > 1:
                                page_range = f"pages {numeric_pages[0]}-{numeric_pages[-1]}"
                            else:
                                page_range = f"page {numeric_pages[0]}"
                        else:
                            # Fallback: use the raw page labels without inventing a numeric range
                            display_pages = sorted(
                                str(p) for p in info["pages"] if p is not None
                            )
                            if not display_pages:
                                page_range = "pages (unknown)"
                            elif len(display_pages) == 1:
                                page_range = f"page {display_pages[0]}"
                            else:
                                page_range = "pages " + ", ".join(display_pages)
                        doc_summaries.append(f"• **{filename}** — {info['count']} chunks, {page_range}")
                    sections.append(f"### Documents ({len(doc_chunks)})\n\n" + "\n".join(doc_summaries))

                if not sections:
                    return constants.GET_ALL_KNOWLEDGE_EMPTY

                total = len(chat_memories) + sum(info["count"] for info in doc_chunks.values())
                return constants.GET_ALL_KNOWLEDGE_HEADER.format(total=total) + "\n\n".join(sections)

            except Exception as e:
                print(f"Error getting all knowledge: {e}")
                import traceback
                traceback.print_exc()
                return constants.GET_ALL_KNOWLEDGE_ERROR

        @tool
        def get_items_by_tag(tag: str) -> str:
            """
            Retrieve all information/notes that have a specific tag or category.

            MUST use this tool when the user:
            - Mentions a specific tag name (e.g., "show family notes", "notes with tag work")
            - Says "notes that have tag X" or "notes tagged with X"
            - Asks to see notes by category

            The tag parameter should be the exact tag name (case-insensitive).
            DO NOT use query_recall for tag-based filtering - always use this tool instead.
            """
            try:
                # Get all documents for this user (no limit to retrieve everything)
                results = vector_store.get(
                    where={"user_id": user_id}
                )

                if not results or not results.get('documents'):
                    return constants.GET_ITEMS_BY_TAG_EMPTY

                # Filter by tag (case-insensitive)
                tag_lower = tag.lower().strip()
                items = []

                for i, metadata in enumerate(results['metadatas']):
                    tags_str = metadata.get('tags', '')
                    tags_list = [t.strip().lower() for t in tags_str.split(',') if t.strip()]

                    if tag_lower in tags_list:
                        items.append(results['documents'][i])

                if not items:
                    # Show what tags actually exist for debugging
                    all_tags = set()
                    for metadata in results['metadatas']:
                        tags_str = metadata.get('tags', '')
                        if tags_str:
                            all_tags.update([t.strip().lower() for t in tags_str.split(',') if t.strip()])

                    available = ", ".join(sorted(all_tags)[:10])
                    return constants.GET_ITEMS_BY_TAG_NOT_FOUND.format(tag=tag, available=available)

                # Format the results
                if len(items) == 1:
                    return constants.GET_ITEMS_BY_TAG_SINGLE.format(tag=tag, content=items[0])
                else:
                    formatted_items = "\n\n---\n\n".join(items)
                    return constants.GET_ITEMS_BY_TAG_MULTIPLE.format(count=len(items), tag=tag, content=formatted_items)

            except Exception as e:
                print(f"Error getting items by tag: {e}")
                import traceback
                traceback.print_exc()
                return constants.GET_ITEMS_BY_TAG_ERROR.format(tag=tag, error=str(e))

        self.tools = [provide_help, add_recall, add_document, query_recall, delete_recall, get_tags, get_all_knowledge, get_items_by_tag]
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Build Graph
        workflow = StateGraph(AgentState)

        # Add Nodes
        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", ToolNode(self.tools))

        # Add Edges
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent", self.should_continue)
        workflow.add_edge("tools", "agent")

        self.app = workflow.compile()

    def extract_pdf_text(self, file_path: str) -> dict:
        """
        Extract text from PDF without saving to knowledge base.
        Returns dict with filename, page_count, and full_text.
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": constants.EXTRACT_PDF_ERROR_NOT_FOUND.format(path=file_path)}
            if path.suffix.lower() != ".pdf":
                return {"error": constants.EXTRACT_PDF_ERROR_INVALID_TYPE.format(suffix=path.suffix)}

            filename = path.name
            loader = PyPDFLoader(file_path)
            pages = loader.load()

            if not pages:
                return {"error": constants.EXTRACT_PDF_ERROR_NO_CONTENT.format(filename=filename)}

            # Extract text from all pages
            full_text = "\n\n".join([page.page_content for page in pages])
            
            return {
                "filename": filename,
                "page_count": len(pages),
                "full_text": full_text,
                "preview": full_text[:1000] + "..." if len(full_text) > 1000 else full_text
            }
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return {"error": str(e)}

    def call_model(self, state: AgentState):
        messages = state["messages"]

        # Include all message types: system, human, ai, and tool
        filtered_messages = []
        for msg in messages:
            if hasattr(msg, 'type') and msg.type in ('system', 'human', 'ai', 'tool'):
                filtered_messages.append(msg)
            elif getattr(msg, 'role', None) in ('system', 'user', 'assistant', 'tool'):
                filtered_messages.append(msg)

        # Add system prompt if it's the first message or if context is missing
        if not filtered_messages or (filtered_messages[0].type != "system"):
            system_prompt = SystemMessage(content=constants.SYSTEM_PROMPT)
            filtered_messages = [system_prompt] + filtered_messages

        response = self.llm_with_tools.invoke(filtered_messages)
        return {"messages": [response]}

    def should_continue(self, state: AgentState) -> Literal["tools", "__end__"]:
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return "__end__"

    def process_message(self, message: str, history: List, pdf_context: dict = None) -> str:
        # Check forbidden phrases from constants
        if any(phrase in message.lower() for phrase in constants.FORBIDDEN_PHRASES):
            return constants.PROCESS_MESSAGE_FORBIDDEN

        # If PDF context is provided, handle it directly without tools
        if pdf_context and not pdf_context.get("error"):
            # Create a special prompt that includes the document content
            doc_prompt = constants.DOC_ANALYSIS_PROMPT_TEMPLATE.format(
                filename=pdf_context['filename'],
                page_count=pdf_context['page_count'],
                preview=pdf_context['preview'],
                message=message
            )

            # Use the LLM directly without tools for document analysis
            response = self.llm.invoke([HumanMessage(content=doc_prompt)])
            return response.content

        chat_history = []
        for msg in history:
            if getattr(msg, 'role', None) == "user":
                chat_history.append(HumanMessage(content=msg.content))
            elif getattr(msg, 'role', None) == "assistant":
                chat_history.append(AIMessage(content=msg.content))

        chat_history.append(HumanMessage(content=message))

        result = self.app.invoke({"messages": chat_history})

        # Check if add_recall tool was used and return its output directly
        tool_output = None
        for msg in result["messages"]:
            if msg.type == "tool":
                # Get the tool output (this is the raw tool return value)
                tool_output = msg.content
                # Check if it's from add_recall (contains "with tags:")
                if "with tags:" in tool_output:
                    return tool_output

        # Otherwise return the AI's response
        for msg in reversed(result["messages"]):
            if msg.type == "ai":
                return msg.content

        return constants.PROCESS_MESSAGE_ERROR

    def get_suggestions(self, context: str, k: int = 1, min_similarity: float = 0.7) -> List[dict]:
        """
        Fetch related knowledge suggestions based on conversation context.

        Args:
            context: The conversation context to search against
            k: Number of suggestions to return
            min_similarity: Minimum similarity score (0-1) to include suggestion

        Returns:
            List of suggestion dicts with id, content, and full_content
        """
        # Use similarity_search_with_score to get relevance scores
        results = self.vector_store.similarity_search_with_score(
            context,
            k=k,
            filter={"user_id": self.user_id}
        )

        # Filter by similarity threshold and format results
        # Note: ChromaDB returns distance (lower is better), not similarity
        # Convert distance to similarity: similarity = 1 / (1 + distance)
        suggestions = []
        for doc, distance in results:
            similarity = 1 / (1 + distance)
            if similarity >= min_similarity:
                suggestions.append({
                    "id": str(hash(doc.page_content)),
                    "content": doc.page_content[:100] + ("..." if len(doc.page_content) > 100 else ""),
                    "full_content": doc.page_content
                })

        return suggestions

    def get_all_tags(self) -> List[dict]:
        """Get all unique tags with document counts for current user."""
        try:
            # Get all documents for this user
            results = self.vector_store.get(
                where={"user_id": self.user_id}
            )

            if not results or not results.get('metadatas'):
                return []

            # Count tags
            tag_counts = {}
            for metadata in results['metadatas']:
                tags_str = metadata.get('tags', '')
                if tags_str:
                    for tag in tags_str.split(','):
                        tag = tag.strip()
                        if tag:
                            tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # Return sorted by count (descending)
            return [
                {"tag": tag, "count": count}
                for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            ]
        except Exception as e:
            print(f"Error getting tags: {e}")
            return []

    def get_items_by_tag(self, tag: str, limit: int = 100) -> List[dict]:
        """Get all information items with a specific tag."""
        try:
            # Get all documents for this user
            results = self.vector_store.get(
                where={"user_id": self.user_id},
                limit=limit
            )

            if not results or not results.get('documents'):
                return []

            # Filter by tag
            items = []
            for i, metadata in enumerate(results['metadatas']):
                tags_str = metadata.get('tags', '')
                if tag in [t.strip() for t in tags_str.split(',')]:
                    items.append({
                        "id": results['ids'][i],
                        "content": results['documents'][i],
                        "tags": [t.strip() for t in tags_str.split(',') if t.strip()]
                    })

            return items
        except Exception as e:
            print(f"Error getting items by tag: {e}")
            return []

    def regenerate_all_tags(self) -> int:
        """Regenerate tags for all existing documents without tags."""
        try:
            # Get all documents for this user
            results = self.vector_store.get(
                where={"user_id": self.user_id}
            )

            if not results or not results.get('documents'):
                return 0

            count = 0
            for i, metadata in enumerate(results['metadatas']):
                # Only regenerate if no tags exist
                if not metadata.get('tags'):
                    doc_id = results['ids'][i]
                    content = results['documents'][i]
                    tags = self._generate_tags_for_migration(content)

                    # Update metadata
                    self.vector_store.update_document(
                        doc_id,
                        metadata={**metadata, "tags": ",".join(tags)}
                    )
                    count += 1

            return count
        except Exception as e:
            print(f"Error regenerating tags: {e}")
            return 0

    def _generate_tags_for_migration(self, content: str, max_tags: int = 3) -> list:
        """Generate tags for migration (standalone method)."""
        prompt = f"""Analyze this information and generate 1-3 relevant category tags.

Tags should be:
- Single words or short phrases (max 2 words)
- Lowercase
- General categories like: work, personal, recipe, contact, meeting, deadline, health, finance, travel, shopping, learning, etc.

Information: {content}

Return ONLY the tags as a comma-separated list (e.g., "work, meeting" or "recipe, food")."""

        try:
            response = self.llm.invoke(prompt)
            tags = [tag.strip().lower() for tag in response.content.split(',')]
            return [tag for tag in tags if tag][:max_tags]
        except Exception as e:
            print(f"Tag generation failed: {e}")
            return ["note"]  # Fallback tag

    def migrate_legacy_metadata(self) -> dict:
        """
        Migrate existing items that lack source_type metadata to the new schema.
        Adds default values: source_type="chat", source="user", etc.
        Safe to run multiple times — skips already-migrated items.
        """
        try:
            stats = {"total": 0, "migrated": 0, "already_migrated": 0, "errors": 0}
            page_size = 5000
            offset = 0

            while True:
                results = self.vector_store.get(
                    where={"user_id": self.user_id},
                    limit=page_size,
                    offset=offset,
                )

                if not results or not results.get("metadatas"):
                    break

                metadatas = results["metadatas"]
                ids = results.get("ids", [])

                for i, metadata in enumerate(metadatas):
                    stats["total"] += 1

                    if metadata.get("source_type"):
                        stats["already_migrated"] += 1
                        continue

                    try:
                        # Guard against mismatched lengths between metadatas and ids
                        if i >= len(ids):
                            logger.error(
                                f"Missing document ID for metadata index {i} during migration"
                            )
                            stats["errors"] += 1
                            continue

                        doc_id = ids[i]
                        updated_metadata = {
                            **metadata,
                            "source_type": "chat",
                            "source": "user",
                            "source_path": "",
                            "page": "",
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        }
                        self.vector_store._collection.update(
                            ids=[doc_id],
                            metadatas=[updated_metadata],
                        )
                        stats["migrated"] += 1
                    except Exception as e:
                        logger.error(f"Error migrating item {i}: {e}")
                        stats["errors"] += 1

                # Move to the next page; if fewer than page_size items were returned,
                # we've reached the end of the collection.
                offset += len(metadatas)
                if len(metadatas) < page_size:
                    break

            return stats
        except Exception as e:
            print(f"Error migrating legacy metadata: {e}")
            return {"total": 0, "migrated": 0, "already_migrated": 0, "errors": 0}
