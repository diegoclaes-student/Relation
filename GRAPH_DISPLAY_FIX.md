# Graph Display Fix - Admin Network Tab

## Problem
Graph was not displaying in the admin's Network tab when logged in as admin.

## Root Cause Analysis
The application had **two graph components with the same ID** (`network-graph`):
1. One in the public view (line 1015)
2. One in the admin's Network tab (line 1310)

Dash can only have **ONE Output per element ID**. The single `update_graph()` callback was trying to output to both, but Dash's pattern only allowed it to update the first one found. The admin graph never received updates because it had the same ID as the public graph.

## Solution

### 1. Changed Admin Graph ID
Changed the admin graph component from `id='network-graph'` to `id='network-graph-admin'` (line 1310).

**File:** `app_v2.py`, line 1310
```python
# BEFORE:
dcc.Graph(id='network-graph', ...)

# AFTER:
dcc.Graph(id='network-graph-admin', ...)
```

### 2. Added Second Callback
Created a separate callback function `update_graph_admin()` specifically for the admin graph component.

**File:** `app_v2.py`, lines 2523-2595 (new)
```python
@app.callback(
    Output('network-graph-admin', 'figure'),
    [Input('layout-selector', 'value'),
     Input('color-dropdown', 'value'),
     Input('data-version', 'data'),
     Input('auto-refresh', 'n_intervals'),
     Input('node-size-slider', 'value'),
     Input('repulsion-slider', 'value'),
     Input('edge-tension-slider', 'value'),
     Input('search-person', 'value')]
)
def update_graph_admin(layout_type, color_by, data_version, n_intervals, node_size, repulsion, edge_tension, search_person):
    """Build graph for admin tab - identical logic to public graph"""
    # Same implementation as update_graph() but outputs to network-graph-admin
```

## How It Works Now

**Before (Broken):**
```
update_graph() callback
    ↓
  Output('network-graph', 'figure')
    ↓
  Updates public graph ONLY
    ↓
  Admin graph NEVER updated
```

**After (Fixed):**
```
Public graph (network-graph)
    ↓
  update_graph() callback → outputs to network-graph
    ↓
  Displays correctly

Admin graph (network-graph-admin)
    ↓
  update_graph_admin() callback → outputs to network-graph-admin
    ↓
  Displays correctly
```

## Inputs Monitored by Both Callbacks
- `layout-selector`: Graph layout type (community, circular, hierarchical, etc.)
- `color-dropdown`: Color scheme (by community or by degree)
- `data-version`: Triggers refresh when relations change
- `auto-refresh`: Auto-refresh interval
- `node-size-slider`: Node/bubble size adjustment
- `repulsion-slider`: Distance/repulsion between bubbles
- `edge-tension-slider`: Anti-crossing force
- `search-person`: Person search/filter

## Expected Behavior After Fix

✅ **Admin users can now:**
- View the network graph in the Network tab
- See updated graph when adding persons/relations
- Adjust graph layout and parameters
- Search for specific persons in the graph
- See all relations with proper visualization

✅ **Public users still:**
- See the graph normally on the public view
- Have full functionality unchanged

## Verification Steps

1. ✅ Start app: `python app_v2.py`
2. Login as admin
3. Navigate to "📊 Network" tab
4. Graph should now display immediately
5. Add a person/relation and see graph update
6. Test all layout and parameter adjustments

## Files Modified
- `app_v2.py`
  - Line 1310: Changed `id='network-graph'` to `id='network-graph-admin'`
  - Lines 2523-2595: Added `update_graph_admin()` callback

## Technical Notes

- Both callbacks are identical in logic to ensure consistency
- The `prevent_initial_call` parameter uses Dash default (True), which is correct here because `data-version` is initialized to 0, triggering the callback on load
- Search functionality properly filters nodes by name
- Error handling included - displays error message if graph building fails
- Maintains responsive design and all Plotly interactions
