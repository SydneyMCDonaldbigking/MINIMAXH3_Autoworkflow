param(
  [string]$OutputRoot = ".\outputs\seedream_reference_assets",
  [switch]$PrintOnly
)

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

function AssetOut([string]$Name) {
  return (Join-Path $OutputRoot $Name)
}

function AssetGenerated([string]$Name) {
  return (Join-Path $OutputRoot "$Name\generated\$Name-1.png")
}

$Jobs = @(
  @{
    Prompt = ".\prompts\seedream_reference_assets\duck_soup_cook_character_scene.md"
    Out = (AssetOut "duck_soup_cook_character_scene")
    Stem = "duck_soup_cook_character_scene"
    References = @(".\sample_pictures\AGO_ducksoup\duck.png")
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\duck_soup_actor_hands_scene.md"
    Out = (AssetOut "duck_soup_actor_hands_scene")
    Stem = "duck_soup_actor_hands_scene"
    References = @(".\sample_pictures\AGO_ducksoup\duck.png")
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\duck_soup_kitchen_opening_clean.md"
    Out = (AssetOut "duck_soup_kitchen_opening_clean")
    Stem = "duck_soup_kitchen_opening_clean"
    References = @(".\sample_pictures\AGO_ducksoup\duck.png")
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\duck_soup_prep_cut_state.md"
    Out = (AssetOut "duck_soup_prep_cut_state")
    Stem = "duck_soup_prep_cut_state"
    References = @(
      (AssetGenerated "duck_soup_actor_hands_scene"),
      ".\sample_pictures\AGO_ducksoup\duck.png"
    )
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\duck_soup_mid_cooking_state.md"
    Out = (AssetOut "duck_soup_mid_cooking_state")
    Stem = "duck_soup_mid_cooking_state"
    References = @(
      (AssetGenerated "duck_soup_actor_hands_scene"),
      (AssetGenerated "duck_soup_prep_cut_state"),
      (AssetGenerated "duck_soup_kitchen_opening_clean"),
      ".\sample_pictures\AGO_ducksoup\duck.png"
    )
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\duck_soup_finished_hero_state.md"
    Out = (AssetOut "duck_soup_finished_hero_state")
    Stem = "duck_soup_finished_hero_state"
    References = @(
      (AssetGenerated "duck_soup_actor_hands_scene"),
      (AssetGenerated "duck_soup_mid_cooking_state"),
      ".\sample_pictures\AGO_ducksoup\duck.png"
    )
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\egg_tart_family_protagonist_hands.md"
    Out = (AssetOut "egg_tart_family_protagonist_hands")
    Stem = "egg_tart_family_protagonist_hands"
    References = @(".\sample_pictures\Umall_trat\trat_pic.png")
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\egg_tart_family_people_character_scene.md"
    Out = (AssetOut "egg_tart_family_people_character_scene")
    Stem = "egg_tart_family_people_character_scene"
    References = @(".\sample_pictures\Umall_trat\trat_pic.png")
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\egg_tart_family_fridge_to_oven_opening.md"
    Out = (AssetOut "egg_tart_family_fridge_to_oven_opening")
    Stem = "egg_tart_family_fridge_to_oven_opening"
    References = @(
      (AssetGenerated "egg_tart_family_people_character_scene"),
      ".\sample_pictures\Umall_trat\trat_pic.png",
      ".\company_logo\AGO.png"
    )
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\egg_tart_family_oven_baking_state.md"
    Out = (AssetOut "egg_tart_family_oven_baking_state")
    Stem = "egg_tart_family_oven_baking_state"
    References = @(
      (AssetGenerated "egg_tart_family_people_character_scene"),
      (AssetGenerated "egg_tart_family_fridge_to_oven_opening"),
      ".\sample_pictures\Umall_trat\trat_pic.png"
    )
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\egg_tart_family_table_scene_clean.md"
    Out = (AssetOut "egg_tart_family_table_scene_clean")
    Stem = "egg_tart_family_table_scene_clean"
    References = @(
      (AssetGenerated "egg_tart_family_protagonist_hands"),
      ".\sample_pictures\Umall_trat\trat_pic.png"
    )
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\egg_tart_family_afternoon_tea_hands_only.md"
    Out = (AssetOut "egg_tart_family_afternoon_tea_hands_only")
    Stem = "egg_tart_family_afternoon_tea_hands_only"
    References = @(
      (AssetGenerated "egg_tart_family_protagonist_hands"),
      (AssetGenerated "egg_tart_family_table_scene_clean"),
      ".\sample_pictures\Umall_trat\trat_pic.png"
    )
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\egg_tart_family_final_hero_state.md"
    Out = (AssetOut "egg_tart_family_final_hero_state")
    Stem = "egg_tart_family_final_hero_state"
    References = @(
      (AssetGenerated "egg_tart_family_protagonist_hands"),
      (AssetGenerated "egg_tart_family_table_scene_clean"),
      ".\sample_pictures\Umall_trat\trat_pic.png"
    )
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\egg_tart_family_people_final_hero.md"
    Out = (AssetOut "egg_tart_family_people_final_hero")
    Stem = "egg_tart_family_people_final_hero"
    References = @(
      (AssetGenerated "egg_tart_family_people_character_scene"),
      (AssetGenerated "egg_tart_family_table_scene_clean"),
      ".\sample_pictures\Umall_trat\trat_pic.png"
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

  Write-Host "[reference-assets] generating $($Job.Stem)"
  & $Python @Args
  if ($LASTEXITCODE -ne 0) {
    throw "Reference asset generation failed: $($Job.Stem)"
  }
}
