# ESE mapping to NijiiroID

`data.json` maps song IDs to ESE chart paths. Empty values are unmapped songs.

## Path migration for ESE b8806607

The upstream commit contains bulk renames but no migration script. The migration
removes punctuation, preserves ASCII letters/digits and file extensions, converts
circled 9 to 9, and trims/collapses spaces. It preserves IDs and empty mappings.
All nonempty target paths must exist before any changes are saved.

```powershell
uv run python migrate_data_paths.py
uv run python migrate_data_paths.py --write
uv run python check_data_paths.py --songs-root ../ESE
```

Both scripts default to the sibling `../ESE` checkout. Use `--ese-root` for a
custom migration target or `--songs-root` for a custom checker target (including
a game Songs directory). The checker skips and reports empty mappings, and exits
with status 1 for missing chart files. Migration defaults to a dry run and is
idempotent.
