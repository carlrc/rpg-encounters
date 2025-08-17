# Encounter Canvas Save Button Implementation Plan

## Overview

Implement a simple save button that dumps the entire canvas state to the backend using a unified API endpoint. This replaces the current lack of persistence for encounter changes.

## Problem Statement

Currently, all encounter changes are lost on page refresh:

- Position changes from dragging encounters
- Adding/removing characters from encounters  
- Editing encounter names and descriptions
- Creating/deleting connections between encounters

## Solution Architecture

### 1. Frontend Changes

#### UI Components

**Save Button Placement:**

- Position below existing "Add Encounter" button in [`frontend/src/components/EncounterBuilder.vue`](frontend/src/components/EncounterBuilder.vue:440)
- Match styling of existing add button
- There is already a save button in the edit card for characters etc use that

**Visual States:**

- Should follow shared css styling

#### New/Existing Item Tracking

**Simple Flag Approach:**

- Add `isNew: true` flag to element's data object for new items
- No complicated ID parsing needed

**New Encounters:**

```javascript
const newEncounter = {
  id: `encounter-${Date.now()}`,
  type: 'encounter',
  position: { x: centerX, y: centerY },
  data: {
    name: 'New Encounter',
    description: '',
    characters: [],
    isNew: true  // Simple flag
  }
}
```

**New Connections:**

```javascript
const newEdge = {
  id: `edge-${Date.now()}`,
  source: connection.source,
  target: connection.target,
  data: {
    selectable: true,
    isNew: true  // Simple flag
  }
}
```

#### Canvas Serialization

**Detection Logic:**

```javascript
const serializeCanvasState = () => {
  const newEncounters = elements.value.filter(el => 
    el.type === 'encounter' && el.data.isNew
  )
  const existingEncounters = elements.value.filter(el => 
    el.type === 'encounter' && !el.data.isNew
  )
  const newConnections = elements.value.filter(el => 
    el.source && el.target && el.data.isNew
  )
  const existingConnections = elements.value.filter(el => 
    el.source && el.target && !el.data.isNew
  )
  
  return { newEncounters, existingEncounters, newConnections, existingConnections }
}
```

#### Save Function

```javascript
const saveCanvas = async () => {
  try {
    isSaving.value = true
    const { newEncounters, existingEncounters, newConnections, existingConnections } = 
      serializeCanvasState()
    
    const response = await apiService.request('/encounters/canvas/save', {
      method: 'POST',
      body: JSON.stringify({
        new_encounters: transformToBackendFormat(newEncounters),
        existing_encounters: transformToBackendFormat(existingEncounters),
        new_connections: transformToBackendFormat(newConnections),
        existing_connections: transformToBackendFormat(existingConnections)
      })
    })
    
    // Update frontend with new database IDs and remove isNew flags
    updateElementsWithDbIds(response)
    showSavedState()
    
  } catch (error) {
    showErrorState(error)
  } finally {
    isSaving.value = false
  }
}
```

### 2. Backend Changes

#### New Batch Model

**File:** `backend/app/models/canvas.py`

```python
class CanvasSaveRequest(BaseModel):
    """Unified request to save entire canvas state"""
    
    new_encounters: List[EncounterCreate] = Field(default_factory=list)
    existing_encounters: List[EncounterUpdate] = Field(default_factory=list) 
    new_connections: List[ConnectionCreate] = Field(default_factory=list)
    existing_connections: List[ConnectionUpdate] = Field(default_factory=list)

class CanvasSaveResponse(BaseModel):
    """Response with created/updated items and their IDs"""
    
    created_encounters: List[Encounter]
    updated_encounters: List[Encounter]
    created_connections: List[Connection]
    updated_connections: List[Connection]
```

#### New Unified Endpoint

**File:** `backend/app/routers/canvas.py`

```python
@router.post("/save", response_model=CanvasSaveResponse)
async def save_canvas(request: CanvasSaveRequest):
    """Save entire canvas state - handles new and existing items"""
    
    results = CanvasSaveResponse(
        created_encounters=[],
        updated_encounters=[],
        created_connections=[],
        updated_connections=[]
    )
    
    # 1. Create new encounters first (they get real IDs)
    for encounter_data in request.new_encounters:
        created = EncounterStore().create_encounter(encounter_data)
        results.created_encounters.append(created)
    
    # 2. Update existing encounters
    for encounter_update in request.existing_encounters:
        if not encounter_update.id:
            raise HTTPException(status_code=400, detail="Existing encounter missing ID")
        updated = EncounterStore().update_encounter(encounter_update.id, encounter_update)
        if not updated:
            raise HTTPException(status_code=404, detail=f"Encounter {encounter_update.id} not found")
        results.updated_encounters.append(updated)
    
    # 3. Create new connections (using real encounter IDs)
    for connection_data in request.new_connections:
        # Validate encounter references
        encounter_store = EncounterStore()
        if not encounter_store.get_encounter_by_id(connection_data.source_encounter_id):
            raise HTTPException(status_code=404, detail="Source encounter not found")
        if not encounter_store.get_encounter_by_id(connection_data.target_encounter_id):
            raise HTTPException(status_code=404, detail="Target encounter not found")
            
        created = ConnectionStore().create_connection(connection_data)
        results.created_connections.append(created)
    
    # 4. Update existing connections
    for connection_update in request.existing_connections:
        if not connection_update.id:
            raise HTTPException(status_code=400, detail="Existing connection missing ID")
        updated = ConnectionStore().update_connection(connection_update.id, connection_update)
        if not updated:
            raise HTTPException(status_code=404, detail=f"Connection {connection_update.id} not found")
        results.updated_connections.append(updated)
    
    return results
```

#### API Service Updates

**File:** `frontend/src/services/api.js`

```javascript
// Add canvas save method
async saveCanvas(canvasData) {
  return this.request('/canvas/save', {
    method: 'POST',
    body: JSON.stringify(canvasData)
  })
}
```

### 3. Implementation Steps

1. **Backend First:**
   - Add `CanvasSaveRequest` and `CanvasSaveResponse` models to `batch_update.py`
   - Add `/canvas/save` endpoint to new `canvas.py` router
   - Register new router in main.py
   - Test endpoint with sample data

2. **Frontend Integration:**
   - Add save button UI to `EncounterBuilder.vue`
   - Implement `isNew` flag tracking for new items
   - Add canvas serialization logic
   - Add save function with error handling
   - Add visual feedback states

### 4. Benefits

✅ **Simplicity**: Single endpoint, simple flag-based tracking  
✅ **User Control**: Users decide when to save  
✅ **Reliability**: Full canvas dump ensures consistency  
✅ **Clear Feedback**: Visual states communicate save status  
✅ **Efficient**: Batch operations minimize API calls  
✅ **Maintainable**: Clean separation of new vs existing items  

### 5. Future Enhancements

- Add keyboard shortcut (Ctrl+S) for save
- Add auto-save option as user preference
- Add save confirmation dialog for large changes
- Add undo/redo functionality
- Add collaborative editing conflict resolution

## Files to Modify

### Backend

- `backend/app/models/canvas.py` - Add new request/response models
- `backend/app/routers/canvas.py` - Add canvas save endpoint

### Frontend  

- `frontend/src/components/EncounterBuilder.vue` - Add save button and logic
- `frontend/src/services/api.js` - Add canvas save API method

## Conclusion

This implementation provides a clean, user-controlled persistence mechanism that leverages existing infrastructure while adding minimal complexity. The unified endpoint approach simplifies both frontend and backend logic while maintaining proper separation of concerns.
