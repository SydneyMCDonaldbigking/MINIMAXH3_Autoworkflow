param(
  [string]$OutputRoot = ".\outputs\seedream_reference_assets",
  [switch]$PrintOnly
)

# Seedream reference bible for the tomato braised beef brisket ad.
#
# Four assets, generated in order because each one feeds the next as a
# reference. That chain is what keeps the cook, the kitchen and the beef
# looking like the same shoot across all three clips.
#
#   1. cook_character_scene    the person and the kitchen
#   2. prep_state              proves the cutting really happened, defines cut sizes
#   3. braise_state            the working state clip 02 has to match
#   4. finished_hero_state     the frame the whole ad lands on
#
# H3 is bad at inventing ingredient processing, so the prep state exists
# precisely so no clip has to show a knife doing close-up work. See the house
# rules in MINIMAX_H3_3X5_NATIVE1080_WORKFLOW.md.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$BundledPython = "C:\Users\uryuu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (Test-Path $BundledPython) {
  $Python = $BundledPython
} else {
  $Python = "python"
}

$Common = @(
  "--model", "bytedance-seed/seedream-4.5",
  "--resolution", "2K",
  "--aspect-ratio", "9:16",
  "--final-size", "1080x1920"
)

# Located by filename, not by byte size: the product folder name contains CJK
# characters and hardcoding either the path or the size is fragile.
$BrisketImage = (Get-ChildItem -Path ".\sample_pictures" -Recurse -Filter "beef.png" |
                 Select-Object -First 1).FullName
if (-not $BrisketImage) {
  throw "Could not find beef.png under .\sample_pictures"
}
Write-Host "[seedream-reference-assets] product image: $BrisketImage"

function AssetOut([string]$Name) {
  return (Join-Path $OutputRoot $Name)
}

function AssetGenerated([string]$Name) {
  return (Join-Path $OutputRoot "$Name\generated\$Name-1.png")
}

$Jobs = @(
  @{
    Prompt = ".\prompts\seedream_reference_assets\tomato_beef_brisket_cook_character_scene.md"
    Out = (AssetOut "tomato_beef_brisket_cook_character_scene")
    Stem = "tomato_beef_brisket_cook_character_scene"
    References = @(
      $BrisketImage,
      ".\company_logo\AGO.png"
    )
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\tomato_beef_brisket_prep_state.md"
    Out = (AssetOut "tomato_beef_brisket_prep_state")
    Stem = "tomato_beef_brisket_prep_state"
    References = @(
      (AssetGenerated "tomato_beef_brisket_cook_character_scene"),
      $BrisketImage
    )
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\tomato_beef_brisket_braise_state.md"
    Out = (AssetOut "tomato_beef_brisket_braise_state")
    Stem = "tomato_beef_brisket_braise_state"
    References = @(
      (AssetGenerated "tomato_beef_brisket_cook_character_scene"),
      (AssetGenerated "tomato_beef_brisket_prep_state"),
      $BrisketImage
    )
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\tomato_beef_brisket_finished_hero_state.md"
    Out = (AssetOut "tomato_beef_brisket_finished_hero_state")
    Stem = "tomato_beef_brisket_finished_hero_state"
    References = @(
      (AssetGenerated "tomato_beef_brisket_cook_character_scene"),
      (AssetGenerated "tomato_beef_brisket_braise_state"),
      $BrisketImage,
      ".\company_logo\AGO.png"
    )
  }
)

foreach ($Job in $Jobs) {
  $Args = @(
    ".\image2_first_frame.py",
    "--prompt-file", $Job.Prompt,
    "--out-dir", $Job.Out,
    "--stem", $Job.Stem
  ) + $Common

  foreach ($Reference in $Job.References) {
    $Args += @("--reference", $Reference)
  }

  if ($PrintOnly) {
    Write-Host "$Python $($Args -join ' ')"
    continue
  }

  Write-Host "[seedream-reference-assets] generating $($Job.Stem)"
  & $Python @Args
  if ($LASTEXITCODE -ne 0) {
    throw "Reference asset generation failed: $($Job.Stem)"
  }
}
