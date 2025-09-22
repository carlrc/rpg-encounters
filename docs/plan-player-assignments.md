# Feature Plan: Assign Players to Encounters (Canvas)

Status: Planned

## Summary
- Add player assignment to encounters on the canvas as a second column of avatars (reuse character icon styles).
- Persist assignments in DB; expose via canvas API; restrict the encounter popup player dropdown to the assigned players only.
- If no players are assigned to an encounter, the dropdown is empty (no fallback to all players).
- Implement DB-level cascade deletion for join rows so associations are automatically removed when an encounter, player, or character is deleted.

## UX Decisions (Confirmed)
- Popup player dropdown shows only players assigned to that encounter.
- If an encounter has no assigned players, the dropdown is empty.
- Players may be assigned to multiple encounters simultaneously (same as characters).
- Reuse existing avatar/icon styles; no visual regressions to character grid or connection handles.

## Backend

### Data Model
- Add many-to-many join table `encounter_players` with ON DELETE CASCADE:
  - `encounter_id` → `encounters.id` (ondelete=CASCADE)
  - `player_id` → `players.id` (ondelete=CASCADE)
- Ensure existing `encounter_characters` also uses ON DELETE CASCADE on both FKs for consistency.

### ORM Relationships (SQLAlchemy)
- EncounterORM
  - `players: List[PlayerORM] = relationship('PlayerORM', secondary=encounter_players, back_populates='encounters')`
  - Keep the existing `characters` relationship as-is (no passive deletes).
- PlayerORM
  - `encounters: List[EncounterORM] = relationship('EncounterORM', secondary=encounter_players, back_populates='players')`
- CharacterORM
  - Keep `encounters` relationship as-is (no passive deletes).
- Import the new association in init_db to ensure table creation.

### Pydantic Models
- `EncounterBase` / `EncounterUpdate` / `Encounter` (backend/app/models/encounter.py)
  - Add `player_ids: List[int] | None` alongside `character_ids`.

### Data Layer
- `EncounterStore` (backend/app/data/encounter_store.py)
  - Add `selectinload(EncounterORM.players)` to queries.
  - In `create`, set `encounter_orm.players` if `player_ids` provided.
  - In `update`, replace `encounter_orm.players` when `player_ids` is included.
  - `_orm_to_encounter`: include `player_ids=[p.id for p in encounter_orm.players]`.

### API
- Canvas GET returns `player_ids` via `Encounter` model.
- Canvas POST (save) accepts `player_ids` for both new and existing encounters and persists them through `EncounterStore`.
- Encounters create/update endpoints accept/pass `player_ids` (no special endpoint changes beyond model updates).

### Cascading Deletions
- Use DB-level cascades in join tables so deleting an encounter, player, or character automatically removes rows in the related join table(s).
- Do not use `passive_deletes`; allow SQLAlchemy to load/delete as needed. DB ON DELETE CASCADE remains the primary safety net for correctness.
- Migration note: existing databases may require dropping and recreating the foreign keys to add ON DELETE CASCADE.

## Frontend

### Data Flow
- EncounterBuilder.vue
  - Load all players (for assignment UI).
  - Transform `/canvas` data to include `data.players` from `player_ids` by resolving IDs to player objects.
  - Provide `getAvailablePlayersForEncounter` analogous to characters.
  - Serialize `player_ids` in save payload (`saveCanvas`) alongside `character_ids`.
  - Pass assigned and available players into `EncounterNode`.
  - Pass assigned players for the selected encounter into `CharacterEncounterPopup`.

### Canvas Node UI
- EncounterNode.vue
  - Add a second column for Players next to Characters.
  - Reuse avatar markup/classes from the character grid.
  - Add an “Add Player” button and dropdown mirroring “Add Character”.
  - Emit `add-player` / `remove-player` events.

### Encounter Popup
- CharacterEncounterPopup.vue
  - Accept a prop with the assigned players for the selected encounter.
  - Populate the `<select>` strictly from that prop.
  - If no assigned players, the dropdown is empty.

## Acceptance Criteria
- Canvas nodes show character and player avatar columns with consistent styling.
- DM can add/remove players on the canvas; saving and reloading preserves assignments.
- Encounter popup lists only assigned players; empty if none assigned.
- DB cascade removes join rows automatically when entities are deleted.
- No regressions to existing character UI/behavior.
- Unit tests updated and passing (including new cases for player_ids and cascades).

## Implementation Steps (Engineering TODOs)
1. Add `encounter_players` association table
2. Link players↔encounters in ORM
3. Add CASCADE FKs to join tables
4. Extend Encounter models: `player_ids`
5. Update `EncounterStore` for players
6. Include `player_ids` in canvas APIs
7. Load players in `EncounterBuilder`
8. Add players column UI to `EncounterNode`
9. Support add/remove players on canvas
10. Serialize `player_ids` in `saveCanvas`
11. Filter popup dropdown by assigned players
12. Update seeds/fixtures and verify cascades
13. Update unit tests for encounters/canvas to include `player_ids`
14. Add tests for deletion cascades (player/character/encounter)

## Tests and Seeding
- Update test fixtures:
  - `backend/tests/fixtures/encounters.py`: add `player_ids` where appropriate.
  - Any tests asserting encounter or canvas payloads: include `player_ids` in expected data.
  - Add tests verifying that deleting a player/character/encounter removes join rows and leaves remaining data consistent.
- Update dev/test seed script:
  - `backend/tests/fixtures/seed_data.py`: create some player↔encounter assignments via `player_ids`.
  - If there is a non-test seed path, mirror minimal assignments for local dev convenience.
  - Re-generate database (or run migration) to pick up ON DELETE CASCADE on join tables.

## Notes / Risks
- Adding ON DELETE CASCADE to existing FKs needs migration; dev environments can rebuild via existing init tooling.
- Ensure `selectinload` on both `characters` and `players` to avoid N+1 when returning canvas.
- Keep UI responsive: loading players once at builder load prevents extra fetches.
