# Auto-Tagging Feature - Implementation Plan

## Overview

Automatically tag stored information by topic/category using AI to analyze content. This helps users organize and filter their knowledge base without manual categorization.

---

## Current State Analysis

**Storage System:**

- Uses ChromaDB for vector embeddings
- Storage method: `add_recall` tool in `backend/brain.py`
- Current metadata: Only `user_id` for data isolation
- No categorization or filtering mechanism

**Retrieval System:**

- `query_recall` tool performs semantic similarity search
- Returns top 3 most similar documents
- No category-based filtering

---

## Feature Design

### What are Tags?

Tags are semantic labels automatically generated when information is stored:

- Examples: `work`, `personal`, `meeting`, `recipe`, `contact`, `deadline`, `project`
- Multiple tags per piece of information
- Used for filtering and organization

### How Auto-Tagging Works

1. **Storage Phase:** When user saves information via `add_recall`:
   - AI analyzes the content
   - Generates 1-3 relevant tags
   - Stores tags in ChromaDB metadata

2. **Retrieval Phase:** When user queries via `query_recall`:
   - Can optionally filter by tags
   - Show tags in AI responses
   - Suggest tag-based searches

3. **Organization:** New endpoints to:
   - List all user's tags with counts
   - Browse information by tag
   - Update/remove tags

---

## Implementation Plan

### Phase 1: Backend - Tag Generation

#### 1.1 Create Tag Generator (`backend/tag_generator.py`)

```python
class TagGenerator:
    def __init__(self, llm):
        self.llm = llm

    def generate_tags(self, content: str, max_tags: int = 3) -> List[str]:
        """
        Use LLM to generate relevant tags for content.
        Returns list of tags (lowercase, alphanumeric).
        """
        prompt = f'''Analyze this information and generate 1-3 relevant category tags.
Tags should be:
- Single words or short phrases (2 words max)
- Lowercase
- General categories like: work, personal, recipe, contact, meeting, deadline, health, finance, travel, shopping, etc.

Information: {content}

Return ONLY the tags as a comma-separated list.'''

        response = self.llm.invoke(prompt)
        tags = [tag.strip().lower() for tag in response.content.split(',')]
        return tags[:max_tags]
```

#### 1.2 Integrate with `add_recall` Tool

Update `backend/brain.py`:

```python
# In SecondBrain.__init__
self.tag_generator = TagGenerator(self.llm)

@tool
def add_recall(content: str) -> str:
    # Generate tags
    tags = tag_generator.generate_tags(content)

    # Add metadata with user_id AND tags
    vector_store.add_texts(
        texts=[content],
        metadatas=[{
            "user_id": user_id,
            "tags": ",".join(tags)  # Store as comma-separated string
        }]
    )
    return f"Information stored successfully with tags: {', '.join(tags)}"
```

#### 1.3 Update `query_recall` Tool

Add optional tag filtering:

```python
@tool
def query_recall(query: str, filter_tags: List[str] = None) -> str:
    """
    Useful for retrieving information from the second brain.
    Optionally filter by tags.
    """
    filter_dict = {"user_id": user_id}

    if filter_tags:
        # ChromaDB $in operator for list matching
        filter_dict["tags"] = {"$in": filter_tags}

    results = vector_store.similarity_search(
        query,
        k=3,
        filter=filter_dict
    )
    # ... rest of logic
```

### Phase 2: Backend - Tag Management API

#### 2.1 Add Tag Endpoints (`backend/main.py`)

```python
@app.get("/tags", response_model=List[TagInfo])
async def get_user_tags(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get all tags for current user with document counts.
    Returns: [{ tag: "work", count: 5 }, ...]
    """
    user_brain = get_user_brain(current_user.id)
    tags = user_brain.get_all_tags()
    return tags

@app.get("/tags/{tag}/items", response_model=List[TaggedItem])
async def get_items_by_tag(
    tag: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get all information items with a specific tag.
    """
    user_brain = get_user_brain(current_user.id)
    items = user_brain.get_items_by_tag(tag)
    return items

@app.post("/tags/regenerate")
async def regenerate_tags(
    current_user: User = Depends(get_current_user)
):
    """
    Regenerate tags for all existing information.
    Useful for migrating existing data.
    """
    user_brain = get_user_brain(current_user.id)
    count = user_brain.regenerate_all_tags()
    return {"message": f"Regenerated tags for {count} items"}
```

#### 2.2 Add Tag Methods to SecondBrain

```python
def get_all_tags(self) -> List[dict]:
    """Get all unique tags with counts."""
    # Query all documents for this user
    # Aggregate tags and counts
    # Return sorted by count

def get_items_by_tag(self, tag: str) -> List[dict]:
    """Get all items with specific tag."""
    results = self.vector_store.similarity_search(
        "",  # Empty query returns all
        k=100,  # Max results
        filter={
            "user_id": self.user_id,
            "tags": {"$contains": tag}
        }
    )
    return [{"content": doc.page_content, "tags": doc.metadata.get("tags", "")}
            for doc in results]

def regenerate_all_tags(self) -> int:
    """Regenerate tags for all existing documents."""
    # Fetch all user documents
    # For each document, generate tags
    # Update metadata
    # Return count
```

#### 2.3 Add Response Models

```python
# In backend/models.py

class TagInfo(BaseModel):
    tag: str
    count: int

class TaggedItem(BaseModel):
    id: str
    content: str
    tags: List[str]
```

### Phase 3: Frontend - Tag Display

#### 3.1 Show Tags in AI Responses

Update `MessageBubble.jsx` to display tags when information is stored:

```jsx
// Parse AI response for tags
// Example: "Information stored successfully with tags: work, meeting"
// Show tags as colored chips below the message
```

#### 3.2 Create Tag Component

New file: `frontend/src/components/tags/TagChip.jsx`

```jsx
export default function TagChip({ tag, onClick, size = "sm" }) {
  return (
    <span
      onClick={onClick}
      className="inline-flex items-center rounded-full bg-blue-100 px-2 py-1 text-xs
                 font-medium text-blue-800 hover:bg-blue-200 cursor-pointer
                 dark:bg-blue-900 dark:text-blue-200"
    >
      #{tag}
    </span>
  );
}
```

### Phase 4: Frontend - Tag Browser (Optional)

#### 4.1 Create Tags Page

New file: `frontend/src/pages/TagsPage.jsx`

- Display all tags as a tag cloud or list
- Show document count per tag
- Click tag to view all items with that tag
- Search/filter functionality

#### 4.2 Add to Navigation

Add link to tags page in Sidebar component.

---

## User Experience Flow

### Storing Information

```text
User: "Remember my dentist appointment is next Tuesday at 2pm"
AI: "Information stored successfully with tags: health, appointment"
[Shows: #health #appointment chips below message]
```

### Querying with Tags

```text
User: "What work meetings do I have?"
AI: [Searches with implicit "work" tag filter]
"Here are your work meetings: ..."
```

### Browsing Tags

```text
User clicks on Sidebar → Tags
Shows: #work (15) #personal (23) #meeting (8) #recipe (12)
User clicks #recipe
Shows: List of all stored recipes
```

---

## Implementation Sequence

### Step 1: Backend Tag Generation (2-3 hours)

1. Create `tag_generator.py`
2. Update `add_recall` to generate and store tags
3. Test tag generation with various content types

### Step 2: Backend Tag Retrieval (1-2 hours)

1. Update `query_recall` to support tag filtering
2. Test filtered searches
3. Modify response format to include tags

### Step 3: Backend Tag Management API (2-3 hours)

1. Add tag aggregation methods to SecondBrain
2. Create `/tags` endpoints
3. Add tag regeneration endpoint for existing data
4. Test with curl/Postman

### Step 4: Frontend Tag Display (2-3 hours)

1. Create TagChip component
2. Update MessageBubble to show tags
3. Parse tags from AI responses
4. Style with Tailwind

### Step 5: Frontend Tag Browser (3-4 hours - Optional)

1. Create TagsPage component
2. Add tag API calls to services/api.js
3. Add navigation link
4. Implement tag filtering UI

---

## Database Migration

**For Existing Data:**

Since existing ChromaDB entries don't have tags, provide a migration endpoint:

```python
@app.post("/migrate/add-tags")
async def migrate_existing_data(current_user: User = Depends(get_current_user)):
    """
    One-time migration: Add tags to all existing information.
    """
    user_brain = get_user_brain(current_user.id)
    count = user_brain.regenerate_all_tags()
    return {"migrated": count}
```

Users can trigger this once after the feature is deployed.

---

## Tag System Design Decisions

### 1. **Tag Granularity**

- **Chosen:** Broad categories (work, personal, meeting, etc.)
- **Rationale:** Easy to understand, less noise, better for small knowledge bases
- **Alternative:** Fine-grained tags (could be too many for personal use)

### 2. **Tag Count per Item**

- **Chosen:** 1-3 tags per item
- **Rationale:** Balance between specificity and simplicity
- **Configurable:** Can adjust max_tags parameter

### 3. **Tag Format**

- **Chosen:** Lowercase, alphanumeric, 1-2 words
- **Examples:** `work`, `health`, `contact-info`, `recipe`
- **Rationale:** Consistent, easy to match and filter

### 4. **Tag Storage**

- **Chosen:** Comma-separated string in ChromaDB metadata
- **Rationale:** ChromaDB supports metadata filtering, simple to implement
- **Alternative:** Separate tags table (more complex, not needed for MVP)

### 5. **Tag Generation Method**

- **Chosen:** AI-generated using LLM
- **Rationale:** Automatic, consistent, leverages existing AI
- **Alternative:** Keyword extraction (less intelligent, rule-based)

---

## Example Tag Categories

Common tags that AI might generate:

- **Life:** `personal`, `family`, `health`, `fitness`, `hobby`
- **Work:** `work`, `project`, `meeting`, `deadline`, `client`
- **Info:** `contact`, `password`, `account`, `note`, `reminder`
- **Content:** `recipe`, `article`, `book`, `movie`, `music`
- **Finance:** `finance`, `budget`, `expense`, `investment`
- **Travel:** `travel`, `trip`, `vacation`, `hotel`, `flight`
- **Shopping:** `shopping`, `wishlist`, `purchase`, `product`
- **Learning:** `learning`, `course`, `skill`, `education`

---

## Files to Create/Modify

| File                                             | Action                                   |
| ------------------------------------------------ | ---------------------------------------- |
| `backend/tag_generator.py`                       | New file - Tag generation logic          |
| `backend/brain.py`                               | Update add_recall and query_recall tools |
| `backend/models.py`                              | Add TagInfo and TaggedItem models        |
| `backend/main.py`                                | Add tag management endpoints             |
| `frontend/src/components/tags/TagChip.jsx`       | New file - Tag display component         |
| `frontend/src/components/chat/MessageBubble.jsx` | Parse and display tags                   |
| `frontend/src/pages/TagsPage.jsx`                | New file - Tag browser (optional)        |
| `frontend/src/services/api.js`                   | Add tag API methods                      |

---

## Testing Plan

1. **Tag Generation:** Store various content types, verify tag relevance
2. **Tag Filtering:** Query with tag filters, verify results are filtered
3. **Tag Aggregation:** Check tag counts are accurate
4. **Migration:** Run tag regeneration on existing data
5. **UI Display:** Verify tags appear correctly in chat
6. **Tag Browser:** Test tag browsing and filtering (if implemented)

---

## Success Metrics

- **Tag Accuracy:** >80% of generated tags are semantically relevant
- **User Adoption:** Users naturally understand and use tags
- **Search Improvement:** Tag-filtered searches return more relevant results
- **Organization:** Users can easily browse information by category

---

## Future Enhancements

1. **Custom Tags:** Allow users to manually add/edit tags
2. **Tag Suggestions:** Suggest tags based on usage patterns
3. **Tag Hierarchies:** Parent/child tag relationships (e.g., work → project)
4. **Tag Renaming:** Bulk rename or merge tags
5. **Smart Filters:** Combine tags with date ranges or search terms
6. **Tag Analytics:** Show most-used tags, tag trends over time

---

## Complexity Assessment

**Difficulty:** Medium

**Why:**

- AI tag generation is straightforward with existing LLM
- ChromaDB metadata filtering is well-supported
- UI changes are minimal
- No complex database migrations needed

**Estimated Time:** 10-15 hours total

**Dependencies:**

- Existing LLM (already available)
- ChromaDB (already integrated)
- No new external services required
