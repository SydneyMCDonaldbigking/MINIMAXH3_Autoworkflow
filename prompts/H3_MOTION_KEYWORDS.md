# H3 Motion Keywords

Use these local motion keywords when writing MiniMax H3 cooking prompts,
especially for 5s clips with thin ingredients, stir-fry, cutting, pouring, or
hand-tool interaction.

## Distilled Rule

Successful clips use fewer actions inside a short time window. The action is
physically simple, low amplitude, and allowed to finish before the next action
begins.

Failed clips usually ask for motion that is too fast or too complex: rapid
stir-fry, repeated tossing, wok shaking, fast chopping, multiple hand/tool
actions at once, or a camera move layered on top of busy food motion.

## Preferred Keywords

- `locked-off`
- `holds still first`
- `very slow push-in 2 cm`
- `slow pull-back 4 cm, then hold still`
- `one controlled low movement`
- `one steady pour`
- `two slow broad pushes only`
- `one slow folding sweep`
- `one gentle fold`
- `one controlled slide`
- `one small adjustment`
- `pause so the texture stays readable`
- `hold still for the final half-second`
- `food rests in the center`
- `low and smooth, not a toss`

## Avoid Keywords

- `quick`
- `rapid`
- `fast stir-fry`
- `tosses through`
- `two quick lifting motions`
- `wok shaking`
- `airborne food`
- `repeated spatula strokes`
- `frantic rhythm`
- `dynamic camera`
- `continuous drift`
- `tight close-up of a hand working a tool`

## Stir-Fry Rewrite Pattern

Instead of:

```text
stirs the pork twice, then tosses the vegetables through in two quick lifting
motions
```

Write:

```text
uses the spatula for two slow broad pushes only: first pushing the pork outward,
then folding it back toward the center. Adds the vegetables in one low pour,
then folds them through once with a wide slow spatula sweep. There is no
tossing, flipping, or rapid wrist motion.
```

## Camera Rule

When the food motion is active, lock the camera. When the camera moves, keep the
food motion nearly still or already completed.

Good pairings:

- locked camera + pour
- locked camera + one fold
- very slow 2 cm push-in + food resting
- 4 cm pull-back + final plated hero

Risky pairings:

- push-in + fast stir-fry
- tilt + knife close-up
- rack focus + pouring + stirring
- handheld drift + wok shaking

## Thin Ingredient Rule

Thin pork strips, chive stems, yellow chives, noodles, egg ribbons, and shredded
vegetables need still frames and clear pauses. In 5s H3 prompts, preserve their
identity by reducing movement:

- show the ingredient still before heat;
- make only one or two slow tool motions;
- end the shot with the food resting, not mid-air;
- name what the ingredient is not when confusion is likely.
