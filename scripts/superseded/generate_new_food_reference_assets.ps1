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

$SampleFiles = Get-ChildItem -LiteralPath ".\sample_pictures" -Recurse -File
$BeefRollImage = ($SampleFiles | Where-Object { $_.Extension -eq ".png" -and $_.Length -eq 499988 } | Select-Object -First 1).FullName
$RibImage = ($SampleFiles | Where-Object { $_.Extension -eq ".png" -and $_.Length -eq 908491 } | Select-Object -First 1).FullName
if (-not $BeefRollImage) {
  throw "Could not locate beef roll sample image by size 499988 under sample_pictures."
}
if (-not $RibImage) {
  throw "Could not locate pork rib sample image by size 908491 under sample_pictures."
}

$Jobs = @(
  @{
    Prompt = ".\prompts\seedream_reference_assets\shuizhu_beef_roll_chef_character_scene.md"
    Out = (AssetOut "shuizhu_beef_roll_chef_character_scene")
    Stem = "shuizhu_beef_roll_chef_character_scene"
    References = @(
      $BeefRollImage,
      ".\company_logo\AGO.png"
    )
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\shuizhu_beef_roll_cabbage_prep_state.md"
    Out = (AssetOut "shuizhu_beef_roll_cabbage_prep_state")
    Stem = "shuizhu_beef_roll_cabbage_prep_state"
    References = @(
      (AssetGenerated "shuizhu_beef_roll_chef_character_scene"),
      $BeefRollImage
    )
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\shuizhu_beef_roll_spicy_broth_state.md"
    Out = (AssetOut "shuizhu_beef_roll_spicy_broth_state")
    Stem = "shuizhu_beef_roll_spicy_broth_state"
    References = @(
      (AssetGenerated "shuizhu_beef_roll_chef_character_scene"),
      (AssetGenerated "shuizhu_beef_roll_cabbage_prep_state"),
      $BeefRollImage
    )
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\shuizhu_beef_roll_finished_hero_state_v2.md"
    Out = (AssetOut "shuizhu_beef_roll_finished_hero_state_v2")
    Stem = "shuizhu_beef_roll_finished_hero_state_v2"
    References = @(
      (AssetGenerated "shuizhu_beef_roll_chef_character_scene"),
      (AssetGenerated "shuizhu_beef_roll_spicy_broth_state"),
      $BeefRollImage,
      ".\company_logo\AGO.png"
    )
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\kelp_pork_rib_soup_mom_family_scene.md"
    Out = (AssetOut "kelp_pork_rib_soup_mom_family_scene")
    Stem = "kelp_pork_rib_soup_mom_family_scene"
    References = @(
      $RibImage,
      ".\company_logo\UMALL.png"
    )
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\kelp_pork_rib_soup_prep_state.md"
    Out = (AssetOut "kelp_pork_rib_soup_prep_state")
    Stem = "kelp_pork_rib_soup_prep_state"
    References = @(
      (AssetGenerated "kelp_pork_rib_soup_mom_family_scene"),
      $RibImage
    )
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\kelp_pork_rib_soup_simmer_state.md"
    Out = (AssetOut "kelp_pork_rib_soup_simmer_state")
    Stem = "kelp_pork_rib_soup_simmer_state"
    References = @(
      (AssetGenerated "kelp_pork_rib_soup_mom_family_scene"),
      (AssetGenerated "kelp_pork_rib_soup_prep_state"),
      $RibImage
    )
  },
  @{
    Prompt = ".\prompts\seedream_reference_assets\kelp_pork_rib_soup_family_hero_state.md"
    Out = (AssetOut "kelp_pork_rib_soup_family_hero_state")
    Stem = "kelp_pork_rib_soup_family_hero_state"
    References = @(
      (AssetGenerated "kelp_pork_rib_soup_mom_family_scene"),
      (AssetGenerated "kelp_pork_rib_soup_simmer_state"),
      $RibImage,
      ".\company_logo\UMALL.png"
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
