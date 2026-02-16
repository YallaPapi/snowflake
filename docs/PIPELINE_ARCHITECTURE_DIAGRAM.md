# SNOWFLAKE VIDEO PIPELINE: FULL ARCHITECTURE & GAP ANALYSIS

**Generated:** 2026-02-16
**Status:** Shot Engine complete, Video Engine missing, Critical bugs in shot list generation

---

## 1. FULL PIPELINE ARCHITECTURE

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         SNOWFLAKE VIDEO GENERATION PIPELINE                      │
│                    (Story → Screenplay → Shots → Video Clips)                    │
└──────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: SCREENPLAY ENGINE (Save the Cat Method)                                │
│ Location: src/screenplay_engine/                                                 │
│ Status: ✅ COMPLETE (v2.0.0, 970 tests passing)                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
  │
  │  INPUT: User seed idea
  │
  ├─► Step 1: Logline (Ch.1)
  │     └─► sp_step_1_logline.json
  │
  ├─► Step 2: Genre Classification (Ch.2)
  │     └─► sp_step_2_genre.json
  │
  ├─► Step 3: Hero Construction (Ch.3)
  │     └─► sp_step_3_hero.json (hero, antagonist, b_story_character)
  │
  ├─► Step 3b: World Bible (NEW)
  │     └─► sp_step_3b_world_bible.json
  │         ├─ arena (rules, time_period, scope)
  │         ├─ geography (landscape, climate, key_locations[])
  │         ├─ social_structure (class_system, power_dynamics, tensions)
  │         ├─ economy (how_people_earn, scarcity_abundance)
  │         ├─ culture (values, customs, taboos)
  │         ├─ daily_life (morning_rhythm, sensory_palette)
  │         └─ rules_of_conflict (story_engine, systemic_pressure, stakes)
  │
  ├─► Step 3c: Full Cast (NEW, LAYERED)
  │     └─► sp_step_3c_full_cast.json
  │         ├─ tier_1_major_supporting[] (5+ scenes, arcs, detailed bios)
  │         ├─ tier_2_minor_supporting[] (2-4 scenes, specific functions)
  │         └─ tier_3_background_types[] (archetypes, population flavor)
  │
  ├─► Step 4: Beat Sheet (Ch.4)
  │     └─► sp_step_4_beat_sheet.json (15 STC beats with %targets)
  │
  ├─► Step 5: Board (Ch.5)
  │     └─► sp_step_5_board.json (scene cards across 4 rows/acts)
  │
  ├─► Step 5b: Visual Bible (NEW)
  │     └─► sp_step_5b_visual_bible.json ◄─────┐
  │         ├─ style_bible                      │ CRITICAL FOR
  │         │   ├─ visual_tone                  │ IMAGE/VIDEO
  │         │   ├─ color_palette                │ GENERATION
  │         │   ├─ lighting_style               │
  │         │   ├─ texture_grain                │
  │         │   ├─ reference_films[]            │
  │         │   ├─ shape_language               │
  │         │   └─ do_not[] (negative prompts)  │
  │         ├─ color_script[] (per-act mood)    │
  │         ├─ location_designs[]               │
  │         │   ├─ location_name                │
  │         │   ├─ visual_description           │
  │         │   ├─ time_variants{}              │
  │         │   ├─ color_sub_palette[]          │
  │         │   ├─ mood_keywords[]              │
  │         │   └─ t2i_base_prompt ◄────────────┤──┐
  │         ├─ character_visual_notes[]         │  │
  │         │   ├─ character_name               │  │
  │         │   ├─ physical_summary             │  │
  │         │   ├─ wardrobe_evolution           │  │
  │         │   ├─ signature_visual_identifier  │  │
  │         │   └─ t2i_portrait_prompt ◄────────┤──┤─ T2I Prompts
  │         └─ cinematography_approach          │  │  (for Flux/SD)
  │             ├─ default_lens                 │  │
  │             ├─ handheld_vs_dolly            │  │
  │             ├─ depth_of_field               │  │
  │             └─ aspect_ratio                 │  │
  │                                              │  │
  ├─► Step 6: Screenplay (end Ch.5)             │  │
  │     └─► sp_step_6_screenplay.json           │  │
  │                                              │  │
  ├─► Step 7: 7 Immutable Laws (Ch.6)           │  │
  │     └─► sp_step_7_laws.json                 │  │
  │                                              │  │
  ├─► Step 8: 9 Diagnostic Checks (Ch.7)        │  │
  │     └─► sp_step_8_diagnostics.json          │  │
  │                                              │  │
  └─► Step 9: Marketing (Ch.8)                  │  │
      └─► sp_step_9_marketing.json              │  │
                                                 │  │
                                                 │  │
┌────────────────────────────────────────────────┼──┼────────────────────────────┐
│ PHASE 2: SHOT ENGINE (Screenplay → Shot List) │  │                            │
│ Location: src/shot_engine/                    │  │                            │
│ Status: ✅ COMPLETE (v12.0.0)                 │  │                            │
└────────────────────────────────────────────────┼──┼────────────────────────────┘
  │                                              │  │
  │  INPUT: sp_step_8_screenplay.json           │  │
  │         sp_step_3_hero.json                 │  │
  │         sp_step_5b_visual_bible.json ───────┘  │
  │         sp_step_3b_world_bible.json            │
  │         sp_step_3c_full_cast.json              │
  │                                                 │
  ├─► V1: Scene Decomposition (step_v1_decomposition.py)
  │     - Parse screenplay scenes into shot segments
  │     - Detect content triggers (dialogue, action, reveals, etc.)
  │     - Extract characters_in_frame from action text
  │     - Classify emotional_intensity, is_disaster_moment
  │     └─► Intermediate: List[ShotSegment]
  │
  ├─► V2: Shot Type Assignment (step_v2_shot_types.py)
  │     - Map trigger → default shot type (wide, close-up, etc.)
  │     - Apply action patterns (shot variety cycle)
  │     - Adjust for emotional intensity
  │     └─► Updated: shot.shot_type
  │
  ├─► V3: Camera Behavior (step_v3_camera.py)
  │     - Map trigger → camera movement (static, tracking, push-in)
  │     - Apply cinematography rules from visual_bible
  │     - Set lens_mm, camera_height, distance_band
  │     └─► Updated: shot.camera_movement, lens_mm, etc.
  │
  ├─► V4: Duration & Pacing (step_v4_pacing.py)
  │     - Calculate raw durations from trigger + dialogue length
  │     - Apply beat-based pacing curve (moderate/rapid/etc.)
  │     - Scale to match scene target_duration_seconds
  │     └─► Updated: shot.duration_seconds, pacing_curve
  │
  ├─► V5: Transition Planning (step_v5_transitions.py)
  │     - Determine cut vs dissolve vs fade
  │     - Apply beat-level transition rules
  │     - Set crossfade durations
  │     └─► Updated: shot.transition_to_next, crossfade_duration
  │
  └─► V6: Prompt Generation (step_v6_prompts.py) ◄────┐
        - Normalize slugline → setting_ref_id          │
        - Normalize characters_in_frame → character_ref_ids
        - Build scene_prompt (I2I edit instruction)    │
        - Build video_prompt (I2V motion description)  │
        - Pull t2i_base_prompt from visual_bible ──────┘
        - Pull t2i_portrait_prompt from visual_bible
        - Build negative_prompt from style_bible.do_not[]
        └─► OUTPUT: shot_list.json (754 shots for 40-scene screenplay)
              │
              ├─ project_id, title, format, total_shots, total_duration_seconds
              └─ scenes[]
                  ├─ scene_number, slugline, beat, emotional_polarity
                  ├─ visual_intent{emotional_start, emotional_end, conflict_axis, etc.}
                  ├─ target_duration_seconds
                  └─ shots[]  ◄────────────────────────────────────────────────┐
                      ├─ shot_id (s001_001, s001_002, ...)                    │
                      ├─ trigger, content, dialogue_text, dialogue_speaker    │
                      ├─ characters_in_frame[] ◄── ⚠️ BUG: often empty       │
                      ├─ shot_type, camera_movement, lens_mm                  │
                      ├─ duration_seconds, pacing_curve                       │
                      ├─ transition_to_next, crossfade_duration               │
                      │                                                        │
                      │  ── V6 PROMPT OUTPUTS (for visual bible) ──           │
                      ├─ setting_ref_id (e.g., "east_la_strip_mall_...")     │
                      ├─ character_ref_ids[] (e.g., ["rae_calder", ...])     │
                      ├─ character_prompt_prefix (T2I portrait prompt)        │
                      ├─ scene_prompt (I2I: character placement/blocking) ◄───┤── TO VIDEO ENGINE
                      ├─ video_prompt (I2V: motion verbs) ◄── ⚠️ BUG         │
                      ├─ negative_prompt (style_bible.do_not[])              │
                      ├─ ambient_description (audio cues)                     │
                      ├─ init_image_source (reference|previous_frame|gen)     │
                      └─ aspect_ratio ("16:9")                                │
                                                                              │
                                                                              │
┌─────────────────────────────────────────────────────────────────────────────┼───┐
│ PHASE 3: VISUAL BIBLE ASSET MANAGER (Image Cache & State Tracking)         │   │
│ Location: ❌ MISSING — needs to be built                                   │   │
│ Status: 🚧 NOT IMPLEMENTED                                                 │   │
└─────────────────────────────────────────────────────────────────────────────┼───┘
  │                                                                           │
  │  INPUT: shot_list.json + sp_step_5b_visual_bible.json                    │
  │                                                                           │
  ├─► Asset Index Builder                                                    │
  │     - Parse visual_bible.location_designs[]                              │
  │     - Parse visual_bible.character_visual_notes[]                        │
  │     - Create normalized lookup tables:                                   │
  │       └─ settings_index: {setting_ref_id → t2i_base_prompt}              │
  │       └─ characters_index: {character_ref_id → t2i_portrait_prompt}      │
  │                                                                           │
  ├─► Setting Image Generator (T2I — ONCE per location)                      │
  │     - For each unique setting_ref_id in shot_list:                       │
  │       1. Check cache: artifacts/{project_id}/settings/{ref_id}.png       │
  │       2. If missing: call Flux/SD with t2i_base_prompt                   │
  │       3. Save to cache                                                   │
  │     └─► OUTPUT: Cached setting images (e.g., 12 unique locations)        │
  │                                                                           │
  ├─► Character Portrait Generator (T2I — ONCE per character)                │
  │     - For each unique character_ref_id in shot_list:                     │
  │       1. Check cache: artifacts/{project_id}/characters/{ref_id}.png     │
  │       2. If missing: call Flux/SD with t2i_portrait_prompt               │
  │       3. Save to cache                                                   │
  │     └─► OUTPUT: Cached character portraits (e.g., 15 named characters)   │
  │                                                                           │
  └─► State Manifest Writer                                                  │
        - Write visual_bible_manifest.json:                                  │
          {                                                                   │
            "settings": {                                                     │
              "east_la_strip_mall_parking_lot": {                            │
                "image_path": "settings/east_la_strip_mall_parking_lot.png", │
                "prompt": "...",                                              │
                "generated_at": "..."                                         │
              }                                                               │
            },                                                                │
            "characters": {                                                   │
              "rae_calder": {                                                 │
                "image_path": "characters/rae_calder.png",                    │
                "prompt": "...",                                              │
                "generated_at": "..."                                         │
              }                                                               │
            }                                                                 │
          }                                                                   │
        └─► OUTPUT: visual_bible_manifest.json                               │
                                                                              │
                                                                              │
┌─────────────────────────────────────────────────────────────────────────────┼───┐
│ PHASE 4: VIDEO ENGINE (Shot → Video Clip)                                  │   │
│ Location: ❌ MISSING — needs to be built at i2v/ or src/video_engine/      │   │
│ Status: 🚧 NOT IMPLEMENTED                                                 │   │
└─────────────────────────────────────────────────────────────────────────────┼───┘
  │                                                                           │
  │  INPUT: shot_list.json + visual_bible_manifest.json                      │
  │                                                                           │
  ├─► Shot Processor (PER SHOT, 754 iterations for full feature)             │
  │     For each shot in shot_list.scenes[].shots[]:                         │
  │                                                                           │
  │     ┌──────────────────────────────────────────────────────────┐         │
  │     │ STEP A: LOAD SETTING IMAGE                              │         │
  │     ├──────────────────────────────────────────────────────────┤         │
  │     │  setting_img = load_cached(shot.setting_ref_id)         │         │
  │     │  # E.g., "settings/east_la_strip_mall_parking_lot.png"  │         │
  │     └──────────────────────────────────────────────────────────┘         │
  │                                                                           │
  │     ┌──────────────────────────────────────────────────────────┐         │
  │     │ STEP B: INPAINT CHARACTERS INTO SETTING (I2I)           │         │
  │     ├──────────────────────────────────────────────────────────┤         │
  │     │  IF shot.characters_in_frame is not empty:              │         │
  │     │    1. Load character portraits from cache:              │         │
  │     │       char_imgs = [load_cached(ref_id)                  │         │
  │     │                    for ref_id in shot.character_ref_ids] │         │
  │     │                                                           │         │
  │     │    2. Call inpainting model (SD Inpaint / Flux Inpaint):│         │
  │     │       composed_img = inpaint(                            │         │
  │     │         base_image=setting_img,                          │         │
  │     │         character_images=char_imgs,                      │         │
  │     │         edit_prompt=shot.scene_prompt,  ◄────────────────┼────┐     CRITICAL:
  │     │         # E.g., "RAE CALDER (lean, wiry-strong, dark    │    │     scene_prompt
  │     │         #       hair, scar) center frame, facing camera"│    │     tells WHERE to
  │     │         negative_prompt=shot.negative_prompt             │    │     place characters
  │     │       )                                                  │    │     in the setting
  │     │  ELSE:                                                   │    │
  │     │    composed_img = setting_img  # no characters          │    │
  │     └──────────────────────────────────────────────────────────┘    │
  │                                                                     │
  │     ┌────────────────────────────────────────────────────────────┐ │
  │     │ STEP C: GENERATE VIDEO CLIP (I2V)                         │ │
  │     ├────────────────────────────────────────────────────────────┤ │
  │     │  video_clip = call_veo_api(                               │ │
  │     │    init_image=composed_img,  ◄─ from Step B               │ │
  │     │    motion_prompt=shot.video_prompt,  ◄─────────────────────┘─┐
  │     │    # E.g., "camera panning right, slow environmental     │   │  CRITICAL:
  │     │    #       reveal, ambient motion, 8.0s"                 │   │  video_prompt
  │     │    duration=shot.duration_seconds,                       │   │  describes MOTION
  │     │    aspect_ratio=shot.aspect_ratio,                       │   │  not composition
  │     │    negative_prompt=shot.negative_prompt,                 │   │
  │     │    generation_profile=shot.generation_profile            │   │
  │     │  )                                                        │   │
  │     │                                                           │   │
  │     │  # Save to disk:                                         │   │
  │     │  output_path = f"clips/{shot.shot_id}.mp4"               │   │
  │     │  video_clip.save(output_path)                            │   │
  │     └───────────────────────────────────────────────────────────┘   │
  │                                                                     │
  │     ┌────────────────────────────────────────────────────────────┐ │
  │     │ STEP D: AUDIO PIPELINE (PARALLEL)                         │ │
  │     ├────────────────────────────────────────────────────────────┤ │
  │     │  IF shot.dialogue_text:                                   │ │
  │     │    1. Generate TTS:                                       │ │
  │     │       tts_audio = elevenlabs.generate(                    │ │
  │     │         text=shot.dialogue_text,                          │ │
  │     │         voice_id=map_speaker_to_voice(                    │ │
  │     │           shot.dialogue_speaker                           │ │
  │     │         )                                                 │ │
  │     │       )                                                   │ │
  │     │    2. Align lips (optional):                             │ │
  │     │       video_clip = wav2lip(video_clip, tts_audio)        │ │
  │     │                                                           │ │
  │     │  # Generate ambient audio from shot.ambient_description  │ │
  │     │  ambient_audio = generate_ambient(                        │ │
  │     │    shot.ambient_description                              │ │
  │     │    # E.g., "outdoor ambiance, crickets, distant traffic" │ │
  │     │  )                                                        │ │
  │     │                                                           │ │
  │     │  # Mix audio layers:                                     │ │
  │     │  final_audio = mix(                                       │ │
  │     │    dialogue=tts_audio if exists,                         │ │
  │     │    ambient=ambient_audio,                                │ │
  │     │    music=None  # TODO: score engine                      │ │
  │     │  )                                                        │ │
  │     │                                                           │ │
  │     │  # Attach to video:                                      │ │
  │     │  video_clip.set_audio(final_audio)                       │ │
  │     └───────────────────────────────────────────────────────────┘ │
  │                                                                     │
  │     └─► OUTPUT: clips/{shot_id}.mp4 (with audio)                   │
  │                                                                     │
  ├─► Shot Stitcher (Assemble full scenes/sequences)                   │
  │     - For each scene in shot_list:                                 │
  │       1. Load all shot clips: clips/s{scene_num}_*.mp4             │
  │       2. Apply transitions (cut / dissolve / fade)                 │
  │       3. Concatenate with crossfade_duration if specified          │
  │       4. Save: scenes/scene_{scene_num}.mp4                        │
  │     └─► OUTPUT: scenes/ directory with 40 scene files              │
  │                                                                     │
  └─► Final Assembly                                                    │
        - Concatenate all scenes/scene_*.mp4                            │
        - Apply act-level transitions (fade to black between acts)     │
        - Add opening/closing titles (from sp_step_9_marketing.json)   │
        - Export final: output/{project_id}_FINAL.mp4                  │
        └─► OUTPUT: Full feature film (~110 minutes, ~6929s)            │
                                                                        │
                                                                        │
═══════════════════════════════════════════════════════════════════════┘

    FINAL OUTPUT: artifacts/{project_id}_FINAL.mp4
    Duration: ~115 minutes for feature film
    Shots: 754 video clips stitched with transitions
    Audio: Dialogue (TTS) + Ambient + Music (future)
    Quality: Production-ready 16:9 video
```

---

## 2. PER-SHOT EXECUTION FLOW (Runtime Detail)

```
┌────────────────────────────────────────────────────────────────────────┐
│ RUNTIME: Processing Shot s001_003 (Scene 1, Shot 3)                   │
│ "Rae exits the taqueria, slides behind a dumpster, pulls baton"       │
└────────────────────────────────────────────────────────────────────────┘

INPUT DATA (from shot_list.json):
  shot_id: "s001_003"
  setting_ref_id: "east_la_strip_mall_parking_lot"
  character_ref_ids: ["rae_calder"]
  scene_prompt: "RAE CALDER (lean, wiry-strong, dark hair, scar) center frame,
                 figure exits the taqueria, rae slides behind a dumpster, she pulls
                 a telescoping baton, medium shot, subject at medium distance,
                 predatory, working-class, Sodium amber, warm tones"
  video_prompt: "camera slowly pushing in, figure exits the taqueria, rae slides
                 behind a, she pulls a telescoping, 8.2s"
  duration_seconds: 8.2
  aspect_ratio: "16:9"

─────────────────────────────────────────────────────────────────────────

STEP 1: LOAD SETTING IMAGE (CACHED)
  ┌─────────────────────────────────────────────────────────────────┐
  │ Lookup: visual_bible_manifest.json                             │
  │   → settings["east_la_strip_mall_parking_lot"]                 │
  │   → image_path: "settings/east_la_strip_mall_parking_lot.png"  │
  │                                                                 │
  │ IF exists:                                                      │
  │   setting_img = load_image(image_path)  ✅ HIT CACHE           │
  │ ELSE:                                                           │
  │   # Generate ONCE per location (first time only)               │
  │   t2i_prompt = visual_bible.location_designs[...].t2i_base_prompt
  │   # "Photorealistic East Los Angeles strip mall parking lot   │
  │   #  at night, cracked asphalt with oil stains, low stucco    │
  │   #  storefronts (payday lender, phone repair), buzzing neon, │
  │   #  sodium vapor streetlights, deep shadows, heat haze..."   │
  │                                                                 │
  │   setting_img = flux_t2i(                                       │
  │     prompt=t2i_prompt,                                          │
  │     width=1920, height=1080,                                    │
  │     steps=50, guidance=7.5                                      │
  │   )                                                             │
  │   save_to_cache(setting_img, image_path)                       │
  │   update_manifest()                                             │
  └─────────────────────────────────────────────────────────────────┘
  OUTPUT: setting_img (1920x1080 base environment, NO people)

─────────────────────────────────────────────────────────────────────────

STEP 2: LOAD CHARACTER PORTRAIT (CACHED)
  ┌─────────────────────────────────────────────────────────────────┐
  │ For each character_ref_id in shot.character_ref_ids:           │
  │   Lookup: visual_bible_manifest.json                           │
  │     → characters["rae_calder"]                                  │
  │     → image_path: "characters/rae_calder.png"                   │
  │                                                                 │
  │   IF exists:                                                    │
  │     char_img = load_image(image_path)  ✅ HIT CACHE            │
  │   ELSE:                                                         │
  │     # Generate ONCE per character (first appearance)           │
  │     t2i_prompt = visual_bible.character_visual_notes[...].t2i_portrait_prompt
  │     # "Photorealistic character portrait of Rae Calder, lean  │
  │     #  wiry-strong woman with light olive skin, dark brown    │
  │     #  shoulder-length hair in messy knot, faint crescent     │
  │     #  scar under right jaw, neutral expression, standing     │
  │     #  against blank background, 35mm portrait lens..."       │
  │                                                                 │
  │     char_img = flux_t2i(                                        │
  │       prompt=t2i_prompt,                                        │
  │       width=1024, height=1536,  # portrait ratio               │
  │       steps=50, guidance=7.5                                    │
  │     )                                                           │
  │     save_to_cache(char_img, image_path)                        │
  │     update_manifest()                                           │
  └─────────────────────────────────────────────────────────────────┘
  OUTPUT: char_imgs[] (list of character portraits, background removed)

─────────────────────────────────────────────────────────────────────────

STEP 3: INPAINT CHARACTERS INTO SETTING (I2I)
  ┌─────────────────────────────────────────────────────────────────┐
  │ Composite characters into setting using scene_prompt:          │
  │                                                                 │
  │ composed_img = sd_inpaint(                                      │
  │   base_image=setting_img,  # the parking lot                   │
  │   character_images=[rae_calder.png],                            │
  │   edit_prompt=shot.scene_prompt,                                │
  │   # "RAE CALDER (lean, wiry-strong...) center frame,           │
  │   #  figure exits the taqueria, medium shot, subject at        │
  │   #  medium distance, predatory, working-class, Sodium amber"  │
  │   strength=0.6,  # blend factor                                 │
  │   guidance=7.0,                                                 │
  │   negative_prompt=shot.negative_prompt                          │
  │   # "blurry, low quality, cartoon, anime, neon-cyberpunk..."   │
  │ )                                                               │
  │                                                                 │
  │ # Alternative: ControlNet for precise placement                │
  │ composed_img = controlnet_inpaint(                              │
  │   base=setting_img,                                             │
  │   char_masks=generate_masks_from_prompt(scene_prompt),         │
  │   char_imgs=[rae_calder.png],                                   │
  │   prompt=scene_prompt,                                          │
  │   controlnet_model="sd15_inpaint"                               │
  │ )                                                               │
  └─────────────────────────────────────────────────────────────────┘
  OUTPUT: composed_img (setting WITH characters in frame, STILL IMAGE)

─────────────────────────────────────────────────────────────────────────

STEP 4: GENERATE VIDEO CLIP (I2V with Google Veo / Runway)
  ┌─────────────────────────────────────────────────────────────────┐
  │ Send composed_img + motion prompt to I2V API:                  │
  │                                                                 │
  │ video_clip = google_veo_2(                                      │
  │   init_image=composed_img,  # from Step 3                      │
  │   motion_prompt=shot.video_prompt,                              │
  │   # "camera slowly pushing in, figure exits the taqueria,      │
  │   #  rae slides behind a, she pulls a telescoping, 8.2s"       │
  │   #  ⚠️ BUG: this is garbage text, motion extraction broken    │
  │   duration_seconds=8.2,                                         │
  │   aspect_ratio="16:9",                                          │
  │   fps=24,                                                       │
  │   motion_strength=0.7,  # how much motion vs static            │
  │   quality="production"                                          │
  │ )                                                               │
  │                                                                 │
  │ # Alternative APIs:                                             │
  │ # - runway_gen3(init_image, text_prompt, duration)             │
  │ # - pika_labs_i2v(init_image, motion_prompt, duration)         │
  │ # - kling_ai_i2v(init_image, motion_prompt, duration)          │
  │ # - luma_dream_machine(init_image, prompt, duration)           │
  └─────────────────────────────────────────────────────────────────┘
  OUTPUT: video_clip (8.2s silent MP4, 1920x1080@24fps)

─────────────────────────────────────────────────────────────────────────

STEP 5: GENERATE & MIX AUDIO (PARALLEL)
  ┌─────────────────────────────────────────────────────────────────┐
  │ A) Dialogue (IF shot.dialogue_text exists):                    │
  │    speaker = shot.dialogue_speaker  # "Rae"                    │
  │    voice_id = character_voice_map[speaker]  # from manifest   │
  │    tts_audio = elevenlabs.generate(                            │
  │      text=shot.dialogue_text,                                  │
  │      voice=voice_id,                                            │
  │      model="eleven_turbo_v2"                                    │
  │    )                                                            │
  │                                                                 │
  │ B) Ambient audio:                                              │
  │    ambient_prompt = shot.ambient_description                   │
  │    # "outdoor ambiance, crickets, distant traffic, warm       │
  │    #  plastic smell from overheating phone chargers"          │
  │    ambient_audio = audiocraft_gen(                             │
  │      prompt=ambient_prompt,                                    │
  │      duration=8.2,                                              │
  │      model="audiogen-medium"                                    │
  │    )                                                            │
  │                                                                 │
  │ C) Mix layers:                                                 │
  │    final_audio = mix_audio(                                    │
  │      dialogue=tts_audio if exists else None,                  │
  │      ambient=ambient_audio,                                    │
  │      music=None,  # TODO: score engine                         │
  │      levels={"dialogue": 0.8, "ambient": 0.3}                  │
  │    )                                                            │
  │                                                                 │
  │ D) Attach to video:                                            │
  │    video_clip.set_audio(final_audio)                           │
  └─────────────────────────────────────────────────────────────────┘
  OUTPUT: video_clip WITH AUDIO (8.2s MP4 with dialogue + ambient)

─────────────────────────────────────────────────────────────────────────

STEP 6: SAVE CLIP TO DISK
  ┌─────────────────────────────────────────────────────────────────┐
  │ output_path = f"artifacts/{project_id}/clips/{shot.shot_id}.mp4"
  │ # "artifacts/sp_rae_blackout_20260214_100612/clips/s001_003.mp4"
  │                                                                 │
  │ video_clip.save(                                                │
  │   output_path,                                                  │
  │   codec="h264",                                                 │
  │   bitrate="8M",                                                 │
  │   audio_codec="aac",                                            │
  │   audio_bitrate="192k"                                          │
  │ )                                                               │
  │                                                                 │
  │ # Update shot manifest:                                        │
  │ shot_manifest.json:                                             │
  │   {                                                             │
  │     "s001_003": {                                               │
  │       "status": "completed",                                    │
  │       "clip_path": "clips/s001_003.mp4",                        │
  │       "duration": 8.2,                                          │
  │       "generated_at": "2026-02-16T10:34:22Z"                    │
  │     }                                                            │
  │   }                                                             │
  └─────────────────────────────────────────────────────────────────┘
  OUTPUT: clips/s001_003.mp4 SAVED ✅

═══════════════════════════════════════════════════════════════════════

REPEAT for all 754 shots → 754 MP4 clips in clips/ directory

THEN: Scene Stitcher concatenates clips with transitions
THEN: Final Assembly produces output/{project_id}_FINAL.mp4
```

---

## 3. COMPREHENSIVE GAP ANALYSIS

### 3.1 WHAT EXISTS TODAY ✅

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| **Screenplay Engine** | ✅ COMPLETE | `src/screenplay_engine/` | 9 steps, 970 tests passing |
| **World Bible** | ✅ COMPLETE | `src/screenplay_engine/pipeline/steps/step_3b_world_bible.py` | Arena, geography, culture, economy |
| **Full Cast (Layered)** | ✅ COMPLETE | `src/screenplay_engine/pipeline/steps/step_3c_full_cast.py` | 3 tiers, layered API calls |
| **Visual Bible** | ✅ COMPLETE | `src/screenplay_engine/pipeline/steps/step_5b_visual_bible.py` | Style bible, color script, location designs, character portraits |
| **Shot Engine** | ✅ COMPLETE | `src/shot_engine/` | 6-step pipeline (V1-V6) |
| - V1: Scene Decomposition | ✅ WORKING | `src/shot_engine/pipeline/steps/step_v1_decomposition.py` | Parses scenes into shots |
| - V2: Shot Type Assignment | ✅ WORKING | `src/shot_engine/pipeline/steps/step_v2_shot_types.py` | Maps trigger → shot type |
| - V3: Camera Behavior | ✅ WORKING | `src/shot_engine/pipeline/steps/step_v3_camera.py` | Camera movement, lens, height |
| - V4: Duration & Pacing | ✅ WORKING | `src/shot_engine/pipeline/steps/step_v4_pacing.py` | Timing per shot |
| - V5: Transitions | ✅ WORKING | `src/shot_engine/pipeline/steps/step_v5_transitions.py` | Cut/dissolve/fade rules |
| - V6: Prompt Generation | ⚠️ BUGGY | `src/shot_engine/pipeline/steps/step_v6_prompts.py` | Generates prompts but has bugs |
| **Shot List Output** | ✅ COMPLETE | `artifacts/{project_id}/shot_list.json` | 754 shots with metadata |

### 3.2 WHAT IS BROKEN/NEEDS FIXING 🔧

#### 3.2.1 V6 Prompt Generation Bugs (CRITICAL)

**BUG 1: Garbage video_prompt (motion extraction failure)**

**Evidence:**
```json
{
  "shot_id": "s001_005",
  "video_prompt": "camera tracking movement, figure skip turns, they slam into the, 3.6s"
}
```

**Root Cause:**
In `step_v6_prompts.py`, the `_extract_motion()` function uses regex to extract motion verbs but fails when:
- Sentence fragments are passed instead of full sentences
- Context is incomplete (e.g., "skip turns" is a character name + verb, not a motion phrase)
- The motion phrase includes incomplete objects ("slam into the" vs "slam into the dumpster")

**Impact:** 2/754 shots (0.3%) have malformed video prompts
**Severity:** HIGH — Veo API will produce nonsense motion from these prompts

**Fix Required:**
1. Improve sentence boundary detection in `_extract_motion()`
2. Add context window expansion (grab full sentence, not just verb window)
3. Add validation: reject prompts with trailing prepositions ("into the", "from the")
4. Fallback: if extraction fails, use trigger-based default motion

---

**BUG 2: characters_in_frame frequently empty when characters ARE in shot**

**Evidence:**
- 296/754 shots (39%) have empty `characters_in_frame` despite character names in `content`
- Example: `content: "Rae shoves him behind the dumpster"` → `characters_in_frame: []`

**Root Cause:**
In `step_v1_decomposition.py`, `_extract_characters()` uses word-boundary regex but fails when:
- Character names appear in possessive form ("Rae's" not matching "Rae")
- Character names appear in lowercase action text
- Known character list is incomplete (missing tier 2/3 characters)

**Impact:** 296 shots missing character metadata
**Severity:** CRITICAL — Shots won't trigger character inpainting in video engine

**Fix Required:**
1. Build complete character name list from Step 3 + 3c artifacts
2. Add fuzzy matching (possessive, lowercase, partial name)
3. Add character detection from dialogue_speaker field (if present, add to frame)
4. Validate: if `dialogue_speaker` exists, they MUST be in `characters_in_frame`

---

**BUG 3: "speaking, speaking" duplication in dialogue shots**

**Evidence:** Not found in sample but mentioned in user request

**Root Cause (hypothetical):**
Likely in `_build_blocking_description()` or scene_prompt generation where dialogue trigger adds "speaking" and then video_prompt adds it again.

**Fix Required:**
1. Grep for duplication pattern in `step_v6_prompts.py`
2. Deduplicate keywords in prompt assembly
3. Add unit test to catch duplicate terms

---

### 3.3 WHAT IS MISSING (TO BE BUILT) 🚧

#### 3.3.1 Visual Bible Asset Manager

**Status:** ❌ NOT IMPLEMENTED
**Priority:** P0 (BLOCKING)
**Estimated Effort:** 3-5 days

**Required Components:**

1. **Asset Index Builder**
   - Input: `sp_step_5b_visual_bible.json`
   - Output: Normalized lookup tables
   - Functions:
     - `build_settings_index()` → `{setting_ref_id: {t2i_prompt, mood, colors}}`
     - `build_characters_index()` → `{char_ref_id: {t2i_portrait_prompt, physical_appearance}}`

2. **Setting Image Generator (T2I)**
   - API: Flux Pro / Stable Diffusion XL
   - Cache: `artifacts/{project_id}/settings/{ref_id}.png`
   - Run ONCE per unique location (e.g., 12 locations for 40-scene screenplay)
   - Estimated cost: $0.05/image × 12 = $0.60 per project

3. **Character Portrait Generator (T2I)**
   - API: Flux Pro / Stable Diffusion XL
   - Cache: `artifacts/{project_id}/characters/{ref_id}.png`
   - Run ONCE per unique character (e.g., 15 named characters)
   - Estimated cost: $0.05/image × 15 = $0.75 per project
   - Special: Remove background for inpainting (rembg library)

4. **Manifest Writer**
   - Output: `visual_bible_manifest.json`
   - Schema:
     ```json
     {
       "settings": {
         "setting_ref_id": {
           "image_path": "settings/{ref_id}.png",
           "prompt": "...",
           "generated_at": "...",
           "width": 1920,
           "height": 1080
         }
       },
       "characters": {
         "char_ref_id": {
           "image_path": "characters/{ref_id}.png",
           "prompt": "...",
           "generated_at": "...",
           "background_removed": true
         }
       }
     }
     ```

**Files to Create:**
- `src/visual_bible_engine/asset_manager.py`
- `src/visual_bible_engine/t2i_client.py` (Flux/SD API wrapper)
- `src/visual_bible_engine/manifest.py` (read/write manifest)

---

#### 3.3.2 Video Engine (MOST CRITICAL)

**Status:** ❌ NOT IMPLEMENTED
**Priority:** P0 (BLOCKING EVERYTHING)
**Estimated Effort:** 2-3 weeks

**Required Components:**

1. **Shot Processor**
   - Input: `shot_list.json` + `visual_bible_manifest.json`
   - Output: 754 MP4 clips in `artifacts/{project_id}/clips/`
   - Per-shot pipeline:
     1. Load cached setting image
     2. Load cached character portrait(s)
     3. Inpaint characters into setting (I2I)
     4. Generate video from composed image (I2V)
     5. Generate dialogue audio (TTS)
     6. Generate ambient audio
     7. Mix audio layers
     8. Attach audio to video
     9. Save clip to disk

2. **Image Inpainting Module (I2I)**
   - API Options:
     - Stable Diffusion Inpaint (local)
     - Flux Inpaint (API, better quality)
     - ControlNet (precise character placement)
   - Input: setting image + character images + scene_prompt
   - Output: Composed still frame (characters in setting)
   - Estimated time: 3-5s per shot (local GPU)

3. **Video Generation Module (I2V)**
   - API Options (PICK ONE):
     - **Google Veo 2** (best quality, expensive, slow)
     - **Runway Gen-3** (good quality, moderate cost)
     - **Pika Labs** (fast, lower quality)
     - **Kling AI** (good for Asian markets)
     - **Luma Dream Machine** (free tier available)
   - Input: composed image + video_prompt + duration
   - Output: Silent video clip (MP4, 1920x1080, 24fps)
   - Estimated time: 30-120s per shot (API-dependent)
   - Estimated cost: $0.10-$0.50 per shot → $75-$377 per feature film

4. **Audio Pipeline**
   - **Dialogue TTS:**
     - API: ElevenLabs / Azure TTS / Google TTS
     - Character voice mapping (from visual bible or manual config)
     - Lip sync (optional): Wav2Lip model
   - **Ambient Audio:**
     - API: AudioCraft (Meta) / Stable Audio
     - Input: `shot.ambient_description`
   - **Audio Mixer:**
     - Library: pydub / moviepy
     - Layer dialogue + ambient + music (future)
     - Export: 192kbps AAC

5. **Shot Stitcher**
   - Library: moviepy / ffmpeg
   - Input: All clips for a scene
   - Apply transitions (cut/dissolve/fade)
   - Output: Scene-level MP4 files

6. **Final Assembly**
   - Concatenate all scenes
   - Add act transitions (fade to black)
   - Add opening/closing titles (from Step 9 marketing)
   - Export final feature film MP4

**Files to Create:**
- `src/video_engine/shot_processor.py`
- `src/video_engine/i2i_inpaint.py` (SD/Flux inpainting wrapper)
- `src/video_engine/i2v_client.py` (Veo/Runway API wrapper)
- `src/video_engine/audio_pipeline.py` (TTS + ambient + mixing)
- `src/video_engine/stitcher.py` (clip concatenation + transitions)
- `src/video_engine/orchestrator.py` (main execution loop)

**API Keys Required:**
- Flux API key (T2I + Inpaint)
- Google Veo API key (I2V) OR Runway OR Pika
- ElevenLabs API key (TTS)
- AudioCraft (local) OR Stable Audio API

---

#### 3.3.3 Audio Engine (Separate Pipeline)

**Status:** ❌ NOT IMPLEMENTED
**Priority:** P1 (can run separately after video)
**Estimated Effort:** 1 week

**Components:**
1. **Character Voice Mapping**
   - Map `dialogue_speaker` → ElevenLabs voice_id
   - Store in config: `voice_map.json`

2. **TTS Generator**
   - API: ElevenLabs (best quality)
   - Fallback: Azure TTS, Google TTS

3. **Ambient Audio Generator**
   - Use AudioCraft (local, free)
   - OR Stable Audio API

4. **Music Score Engine (FUTURE)**
   - AI music generation for scenes
   - Beat-aligned transitions

5. **Lip Sync (OPTIONAL)**
   - Wav2Lip model for dialogue shots
   - Requires face detection in video

---

#### 3.3.4 Asset Cache System

**Status:** ❌ NOT IMPLEMENTED
**Priority:** P0 (CRITICAL FOR COST SAVINGS)
**Estimated Effort:** 2 days

**Why Critical:**
Without caching, regenerating setting images and character portraits for every shot would cost:
- 754 shots × $0.05/image = $37.70 (vs $1.35 with caching)
- Processing time: 754 shots × 5s = 63 minutes (vs 1 minute with caching)

**Components:**
1. **Cache Storage**
   - Directory: `artifacts/{project_id}/cache/`
   - Subdirs: `settings/`, `characters/`, `clips/`

2. **Cache Lookup**
   - Before generating any image, check cache
   - Use normalized ref_id as key

3. **Cache Invalidation**
   - If visual bible changes, mark settings/characters as stale
   - If screenplay changes, mark clips as stale

4. **Manifest Tracking**
   - `visual_bible_manifest.json` tracks all cached assets
   - `shot_manifest.json` tracks all generated clips

**Files to Create:**
- `src/cache/cache_manager.py`
- `src/cache/manifest_io.py`

---

#### 3.3.5 Clip Stitcher & Final Assembly

**Status:** ❌ NOT IMPLEMENTED
**Priority:** P1 (needed for full output)
**Estimated Effort:** 3 days

**Components:**

1. **Scene Stitcher**
   - Input: All clips for a scene (e.g., 18 clips for Scene 1)
   - Apply transitions:
     - `cut`: instant (no blend)
     - `dissolve`: crossfade over `crossfade_duration`
     - `fade_black`: fade out → fade in
   - Output: `scenes/scene_001.mp4`

2. **Act Transitions**
   - Between acts: 2-second fade to black

3. **Opening/Closing Titles**
   - Pull from `sp_step_9_marketing.json`:
     - `title_sequence` (opening)
     - `poster_tagline` (closing card)
   - Generate title cards with Pillow/moviepy
   - Insert at start/end of film

4. **Final Export**
   - Concatenate: titles + all scenes + credits
   - Export: `output/{project_id}_FINAL.mp4`
   - Codec: H.264, 8Mbps, 1920x1080, 24fps
   - Audio: AAC, 192kbps, stereo

**Files to Create:**
- `src/video_engine/scene_stitcher.py`
- `src/video_engine/title_generator.py`
- `src/video_engine/final_assembly.py`

---

### 3.4 ESTIMATED COSTS (Per Feature Film)

| Item | Unit Cost | Quantity | Total |
|------|-----------|----------|-------|
| **T2I (Settings)** | $0.05/image | 12 unique locations | $0.60 |
| **T2I (Characters)** | $0.05/image | 15 characters | $0.75 |
| **I2V (Veo 2)** | $0.30/shot | 754 shots | $226.20 |
| **TTS (ElevenLabs)** | $0.001/char | ~50K characters | $50.00 |
| **Ambient Audio** | Local (free) | - | $0.00 |
| **TOTAL (Veo)** | | | **$277.55** |
| | | | |
| **I2V (Runway Gen-3)** | $0.10/shot | 754 shots | $75.40 |
| **TOTAL (Runway)** | | | **$126.75** |
| | | | |
| **I2V (Pika Labs)** | $0.05/shot | 754 shots | $37.70 |
| **TOTAL (Pika)** | | | **$89.05** |

**Recommended:** Start with Pika Labs for prototyping ($89/film), upgrade to Runway ($127/film) for production quality.

---

### 3.5 ESTIMATED PROCESSING TIME (Per Feature Film)

| Phase | Time per Shot | Total Shots | Total Time |
|-------|--------------|-------------|------------|
| **Asset Generation** (settings + chars) | 5s | 27 images | **2.25 min** |
| **I2I Inpainting** (local GPU) | 4s | 754 shots | **50 min** |
| **I2V Generation** (Veo API) | 60s | 754 shots | **12.6 hours** |
| **I2V Generation** (Runway API) | 30s | 754 shots | **6.3 hours** |
| **I2V Generation** (Pika API) | 15s | 754 shots | **3.2 hours** |
| **Audio Generation** (TTS + ambient) | 3s | 754 shots | **38 min** |
| **Audio Mixing** | 1s | 754 shots | **13 min** |
| **Clip Stitching** | 0.5s | 40 scenes | **20 sec** |
| **Final Assembly** | - | 1 film | **2 min** |
| | | | |
| **TOTAL (Pika, parallel)** | | | **~5 hours** |
| **TOTAL (Runway, parallel)** | | | **~8 hours** |
| **TOTAL (Veo, parallel)** | | | **~14 hours** |

**Note:** With API parallelization (10 concurrent requests), total time reduces by 50-70%.

---

### 3.6 PRIORITY ORDER (What to Build First)

1. **P0 (BLOCKING):**
   - Fix V6 bugs (motion extraction, character detection) — **1 day**
   - Build Visual Bible Asset Manager — **3 days**
   - Build Video Engine core (shot processor + I2I + I2V) — **1 week**

2. **P1 (HIGH):**
   - Build Audio Pipeline (TTS + ambient + mixing) — **3 days**
   - Build Cache System — **2 days**
   - Build Scene Stitcher — **2 days**

3. **P2 (MEDIUM):**
   - Build Final Assembly (titles + export) — **2 days**
   - Add Lip Sync (Wav2Lip) — **3 days**

4. **P3 (LOW):**
   - Build Music Score Engine — **1 week**
   - Add Veo API fallback logic — **1 day**

---

### 3.7 RECOMMENDED TECH STACK

```python
# Core Dependencies
{
  "video_generation": "google-veo-api OR runwayml OR pika-labs",
  "image_generation": "flux-pro OR stable-diffusion-xl",
  "inpainting": "controlnet OR flux-inpaint",
  "tts": "elevenlabs OR azure-tts",
  "audio_generation": "audiocraft (local) OR stable-audio",
  "video_editing": "moviepy OR ffmpeg-python",
  "audio_mixing": "pydub",
  "background_removal": "rembg",
  "cache": "filesystem + JSON manifest",
  "parallelization": "concurrent.futures OR asyncio"
}
```

---

## 4. CRITICAL ISSUES SUMMARY

### 4.1 Shot Engine Bugs (MUST FIX)

1. **Video prompt garbage (2/754 shots):**
   - "figure skip turns, they slam into the" → nonsense
   - Fix: Improve `_extract_motion()` sentence parsing

2. **Missing character detection (296/754 shots):**
   - Empty `characters_in_frame` despite characters in `content`
   - Fix: Improve `_extract_characters()` fuzzy matching + add from `dialogue_speaker`

3. **Speaking duplication (unknown count):**
   - "speaking, speaking" in prompts
   - Fix: Deduplicate keywords in prompt assembly

### 4.2 Missing Components (MUST BUILD)

1. **Visual Bible Asset Manager:**
   - No system to generate/cache setting images
   - No system to generate/cache character portraits

2. **Video Engine:**
   - No I2I inpainting module
   - No I2V API client
   - No shot processor loop

3. **Audio Pipeline:**
   - No TTS integration
   - No ambient audio generation
   - No audio mixing

4. **Asset Cache:**
   - No caching layer (will waste money regenerating images)

5. **Stitcher:**
   - No scene assembly
   - No final film export

---

## 5. NEXT STEPS (Actionable Plan)

### Week 1: Fix Shot Engine + Build Asset Manager
- [ ] Day 1: Fix V6 motion extraction bug
- [ ] Day 2: Fix V6 character detection bug
- [ ] Day 3-5: Build Visual Bible Asset Manager (T2I settings + characters)

### Week 2: Build Video Engine Core
- [ ] Day 1-2: Build I2I inpainting module (SD/Flux)
- [ ] Day 3-4: Build I2V API client (Pika Labs for prototyping)
- [ ] Day 5: Build shot processor loop (integrate I2I + I2V)

### Week 3: Audio + Stitching
- [ ] Day 1-2: Build TTS pipeline (ElevenLabs)
- [ ] Day 3: Build ambient audio generation (AudioCraft)
- [ ] Day 4: Build audio mixer
- [ ] Day 5: Build scene stitcher + final assembly

### Week 4: Testing + Optimization
- [ ] Day 1-2: End-to-end test (generate 5-minute short film)
- [ ] Day 3: Optimize caching + parallelization
- [ ] Day 4: Cost/quality analysis (Pika vs Runway vs Veo)
- [ ] Day 5: Documentation + deployment guide

---

## 6. ARCHITECTURE NOTES

### 6.1 Setting-Per-Location Architecture

**Key Insight from v12.0.0:**
The visual bible now generates ONE setting design per UNIQUE LOCATION (not per scene). This is critical for:

1. **Cost savings:** 12 setting images instead of 40 (one per scene)
2. **Continuity:** Same parking lot image used across 5 scenes
3. **Cache efficiency:** Setting images reused across multiple shots

**How it works:**
- `location_designs[]` in visual bible has `time_variants` dict
- Shot engine normalizes slugline → `setting_ref_id`
- Visual Bible Asset Manager generates base image ONCE per location
- Video Engine applies time-of-day variants via I2I editing if needed

### 6.2 Character State Tracking

**Challenge:** Characters change wardrobe, injuries, etc. across acts.

**Solution (Future):**
- Visual bible `character_visual_notes[]` includes `wardrobe_evolution`
- Asset Manager generates MULTIPLE portraits per character:
  - `rae_calder_act1.png` (initial wardrobe)
  - `rae_calder_act2.png` (bloodied, torn jacket)
  - `rae_calder_act3.png` (cleaned up, different clothes)
- Shot processor selects variant based on `shot.beat` → act mapping

### 6.3 Parallelization Strategy

**Single-threaded time:** 14 hours for Veo
**10-parallel time:** 1.4 hours (10x speedup)

**Implementation:**
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [
        executor.submit(process_shot, shot)
        for shot in shot_list.all_shots()
    ]
    results = [f.result() for f in futures]
```

**Note:** API rate limits may cap parallelization (e.g., Veo: 5 concurrent)

---

## END OF DOCUMENT

**Generated:** 2026-02-16
**Version:** 1.0.0
**Next Review:** After V6 bugs fixed + Asset Manager built
