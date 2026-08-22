---
name: reels-captions
description: Write or rewrite the Instagram Reels subtitle track and caption cues for a 15-second UMALL / Asian Grocer Online food ad. Use whenever a dish needs reels_subtitles.srt, reels_caption_cues.md or analysis/caption-cues/clip-0N.json written, reviewed or fixed.
---

# Reels captions for a 15-second food ad

## The failure this exists to prevent

The first pass at these was nine captions, evenly spaced about 1.5 seconds apart,
each describing what was already on screen:

```
0.4s  Start with whole prawns          <- the shot is prawns
2.1s  Bruise the lemongrass            <- the shot is lemongrass being bruised
3.8s  Aromatics into boiling stock     <- still narrating the picture
```

The client's verdict was blunt and correct: that is a recipe read aloud, not
Reels copy. **A caption that describes the picture is wasted.** The viewer can
already see the picture. The caption's job is to supply what the picture cannot.

## Structure

Five or six captions across 15.55 seconds. Never nine. Uneven spacing, with
silence where the footage carries itself.

| Window | Job |
| --- | --- |
| 0.0 - 2.6 s | **Hook.** A claim, a problem, or a mistake the viewer has made. This is the only line that decides whether the rest is seen. |
| 2.6 - 5.0 s | **Setup.** Name the promise or the cause. |
| 5.0 - 10.5 s | **Turn.** The one technique that actually matters - the step people get wrong, stated as an instruction. Usually two captions. |
| 10.5 - 13.5 s | **Payoff.** What the result looks like, in the words the viewer would use. |
| 13.5 - 15.2 s | **Land it.** A consequence, a cost, or a line worth repeating. Not a summary. |

## Rules

- **Never describe what is on screen.** If the caption would still make sense
  with the video muted and hidden, it is doing nothing.
- **Open on the viewer, not the ingredient.** "If your kimchi fried rice comes
  out soggy" beats "Chop the kimchi small". The viewer recognises themselves in
  the first second.
- **The turn is the research.** Every dish went through recipe research whose
  whole point was finding the step that gets done wrong. That step is the
  caption. If the ad has no such step, the research was not done.
- **End on a cost, not a compliment.** "Any longer and they are rubber" lands.
  "Hot, sour and delicious" does not.
- **Fragments are fine.** "Beef first. Alone. Until there is no red left."
- Two to six words per *cue* in the clip-relative JSON; the SRT track may run
  longer per line because it is read, not overlaid as a chip.
- No prices, no availability claims, no health claims, no superlatives you
  cannot support.
- The video prompt forbids generated subtitles. These are burned in during the
  edit, so they are edit data and never appear in an H3 prompt.

## Worked example

Tom yum goong, where the research finding was that the prawns need sixty seconds
and are ruined by more:

```
 0.3-2.6   Most tom yum is ruined in the last minute
 3.0-5.0   The broth is built before the prawns ever see it
 5.6-8.4   Lemongrass, galangal, lime leaf. Then the chilli paste.
 9.4-11.6  Prawns go in. Count to sixty.
12.0-13.6  Out the second they turn orange
13.9-15.2  Any longer and they are rubber
```

Kimchi beef fried rice, where the finding was that rice added early goes soggy:

```
 0.3-2.6   If your kimchi fried rice comes out soggy
 2.9-4.6   it is because you added the rice too early
 5.2-7.8   Beef first. Alone. Until there is no red left.
 8.4-10.6  Then the kimchi, and fry the brine off it
11.0-13.0  Only now does the rice go in
13.4-15.2  Every grain separate, every grain red
```

Both open on a problem, both give the cause before the instruction, and both end
on what happens if you get it wrong.

## Files to produce

Per dish, under `sequence_outputs/<slug>/`:

- `05_social/reels_subtitles.srt` - the full 15-second track, 5-6 cues
- `05_social/reels_caption_cues.md` - the same, human-readable, for the editor
- `04_analysis/caption-cues/clip-0N.json` - clip-relative, `schema_version: 1`,
  two to six words per cue, two cues per clip is usually right

Clip-relative timings restart at 0.0 for each clip. A 15.55-second ad is three
5.167-second clips, so a caption at 9.4 s in the SRT is at about 4.2 s in clip 02.

## Checking your own work

Read only the captions, in order, without the video. They should tell a small
complete story with a problem and a resolution. If they read as a numbered list
of steps, start again.
