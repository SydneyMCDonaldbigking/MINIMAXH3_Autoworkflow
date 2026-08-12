# Superseded

Three PowerShell scripts that generated Seedream references before
`generate_dish_assets.py` existed. Each hard-coded one dish's four prompts, which
is why there are three of them and why they drifted apart.

Kept rather than deleted because they are the record of what the config schema
came from: the fields in `prompts/dish_configs/*.json` are the parts of these
scripts that varied between dishes.

Do not use them. `generate_dish_assets.py` reads a config, chains the references
so the cook and kitchen carry across, supports `--kinds` for partial re-renders,
and carries the negative rules that were learned after these were written.
