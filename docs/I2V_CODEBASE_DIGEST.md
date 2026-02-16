# I2V Codebase Architecture Digest

**Generated**: 2026-02-16
**Purpose**: Complete architectural reference for integrating Snowflake screenplay engine with i2v video generation platform

---

## 1. HIGH-LEVEL ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────┐
│                         I2V ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐      ┌─────────────────┐      ┌──────────────┐  │
│  │   Frontend   │◄────►│  FastAPI        │◄────►│  External    │  │
│  │   (React)    │      │  Backend        │      │  APIs        │  │
│  └──────────────┘      │  (Python)       │      └──────────────┘  │
│                        └─────────────────┘              │          │
│                                │                        │          │
│                                ▼                        │          │
│                        ┌─────────────────┐              │          │
│                        │  Database       │              │          │
│                        │  (SQLite)       │              │          │
│                        └─────────────────┘              │          │
│                                                          │          │
│  External API Providers:                                │          │
│  • Fal.ai (I2V: Wan, Kling, Veo, Sora, Luma)           │          │
│  • Fal.ai (T2I: FLUX, Kling, Ideogram, Nano-Banana)    │          │
│  • Vast.ai (Self-hosted SwarmUI for I2V)               │          │
│  • ElevenLabs (TTS voice synthesis)                     │          │
│  • Hedra (Lip sync)                                     │          │
│  • Instagram API (Publishing)                           │          │
│  • Twitter API (Publishing)                             │          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. BACKEND SERVICE MAP

### Core Services (`app/services/`)

#### **2.1 Generation Services**

##### **generation_service.py**
- **Purpose**: Unified dispatcher for image/video generation
- **Key Functions**:
  - `generate_image(image_url, prompt, model, ...)` → List[str] (image URLs)
  - `generate_video(image_url, prompt, model, ...)` → str (video URL)
  - `process_video_job(job_id)` → background task processor
- **Model Routing**:
  - `vastai-*` models → SwarmUI on Vast.ai
  - All other models → Fal.ai
- **Post-processing**: Supports caption overlay + spoofing (crop/scale/metadata)
- **Dependencies**: fal_client, image_client, vastai_orchestrator, post_process_video

##### **pipeline_executor.py**
- **Purpose**: Execute multi-step generation pipelines (text→image→video chains)
- **Step Types Supported**:
  - `prompt_enhance`: Enhance prompt with AI
  - `i2i`: Image-to-image transformation (inpainting/compositing)
  - `i2v`: Image-to-video animation
  - `face_swap`: Swap faces in images
  - `tts`: Text-to-speech audio generation
  - `lipsync`: Apply lip sync to video
  - `audio_bed`: Overlay background music
  - `video_concat`: Stitch multiple videos together
- **Error Handling**: Retry logic, orphan detection, cooldown management
- **Database**: Creates Pipeline and PipelineStep records for tracking

##### **vastai_orchestrator.py**
- **Purpose**: Manage self-hosted SwarmUI instances on Vast.ai for I2V
- **Key Methods**:
  - `generation_fn(item, model, resolution, ...)` → video URL
  - Instance pooling, health checks, retry logic
- **Supported Models**: vastai-wan22-remix-i2v, vastai-wan22-t2v, vastai-cogvideox, vastai-svd
- **Features**: Progress tracking (0-100%), caption overlay, spoofing

#### **2.2 Media Processing Services**

##### **video_concat.py** (VideoConcatService)
- **Purpose**: Stitch multiple video clips into one final video
- **Methods**:
  - `concatenate_videos(video_urls, output_path)` → str (final video path)
- **Uses**: FFmpeg for video assembly

##### **audio_bed_service.py** (AudioBedService)
- **Purpose**: Overlay background music on videos
- **Methods**:
  - `extract_random_clip(song_path, target_duration)` → str (clip path)
  - `overlay_audio(video_path, audio_path, ...)` → str (output path)
- **Features**: Fade in/out, volume control, audio mixing
- **Scenarios**: Silent video, video with audio (mix), replace audio

##### **lipsync_service.py**
- **Purpose**: Apply lip sync to video using Hedra API
- **Methods**:
  - `apply_lipsync(video_url, audio_url)` → job_id
  - `get_lipsync_status(job_id)` → status + result URL
- **Provider**: Hedra API

##### **tts_service.py**
- **Purpose**: Generate speech audio from text
- **Methods**:
  - `generate_speech(text, voice_id, model)` → audio_url
- **Provider**: ElevenLabs API
- **Voices**: Configurable voice IDs

##### **frame_extractor.py** (FrameExtractorService)
- **Purpose**: Extract still frames from videos
- **Methods**:
  - `extract_frame(video_url, timestamp)` → image_url
- **Uses**: FFmpeg

##### **slideshow_generator.py**
- **Purpose**: Create slideshow videos from image sequences
- **Methods**:
  - `generate_slideshow(images, transitions, music)` → video_url
- **Uses**: FFmpeg with ken burns effects, transitions

#### **2.3 Content Generation Services**

##### **caption_generator.py**
- **Purpose**: Generate on-screen captions for videos
- **Methods**:
  - `generate_captions(api_key, count, style, dm_bait_percent)` → List[str]
- **Styles**: cosplay, cottagecore, gym, male_thirst, etc.
- **Provider**: Claude (Anthropic)

##### **post_caption_generator.py**
- **Purpose**: Generate Instagram/TikTok post captions (text below video, NOT on-screen)
- **Methods**:
  - `generate_feral_post_caption(video_url, style)` → dict (caption, OCR text)
- **Features**: Extracts frame, OCR on-screen text, generates complementary caption
- **Styles**: auto, funny, serious, relatable, flirty, mysterious

##### **prompt_enhancer.py**
- **Purpose**: Enhance user prompts for better image/video generation
- **Methods**:
  - `enhance_prompt(prompt, style, ...)` → enhanced_prompt
- **Provider**: Claude (Anthropic)

##### **prompt_generator.py**
- **Purpose**: Generate prompts for image/video creation
- **Methods**:
  - `generate_prompts(count, style, ...)` → List[str]
  - `generate_carousel_prompts(num_images, ...)` → List[str]
  - `generate_i2v_prompts(count, motion_type, ...)` → List[str]
  - `generate_chain_prompts(num_segments, ...)` → List[str]
- **Provider**: Claude (Anthropic)

##### **i2v_prompt_generator.py**
- **Purpose**: Generate I2V motion prompts
- **Methods**:
  - `generate_i2v_prompts(count, motion_type, ...)` → List[dict]
- **Motion Types**: camera_motion, character_motion, environmental, transitions

##### **nsfw_prompt_generator.py**
- **Purpose**: Generate NSFW content prompts
- **Methods**:
  - `generate_nsfw_prompts(count, style, ...)` → List[str]
  - `generate_nsfw_caption(...)` → str

##### **scene_structurer.py** (SceneStructurerService)
- **Purpose**: Structure prompts into scenes with camera movements
- **Methods**:
  - `structure_scene(prompt)` → dict (scenes, shots, camera moves)
- **Provider**: Claude (Anthropic)

#### **2.4 Social Media Services**

##### **instagram_scheduler.py**
- **Purpose**: Schedule Instagram posts for future publishing
- **Methods**:
  - `schedule_post(media_url, caption, scheduled_time)` → post_id
- **Database**: ScheduledPost table

##### **twitter_autopilot.py**
- **Purpose**: Automated Twitter posting based on content library
- **Methods**:
  - `generate_text_tweet(config)` → tweet_text
  - `get_random_media(step_type)` → media_url
- **Features**: Trend monitoring, style scraping, auto-scheduling

##### **twitter_client.py** (TwitterClient)
- **Purpose**: Twitter API integration
- **Methods**:
  - `post_tweet(text, media_urls)` → tweet_id
  - `create_thread(tweets)` → thread_id
- **OAuth**: OAuth 1.0a and OAuth 2.0 support

#### **2.5 Utility Services**

##### **r2_cache.py**
- **Purpose**: Cache media files to Cloudflare R2 storage
- **Methods**:
  - `cache_video(original_url, video_bytes)` → cached_url
  - `cache_image(original_url, image_bytes)` → cached_url
- **Provider**: Cloudflare R2

##### **thumbnail.py**
- **Purpose**: Generate video thumbnails
- **Methods**:
  - `generate_thumbnail(video_url)` → thumbnail_url
  - `generate_thumbnails_batch(video_urls)` → List[thumbnail_url]
- **Uses**: FFmpeg to extract middle frame

##### **cooldown_manager.py**
- **Purpose**: Exponential backoff for failed jobs
- **Classes**: ModelCooldownManager, JobCooldownManager
- **Methods**:
  - `should_process(entity_id)` → bool
  - `record_failure(entity_id, error)` → CooldownState
  - `record_success(entity_id)` → CooldownState
- **Schedule**: 5s, 15s, 1m, 5m, 15m, 1h, 6h, 24h

##### **error_classifier.py**
- **Purpose**: Classify errors for intelligent retry decisions
- **Error Types**: NETWORK, RATE_LIMIT, INVALID_INPUT, TRANSIENT, PERMANENT, UNKNOWN
- **Methods**:
  - `classify(error)` → ClassifiedError (with retry params)

##### **retry_manager.py**
- **Purpose**: Retry logic with exponential backoff
- **Methods**:
  - `retry_with_backoff(fn, max_retries, ...)` → result

##### **cost_calculator.py**
- **Purpose**: Estimate credit costs for jobs
- **Pricing Table**: i2i, i2v, carousel, pipeline, tts, lipsync, face_swap
- **Methods**:
  - `calculate_job_cost(output_type, quantity, options)` → int (credits)

##### **credits.py**
- **Purpose**: User credit management
- **Methods**:
  - `get_balance(db, user_id)` → int
  - `add_credits(db, user_id, amount, ...)` → CreditTransaction
  - `deduct_credits(db, user_id, amount, ...)` → CreditTransaction

---

## 3. ROUTER MAP (API Endpoints)

### Core Generation Routers

#### **3.1 `/api/pipelines` (pipelines.py)**
Multi-step generation pipelines. Primary router for complex workflows.

**Endpoints**:
- `POST /api/pipelines/submit` → Create pipeline with steps
  - **Request**: Pipeline config (steps: prompt_enhance, i2i, i2v, face_swap, tts, lipsync, audio_bed, video_concat)
  - **Response**: pipeline_id
- `GET /api/pipelines/{pipeline_id}` → Get pipeline status
- `GET /api/pipelines/{pipeline_id}/steps` → Get all steps
- `POST /api/pipelines/{pipeline_id}/retry` → Retry failed pipeline
- `DELETE /api/pipelines/{pipeline_id}` → Cancel pipeline

**Step Types**:
- `i2i`: Image-to-image (model, prompt, image_url)
- `i2v`: Image-to-video (model, prompt, image_url, resolution, duration_sec)
- `face_swap`: Face swap (face_url, target_url, gender)
- `tts`: Text-to-speech (text, voice_id, model)
- `lipsync`: Lip sync (video_url, audio_url)
- `audio_bed`: Background music (video_url, song_url, mode)
- `video_concat`: Stitch videos (video_urls)
- `prompt_enhance`: Enhance prompt (prompt, style)

#### **3.2 `/api/flow` (flow_generation.py)**
Simplified single-video generation (wrapper around pipelines).

**Endpoints**:
- `POST /api/flow/generate` → Generate single I2V video
  - **Request**: prompt, image_url, model, resolution, duration_sec
  - **Response**: job_id (202 Accepted)
- `POST /api/flow/batch` → Generate multiple videos in parallel
  - **Request**: List of jobs
  - **Response**: batch_id, pipeline_id
- `GET /api/flow/jobs/{job_id}` → Get job status
- `GET /api/flow/jobs` → List all jobs
- `DELETE /api/flow/jobs` → Clear completed jobs
- `POST /api/flow/refresh-urls/{pipeline_id}` → Refresh expired video URLs

#### **3.3 `/api/video-chain` (video_chain.py)**
Multi-segment video chains (I2V → I2V → I2V...).

**Endpoints**:
- `POST /api/video-chain/chain` → Create video chain
  - **Request**: segments (each with prompt, init_image_url, model, duration)
  - **Response**: chain_id (201 Created)
- `GET /api/video-chain/chain/{chain_id}` → Get chain status
- `GET /api/video-chain/chain/{chain_id}/video` → Download final stitched video
- `POST /api/video-chain/chain/{chain_id}/resume` → Resume failed chain
- `DELETE /api/video-chain/chain/{chain_id}` → Cancel chain
- `GET /api/video-chain/chains` → List all chains
- `GET /api/video-chain/chain/{chain_id}/segments` → Get all segments

#### **3.4 `/api/simple-chain` (simple_chain.py)**
Simplified T2I → I2V workflow.

**Endpoints**:
- `POST /api/simple-chain/submit` → Submit T2I + I2V job
  - **Request**: i2i_prompt, i2i_model, i2v_prompt, i2v_model, resolution
  - **Response**: job_id (202 Accepted)
- `POST /api/simple-chain/generate` → Generate chain
  - **Request**: Same as submit
  - **Response**: Synchronous result with image_url, video_url
- `POST /api/simple-chain/bulk-submit` → Bulk chain generation
  - **Request**: List of chain configs
  - **Response**: List of job_ids

#### **3.5 `/api/storyboard` (storyboard.py)**
Multi-image T2I generation with structured prompts.

**Endpoints**:
- `POST /api/storyboard/structure-prompt` → Convert single prompt to multi-shot storyboard
  - **Request**: prompt, num_shots
  - **Response**: List of scene descriptions with camera movements

### Media Services Routers

#### **3.6 `/api/slideshow` (slideshow.py)**
**Endpoints**:
- `POST /api/slideshow/generate` → Create slideshow from images
  - **Request**: image_urls, transitions, music_url
  - **Response**: job_id (202 Accepted)
- `GET /api/slideshow/{job_id}/status` → Get status
- `GET /api/slideshow/{job_id}/download` → Download video

#### **3.7 `/api/lipsync` (lipsync.py)**
**Endpoints**:
- `POST /api/lipsync/apply` → Apply lip sync
  - **Request**: video_url, audio_url
  - **Response**: job_id (202 Accepted)
- `GET /api/lipsync/{job_id}/status` → Get status
- `GET /api/lipsync/{job_id}/download` → Download result

#### **3.8 `/api/tts` (tts.py)**
**Endpoints**:
- `POST /api/tts/generate` → Generate speech
  - **Request**: text, voice_id, model
  - **Response**: audio_url
- `GET /api/tts/voices` → List available voices
- `POST /api/tts/preview` → Preview voice

### Content Generation Routers

#### **3.9 `/api/post-captions` (captions.py)**
**Endpoints**:
- `POST /api/post-captions/generate` → Generate post caption for single video
  - **Request**: video_url, style, include_hashtags, frame_timestamp
  - **Response**: post_caption, detected_onscreen_text, style_used
- `POST /api/post-captions/generate-bulk` → Generate captions for multiple videos
  - **Request**: video_urls (max 50), style
  - **Response**: List of results with captions
- `GET /api/post-captions/styles` → List available styles

#### **3.10 `/api/templates` (templates.py)**
Pre-built generation templates.

**Endpoints**:
- `GET /api/templates` → List all templates
- `GET /api/templates/{template_id}` → Get template
- `POST /api/templates/admin` → Create template (admin only)
- `PATCH /api/templates/admin/{template_id}` → Update template
- `DELETE /api/templates/admin/{template_id}` → Delete template

#### **3.11 `/api/presets` (presets.py)**
User-saved presets.

**Endpoints**:
- `POST /api/presets` → Create preset
- `GET /api/presets` → List presets
- `GET /api/presets/{uuid}` → Get preset
- `PATCH /api/presets/{uuid}` → Update preset
- `DELETE /api/presets/{uuid}` → Delete preset
- `POST /api/presets/{uuid}/duplicate` → Duplicate preset
- `POST /api/presets/{uuid}/load` → Load preset

### Social Media Routers

#### **3.12 `/api/instagram` (instagram.py)**
**Endpoints**:
- `GET /api/instagram/auth-url` → Get OAuth URL
- `POST /api/instagram/callback` → Handle OAuth callback
- `GET /api/instagram/status` → Check connection status
- `POST /api/instagram/post` → Publish reel immediately
- `POST /api/instagram/schedule` → Schedule post
- `GET /api/instagram/scheduled` → List scheduled posts
- `DELETE /api/instagram/scheduled/{post_id}` → Cancel scheduled post
- `PATCH /api/instagram/scheduled/{post_id}` → Update scheduled post
- `POST /api/instagram/scheduled/{post_id}/publish-now` → Publish immediately
- `GET /api/instagram/accounts` → List connected accounts
- `PATCH /api/instagram/accounts/{account_id}` → Update account

#### **3.13 `/api/twitter` (twitter.py)**
**Endpoints**:
- `POST /api/twitter/post` → Post tweet
- `POST /api/twitter/thread` → Post thread
- `POST /api/twitter/schedule` → Schedule tweet
- `GET /api/twitter/scheduled` → List scheduled tweets
- `DELETE /api/twitter/scheduled/{tweet_id}` → Cancel scheduled tweet
- `GET /api/twitter/accounts` → List connected accounts

#### **3.14 `/api/twitter-autopilot` (twitter_autopilot.py)**
**Endpoints**:
- `GET /api/twitter-autopilot/status` → Get autopilot status
- `GET /api/twitter-autopilot/config/{account_id}` → Get config
- `PUT /api/twitter-autopilot/config/{account_id}` → Update config
- `POST /api/twitter-autopilot/config/{account_id}/toggle` → Enable/disable
- `POST /api/twitter-autopilot/trigger/{account_id}` → Manual trigger
- `POST /api/twitter-autopilot/search-trends/{account_id}` → Search trends
- `POST /api/twitter-autopilot/preview-tweet/{account_id}` → Preview tweet

#### **3.15 `/api/campaigns` (campaigns.py)**
Multi-account campaign management.

**Endpoints**:
- `GET /api/campaigns` → List campaigns
- `POST /api/campaigns` → Create campaign
- `GET /api/campaigns/{campaign_id}` → Get campaign
- `PUT /api/campaigns/{campaign_id}` → Update campaign
- `DELETE /api/campaigns/{campaign_id}` → Delete campaign
- `POST /api/campaigns/{campaign_id}/accounts` → Add accounts
- `DELETE /api/campaigns/{campaign_id}/accounts/{account_id}` → Remove account
- `GET /api/campaigns/{campaign_id}/posts` → List posts
- `POST /api/campaigns/{campaign_id}/send` → Distribute content to campaign

### User & Auth Routers

#### **3.16 `/api/auth` (auth.py)**
**Endpoints**:
- `POST /api/auth/signup` → Register new user
- `POST /api/auth/login` → Login
- `POST /api/auth/refresh` → Refresh token
- `GET /api/auth/me` → Get current user
- `POST /api/auth/logout` → Logout

#### **3.17 `/api/credits` (credits.py)**
**Endpoints**:
- `GET /api/credits/balance` → Get balance
- `GET /api/credits/transactions` → Get transaction history
- `POST /api/credits/estimate` → Estimate cost
- `GET /api/credits/pricing` → Get pricing table
- `POST /api/credits/admin/adjust` → Admin adjust credits
- `GET /api/credits/admin/user/{user_id}/balance` → Admin view balance
- `GET /api/credits/admin/user/{user_id}/transactions` → Admin view transactions

### Utility Routers

#### **3.18 `/api/downloads` (downloads.py)**
**Endpoints**:
- `POST /api/downloads/zip` → Download multiple images/videos as ZIP
  - **Request**: image_urls (up to 500), filename
  - **Response**: StreamingResponse with ZIP file

#### **3.19 `/api/exports` (exports.py)**
**Endpoints**:
- `GET /api/exports/lora-training/{pipeline_id}` → Export LoRA training data
  - **Returns**: ZIP with images + prompts.csv (filename, prompt)

#### **3.20 `/api/analytics` (analytics.py)**
**Endpoints**:
- `GET /api/analytics/dashboard` → Instagram dashboard analytics
- `GET /api/analytics/account/{ig_user_id}` → Account analytics
- `GET /api/analytics/recent/{ig_user_id}` → Recent posts
- `GET /api/analytics/global` → Global analytics

#### **3.21 `/api/nsfw` (nsfw.py)**
NSFW content generation endpoints.

**Endpoints**:
- `GET /api/nsfw/status` → Check NSFW generation availability
- `GET /api/nsfw/models` → List NSFW models
- `POST /api/nsfw/prompts` → Generate NSFW prompts
- `POST /api/nsfw/prompt` → Generate single NSFW prompt
- `POST /api/nsfw/caption` → Generate NSFW caption

---

## 4. FRONTEND PAGE MAP

### **4.1 Dashboard.tsx**
- **Purpose**: Main dashboard with quick stats
- **API Calls**: `/api/auth/me`, `/api/credits/balance`, `/api/pipelines` (recent)
- **Components**: StatsCards, RecentPipelines, QuickActions

### **4.2 ImageGeneration.tsx**
- **Purpose**: Image generation UI
- **API Calls**: `/api/flow/generate` (i2i step only)
- **Features**: Model selector (all T2I models), prompt input, aspect ratio, quality

### **4.3 VideoGeneration.tsx**
- **Purpose**: Video generation UI
- **API Calls**: `/api/flow/generate` (i2v step)
- **Features**: Model selector (all I2V models), motion prompt, resolution, duration

### **4.4 Playground.tsx**
- **Purpose**: Full pipeline builder
- **API Calls**: `/api/pipelines/submit`, `/api/pipelines/{id}`
- **Features**: Drag-drop step builder, live preview, step chaining

### **4.5 Storyboard.tsx**
- **Purpose**: Multi-scene storyboard creator
- **API Calls**: `/api/storyboard/structure-prompt`, `/api/flow/batch`
- **Features**: Scene editor, camera movement selector, batch generation

### **4.6 Storylines.tsx**
- **Purpose**: Video chain creator (I2V → I2V → I2V...)
- **API Calls**: `/api/video-chain/chain`, `/api/video-chain/chain/{id}`
- **Features**: Segment editor, init frame selector, chain preview

### **4.7 ContentLibrary.tsx**
- **Purpose**: Browse all generated content
- **API Calls**: `/api/flow/jobs`, `/api/pipelines`
- **Features**: Filter by type (image/video), search, download, delete

### **4.8 Jobs.tsx**
- **Purpose**: Job queue monitoring
- **API Calls**: `/api/flow/jobs`, `/api/flow/jobs/{id}`
- **Features**: Real-time status, error logs, retry button

### **4.9 Templates.tsx**
- **Purpose**: Browse and use templates
- **API Calls**: `/api/templates`, `/api/templates/{id}`
- **Features**: Template gallery, apply to new job

### **4.10 Presets.tsx**
- **Purpose**: Manage user presets
- **API Calls**: `/api/presets`, `/api/presets/{id}`
- **Features**: Create, edit, delete, load presets

### **4.11 Campaigns.tsx**
- **Purpose**: Multi-account campaign management
- **API Calls**: `/api/campaigns`, `/api/campaigns/{id}`
- **Features**: Add accounts, distribute content, schedule posts

### **4.12 InstagramSchedule.tsx**
- **Purpose**: Instagram scheduler
- **API Calls**: `/api/instagram/scheduled`, `/api/instagram/schedule`
- **Features**: Calendar view, post editor, publish now

### **4.13 AccountManagement.tsx**
- **Purpose**: Manage connected social accounts
- **API Calls**: `/api/instagram/accounts`, `/api/twitter/accounts`
- **Features**: Connect, disconnect, refresh tokens

---

## 5. GENERATION CAPABILITIES

### **5.1 Text-to-Image (T2I) Models**

All T2I models use **Fal.ai** as provider.

#### **FLUX Family (fal.ai)**

**FLUX.1**:
- `flux-general`: FLUX 1.0 i2i - strength controls transformation ($0.025/image)
  - Supports: strength, guidance_scale (0-5), num_inference_steps, scheduler

**FLUX.2** (Black Forest Labs - Nov 2025):
- `flux-2-dev`: Open-source, configurable, fast prototyping ($0.012/MP)
  - Supports: guidance_scale (0-20, default 2.5), num_inference_steps, prompt_expansion, acceleration (none/regular/high)
  - Multi-ref: Up to 4 images
- `flux-2-pro`: Zero-config production, best quality ($0.03/MP)
  - Supports: safety_tolerance (1-5)
  - Multi-ref: Up to 9 images
  - NO guidance_scale, NO num_inference_steps (zero-config)
- `flux-2-flex`: Fully configurable, multi-reference ($0.04/image)
  - Supports: guidance_scale (1.5-10, default 3.5), num_inference_steps, prompt_expansion (default true), safety_tolerance
  - Multi-ref: Up to 10 images
- `flux-2-max`: Highest quality, zero-config ($0.08/image)
  - Supports: safety_tolerance
  - Multi-ref: Up to 10 images
  - NO guidance_scale, NO num_inference_steps

**FLUX.1 Kontext** (In-context editing):
- `flux-kontext-dev`: Natural language image editing ($0.025/image)
  - Supports: guidance_scale (0-20, default 3.5), num_inference_steps
- `flux-kontext-pro`: Production in-context editing ($0.04/image)
  - Supports: guidance_scale, num_inference_steps

**FLUX Inpainting**:
- `flux_inpainting`: FLUX General Inpainting (fal-ai/flux-general/inpainting)
  - Supports: mask_url, strength, guidance_scale, controlnets, ip_adapters

#### **Other T2I Models**

- `gpt-image-1.5`: High-fidelity editing, strong prompt adherence ($0.009-$0.20/image)
- `kling-image`: Multi-reference control with Elements for character consistency ($0.028/image)
  - Supports: Up to 10 images + 10 elements, aspect_ratio, resolution (1K/2K)
  - Elements: frontal_image_url + 1-3 reference_image_urls per element
- `nano-banana-pro`: Google's best model - realistic, good typography ($0.15/image)
- `nano-banana`: Budget Google model ($0.039/image)
- `nano-banana-edit`: Multi-image compositing - combine subject from image1 with scene from image2 ($0.15/image)
  - Requires exactly 2 images
- `ideogram-2`: Best for text-in-image, accurate typography ($0.04/image)
  - Supports: strength (0.01-1.0), style (realistic, design, 3d, anime)

**How to Call T2I**:
```python
from app.services.generation_service import generate_image

image_urls = await generate_image(
    image_url="https://...",  # Source image
    prompt="transform into cyberpunk scene",
    model="flux-2-flex",  # Or any other model
    aspect_ratio="9:16",
    num_images=1,
    # FLUX.2 specific
    flux_image_urls=["https://ref1.jpg", "https://ref2.jpg"],  # Multi-ref
    flux_guidance_scale=3.5,
    flux_num_inference_steps=28,
    flux_enable_prompt_expansion=True,
    flux_safety_tolerance="5"  # 5 = most permissive (NSFW)
)
# Returns: List[str] of image URLs
```

**Endpoint**:
```bash
POST /api/flow/generate
{
  "steps": [
    {
      "step_type": "i2i",
      "model": "flux-2-flex",
      "prompt": "transform into cyberpunk scene",
      "image_url": "https://...",
      "aspect_ratio": "9:16",
      "flux_image_urls": ["https://ref1.jpg", "https://ref2.jpg"],
      "flux_guidance_scale": 3.5
    }
  ]
}
```

### **5.2 Image-to-Video (I2V) Models**

#### **Fal.ai I2V Models**

**Wan (Minimax)**:
- `wan`: Wan 2.5 Preview - 480p/720p/1080p ($0.05-0.15/s)
- `wan21`: Wan 2.1 - 480p/720p ($0.20/vid, $0.40/vid)
- `wan22`: Wan 2.2 - 480p/580p/720p ($0.04-0.08/s)
  - Supports: 17-161 frames (16 fps), aspect_ratio 9:16, negative_prompt
- `wan-pro`: Wan Pro - 1080p ($0.16/s, ~$0.80/5s)
- `wan26`: Wan 2.6 - 720p/1080p, 5/10/15s durations ($0.10-0.15/s)

**Kling (Kuaishou)**:
- `kling`: Kling 2.5 Turbo Pro - $0.35/5s + $0.07/extra sec
  - Supports: generate_audio (native audio generation), aspect_ratio, duration (5s/10s)
- `kling-master`: Kling 2.1 Master - $1.40/5s + $0.28/extra sec (highest quality)
- `kling-standard`: Kling 2.1 Standard - $0.25/5s + $0.05/extra sec (budget)
- `kling26-pro`: Kling 2.6 Pro - $0.07/s (audio off), $0.14/s (audio on)

**Veo (Google)**:
- `veo2`: Veo 2 - $0.50/s (720p only, 5-8s)
  - NO audio support (only Veo 3.1 has audio)
- `veo31-fast`: Veo 3.1 Fast - $0.10/s (no audio), $0.15/s (audio)
  - Supports: duration (4s/6s/8s), resolution (720p/1080p), enable_audio
- `veo31`: Veo 3.1 Standard - $0.20/s (no audio), $0.40/s (audio)
- `veo31-flf`: Veo 3.1 First-Last Frame - $0.20/s (no audio), $0.40/s (audio)
  - Requires: first_frame_image + last_frame_image
- `veo31-fast-flf`: Veo 3.1 Fast First-Last Frame - $0.10/s (no audio), $0.15/s (audio)

**Sora (OpenAI)**:
- `sora-2`: Sora 2 - $0.10/s (720p only, 4/8/12s)
  - Always generates audio (no parameter needed)
- `sora-2-pro`: Sora 2 Pro - $0.30/s (720p), $0.50/s (1080p), 4/8/12s

**Luma (Luma AI)**:
- `luma`: Luma Dream Machine - $0.032/s (5s=$0.16, 9s=$0.29)
  - Supports: duration (5s/9s), resolution (540p/720p/1080p)
- `luma-ray2`: Luma Ray 2 - $0.05/s (5s=$0.25, 9s=$0.45), better quality

**Other**:
- `cogvideox`: CogVideoX-5B - $0.20/video (flat rate)
- `stable-video`: Stable Video Diffusion - $0.075/video (flat rate)
  - Image-only, NO prompt support

#### **Vast.ai I2V Models (Self-hosted SwarmUI)**

- `vastai-wan22-remix-i2v`: Wan 2.2 Remix on Vast.ai
- `vastai-wan22-t2v`: Wan 2.2 T2V on Vast.ai
- `vastai-cogvideox`: CogVideoX on Vast.ai
- `vastai-svd`: Stable Video Diffusion on Vast.ai

**Vast.ai Features**:
- Progress tracking (0-100%)
- Caption overlay (on-screen text)
- Spoofing (crop/scale/metadata)
- Custom frames, FPS, video_steps

**How to Call I2V**:
```python
from app.services.generation_service import generate_video

video_url = await generate_video(
    image_url="https://...",  # Source image (None for T2V)
    prompt="camera zooms in slowly, dramatic lighting",
    model="wan22",  # Or any other model
    resolution="1080p",
    duration_sec=5,
    enable_audio=False,
    negative_prompt="static, low quality"
)
# Returns: str (video URL)
```

**Endpoint**:
```bash
POST /api/flow/generate
{
  "steps": [
    {
      "step_type": "i2v",
      "model": "wan22",
      "prompt": "camera zooms in slowly",
      "image_url": "https://...",
      "resolution": "1080p",
      "duration_sec": 5,
      "enable_audio": false
    }
  ]
}
```

### **5.3 Text-to-Video (T2V) Models**

**T2V models do NOT require image_url**:
- `wan22-t2v`: Wan 2.2 T2V ($0.04-0.08/s)
- `kling-t2v`: Kling 2.5 Turbo Pro T2V ($0.35/5s + $0.07/extra sec)
- `veo31-fast-t2v`: Veo 3.1 Fast T2V ($0.10/s no audio, $0.15/s audio)
- `vastai-wan22-t2v`: Wan 2.2 T2V on Vast.ai

**How to Call T2V**:
```python
video_url = await generate_video(
    image_url=None,  # Not needed for T2V
    prompt="a cat walking in a cyberpunk city",
    model="wan22-t2v",
    resolution="720p",
    duration_sec=5
)
```

### **5.4 TTS Capabilities**

**Provider**: ElevenLabs

**How to Call**:
```python
from app.services.tts_service import generate_speech

audio_url = await generate_speech(
    text="Hello, this is a test.",
    voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel
    model="eleven_turbo_v2_5"
)
# Returns: str (audio URL)
```

**Endpoint**:
```bash
POST /api/tts/generate
{
  "text": "Hello, this is a test.",
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "model": "eleven_turbo_v2_5"
}
```

**Available Voices**:
```bash
GET /api/tts/voices
```

### **5.5 Lip Sync Capabilities**

**Provider**: Hedra API

**How to Call**:
```python
from app.services.lipsync_service import apply_lipsync, get_lipsync_status

# Submit job
job_id = await apply_lipsync(
    video_url="https://...",
    audio_url="https://..."
)

# Poll for result
status = await get_lipsync_status(job_id)
# status = {"status": "completed", "video_url": "https://..."}
```

**Endpoint**:
```bash
POST /api/lipsync/apply
{
  "video_url": "https://...",
  "audio_url": "https://..."
}

GET /api/lipsync/{job_id}/status
```

### **5.6 Video Stitching/Assembly Capabilities**

**Service**: VideoConcatService (uses FFmpeg)

**How to Call**:
```python
from app.services.video_concat import VideoConcatService

service = VideoConcatService()
final_video_path = await service.concatenate_videos(
    video_urls=["https://clip1.mp4", "https://clip2.mp4", "https://clip3.mp4"],
    output_path="/tmp/final.mp4"
)
# Returns: str (local file path)
```

**Endpoint** (via pipeline):
```bash
POST /api/pipelines/submit
{
  "steps": [
    {
      "step_type": "video_concat",
      "video_urls": ["https://clip1.mp4", "https://clip2.mp4"]
    }
  ]
}
```

### **5.7 Inpainting/I2I Capabilities**

**FLUX Inpainting**:
```python
from app.image_client import generate_flux_inpainting

result = await generate_flux_inpainting(
    prompt="a red apple",
    image_url="https://base.jpg",
    mask_url="https://mask.jpg",  # White = inpaint, black = preserve
    strength=0.85,
    guidance_scale=3.5,
    num_inference_steps=28
)
# Returns: dict with images, seed
```

**Multi-Image Compositing** (Nano-Banana Edit):
```python
image_urls = await generate_image(
    image_url="https://subject.jpg",  # Main image
    prompt="put the person from @image1 into the scene from @image2",
    model="nano-banana-edit",
    additional_images=["https://background.jpg"]  # Second image
)
```

**Face Swap**:
```python
from app.face_swap_client import submit_face_swap_job, get_face_swap_result

# Submit job
request_id = await submit_face_swap_job(
    face_image_url="https://face.jpg",
    target_image_url="https://target.jpg",
    gender="female",
    workflow_type="target_hair",  # or "user_hair"
    upscale=True
)

# Poll for result
result = await get_face_swap_result(request_id, model="easel-advanced")
# result = {"status": "completed", "image_url": "https://..."}
```

**Endpoint**:
```bash
POST /api/pipelines/submit
{
  "steps": [
    {
      "step_type": "face_swap",
      "face_image_url": "https://face.jpg",
      "target_image_url": "https://target.jpg",
      "gender": "female"
    }
  ]
}
```

---

## 6. PIPELINE SYSTEM

### **6.1 Pipeline Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    PIPELINE EXECUTOR                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Database Tables:                                           │
│  • Pipeline (id, name, status, created_at)                  │
│  • PipelineStep (id, pipeline_id, step_type, status,        │
│                  inputs, outputs, step_order)               │
│                                                             │
│  Step Execution Flow:                                       │
│  1. Create Pipeline record                                  │
│  2. Create PipelineStep records (step_order 1, 2, 3...)    │
│  3. Execute steps sequentially                              │
│  4. Each step:                                              │
│     • Reads inputs from previous step's outputs             │
│     • Calls appropriate service (generate_image,            │
│       generate_video, etc.)                                 │
│     • Stores outputs (image_url, video_url)                 │
│     • Updates status (pending → running → completed)        │
│  5. On completion: Pipeline status = completed              │
│  6. On failure: Pipeline status = failed                    │
│                                                             │
│  Error Handling:                                            │
│  • Retry logic with exponential backoff                     │
│  • Orphan detection (stuck in "running" for >1h)            │
│  • Cooldown management (exponential backoff)                │
│  • Error classification (network, rate limit, invalid,      │
│                          transient, permanent)              │
└─────────────────────────────────────────────────────────────┘
```

### **6.2 Supported Step Types**

| Step Type | Purpose | Inputs | Outputs | Provider |
|-----------|---------|--------|---------|----------|
| `prompt_enhance` | Enhance prompt with AI | `prompt`, `style` | `enhanced_prompt` | Claude |
| `i2i` | Image-to-image | `image_url`, `prompt`, `model` | `image_urls` | Fal.ai |
| `i2v` | Image-to-video | `image_url`, `prompt`, `model`, `resolution`, `duration_sec` | `video_url` | Fal.ai or Vast.ai |
| `face_swap` | Swap faces | `face_image_url`, `target_image_url`, `gender` | `image_url` | Fal.ai |
| `tts` | Text-to-speech | `text`, `voice_id`, `model` | `audio_url` | ElevenLabs |
| `lipsync` | Apply lip sync | `video_url`, `audio_url` | `video_url` | Hedra |
| `audio_bed` | Background music | `video_url`, `song_url`, `mode` | `video_url` | FFmpeg |
| `video_concat` | Stitch videos | `video_urls` | `video_url` | FFmpeg |

### **6.3 Output Chaining**

Steps automatically chain outputs:

```json
{
  "steps": [
    {
      "step_type": "i2i",
      "model": "flux-2-flex",
      "prompt": "cyberpunk portrait",
      "image_url": "https://input.jpg"
    },
    {
      "step_type": "i2v",
      "model": "wan22",
      "prompt": "camera zooms in",
      "image_url": "{{prev.image_urls[0]}}",  // Uses output from step 1
      "resolution": "1080p",
      "duration_sec": 5
    },
    {
      "step_type": "tts",
      "text": "Hello, this is a test.",
      "voice_id": "21m00Tcm4TlvDq8ikWAM"
    },
    {
      "step_type": "lipsync",
      "video_url": "{{step[1].video_url}}",  // Uses output from step 2
      "audio_url": "{{prev.audio_url}}"  // Uses output from step 3
    }
  ]
}
```

### **6.4 Error Handling & Retry Logic**

**Error Classification** (from `error_classifier.py`):
- `NETWORK`: Retry with backoff (timeouts, connection refused)
  - Max retries: 5, base delay: 1s
- `RATE_LIMIT`: Retry with longer backoff (HTTP 429)
  - Max retries: 5, base delay: 30s
- `INVALID_INPUT`: Fail immediately (HTTP 400, validation error)
  - Max retries: 0
- `TRANSIENT`: Retry 2-3x then fail (HTTP 500-503)
  - Max retries: 3, base delay: 2s
- `PERMANENT`: Fail immediately (HTTP 401/403)
  - Max retries: 0
- `UNKNOWN`: Default to transient behavior
  - Max retries: 2, base delay: 5s

**Cooldown Schedule** (from `cooldown_manager.py`):
After consecutive failures:
- 1st: 5 seconds
- 2nd: 15 seconds
- 3rd: 1 minute
- 4th: 5 minutes
- 5th: 15 minutes
- 6th: 1 hour
- 7th: 6 hours
- 8th+: 24 hours

**Orphan Detection**:
- Steps stuck in "running" for >1 hour are marked as orphaned
- Automatically retried or marked as failed

---

## 7. WHAT'S RELEVANT FOR SNOWFLAKE INTEGRATION

### **7.1 Recommended Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│              SNOWFLAKE → I2V INTEGRATION                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Snowflake Screenplay Engine (outputs):                     │
│  • World Bible (locations, settings)                        │
│  • Character Bible (character bios, visual descriptions)    │
│  • Visual Bible (setting-per-location prompts)             │
│  • Scene Breakdown (beats → scenes with dialogue)           │
│                                                             │
│  ▼                                                          │
│                                                             │
│  Shot Engine (NEW - to build):                              │
│  • Parse Visual Bible (setting descriptions per location)   │
│  • Parse Character Bible (visual features per character)    │
│  • For each scene:                                          │
│    1. Generate setting image (T2I, once per location)       │
│    2. Generate character portraits (T2I, once per char)     │
│    3. Inpaint characters into setting (I2I compositing)     │
│    4. Animate frame (I2V via Veo/Kling/Wan)                │
│    5. Generate dialogue audio (TTS)                         │
│    6. Apply lip sync                                        │
│    7. Repeat for all shots in scene                        │
│  • Stitch shots into scene (video_concat)                   │
│  • Stitch scenes into film (video_concat)                   │
│                                                             │
│  ▼                                                          │
│                                                             │
│  I2V Platform (storage):                                    │
│  • R2 cache (Cloudflare) for all assets                    │
│  • Pipeline records for tracking                           │
└─────────────────────────────────────────────────────────────┘
```

### **7.2 Specific Services to Use**

#### **For Setting Images** (once per location):
**Service**: `generation_service.generate_image()`
**Model**: `flux-2-flex` (best quality, multi-reference support)
**Input**: Visual Bible location description (e.g., "Victorian mansion exterior, fog, moonlight")
**Output**: List[str] of setting image URLs
**Endpoint**: `POST /api/flow/generate` with `step_type: "i2i"`

```python
from app.services.generation_service import generate_image

setting_url = (await generate_image(
    image_url="https://base_reference.jpg",  # Optional reference
    prompt="Victorian mansion exterior, fog, moonlight, gothic architecture",
    model="flux-2-flex",
    aspect_ratio="16:9",
    num_images=1,
    flux_guidance_scale=3.5,
    flux_enable_prompt_expansion=True
))[0]
```

#### **For Character Portraits** (once per character):
**Service**: `generation_service.generate_image()`
**Model**: `flux-2-flex` or `kling-image` (for character consistency)
**Input**: Character Bible visual description (e.g., "male, 30s, tall, dark hair, green eyes")
**Output**: List[str] of character portrait URLs
**Endpoint**: `POST /api/flow/generate` with `step_type: "i2i"`

```python
character_url = (await generate_image(
    image_url="https://character_reference.jpg",  # Optional reference
    prompt="male, 30s, tall, dark hair, green eyes, professional attire",
    model="kling-image",  # Good for character consistency
    aspect_ratio="9:16",
    num_images=1,
    elements=[{  # Use Kling Elements for consistency across scenes
        "frontal_image_url": "https://char_ref_frontal.jpg",
        "reference_image_urls": ["https://char_ref_side.jpg", "https://char_ref_back.jpg"]
    }]
))[0]
```

#### **For Inpainting Characters into Settings**:
**Service**: `image_client.generate_flux_inpainting()` or `generation_service.generate_image()` with `nano-banana-edit`
**Models**:
- `flux_inpainting` (FLUX General Inpainting) - best control with mask
- `nano-banana-edit` (Multi-image compositing) - simpler, no mask needed
**Input**: Setting image + character image (+ optional mask for FLUX)
**Output**: Composite image URL

**Option 1: FLUX Inpainting (with mask)**:
```python
from app.image_client import generate_flux_inpainting

composite = await generate_flux_inpainting(
    prompt="person standing in the room",
    image_url="https://setting.jpg",  # Base setting
    mask_url="https://mask.jpg",  # White = where to insert character
    strength=0.85,
    guidance_scale=3.5,
    ip_adapters=[{  # Use IP-Adapter to inject character reference
        "path": "h94/IP-Adapter",
        "image_url": "https://character.jpg",
        "scale": 0.8
    }]
)
composite_url = composite["images"][0]["url"]
```

**Option 2: Nano-Banana Edit (simpler, no mask)**:
```python
composite_url = (await generate_image(
    image_url="https://character.jpg",  # Subject image
    prompt="put the person from @image1 into the scene from @image2",
    model="nano-banana-edit",
    additional_images=["https://setting.jpg"],  # Background image
    aspect_ratio="16:9"
))[0]
```

#### **For Animating Frames** (I2V):
**Service**: `generation_service.generate_video()`
**Recommended Models**:
- `wan22`: Budget-friendly, good quality ($0.04-0.08/s)
- `veo31-fast`: Google, faster, supports audio ($0.10-0.15/s)
- `kling26-pro`: Premium, native audio generation ($0.07-0.14/s)
**Input**: Composite frame + motion prompt
**Output**: Video URL

```python
from app.services.generation_service import generate_video

shot_video_url = await generate_video(
    image_url="https://composite_frame.jpg",
    prompt="camera slowly zooms in on the character's face, dramatic lighting",
    model="wan22",
    resolution="1080p",
    duration_sec=5,
    enable_audio=False,  # Add audio later with TTS + lipsync
    negative_prompt="static, low quality, blurry"
)
```

#### **For Dialogue Audio** (TTS):
**Service**: `tts_service.generate_speech()`
**Provider**: ElevenLabs
**Input**: Dialogue text from scene breakdown
**Output**: Audio URL

```python
from app.services.tts_service import generate_speech

dialogue_audio_url = await generate_speech(
    text="I never should have come here.",
    voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel (female)
    model="eleven_turbo_v2_5"
)
```

**Available Voices**:
```python
# Get list of voices
voices = await get_available_voices()
# Returns: List[dict] with voice_id, name, gender
```

#### **For Lip Sync**:
**Service**: `lipsync_service.apply_lipsync()`
**Provider**: Hedra
**Input**: Shot video + dialogue audio
**Output**: Video with lip sync

```python
from app.services.lipsync_service import apply_lipsync, get_lipsync_status

# Submit job
job_id = await apply_lipsync(
    video_url=shot_video_url,
    audio_url=dialogue_audio_url
)

# Poll for result (async)
import asyncio
while True:
    status = await get_lipsync_status(job_id)
    if status["status"] == "completed":
        final_shot_url = status["video_url"]
        break
    elif status["status"] == "failed":
        raise Exception(status["error_message"])
    await asyncio.sleep(5)
```

#### **For Stitching Shots into Scenes**:
**Service**: `video_concat.VideoConcatService`
**Input**: List of shot video URLs
**Output**: Scene video file path

```python
from app.services.video_concat import VideoConcatService

service = VideoConcatService()
scene_video_path = await service.concatenate_videos(
    video_urls=[shot1_url, shot2_url, shot3_url],
    output_path="/tmp/scene_01.mp4"
)
```

#### **For Stitching Scenes into Film**:
**Service**: `video_concat.VideoConcatService`
**Input**: List of scene video URLs
**Output**: Final film file path

```python
final_film_path = await service.concatenate_videos(
    video_urls=[scene1_url, scene2_url, ...],
    output_path="/tmp/final_film.mp4"
)
```

#### **For Storing Assets** (R2 Cache):
**Service**: `r2_cache`
**Provider**: Cloudflare R2
**Input**: Video bytes or URL
**Output**: Cached URL (permanent storage)

```python
from app.services.r2_cache import cache_video, cache_image

# Cache video
cached_video_url = await cache_video(
    original_url="https://temp_fal_url.mp4",
    video_bytes=video_bytes  # Optional, will download if not provided
)

# Cache image
cached_image_url = await cache_image(
    original_url="https://temp_fal_url.jpg",
    image_bytes=image_bytes
)
```

### **7.3 Recommended Pipeline Pattern for Snowflake**

**Use Case**: Generate a single scene with 3 shots (wide, medium, close-up)

```python
# 1. Generate setting (once per location)
setting_url = await generate_image(
    prompt=visual_bible["mansion_exterior"],
    model="flux-2-flex"
)

# 2. Generate character portrait (once per character)
hero_portrait_url = await generate_image(
    prompt=character_bible["hero"]["visual_description"],
    model="kling-image"
)

# 3. For each shot in scene:
shots = []
for shot in scene_breakdown["shots"]:
    # 3a. Inpaint character into setting
    composite_url = await generate_image(
        image_url=hero_portrait_url,
        prompt=f"put @image1 into @image2, {shot['framing']}",  # e.g., "wide shot", "close-up"
        model="nano-banana-edit",
        additional_images=[setting_url]
    )

    # 3b. Animate frame
    video_url = await generate_video(
        image_url=composite_url,
        prompt=shot["motion_prompt"],  # e.g., "camera zooms in slowly"
        model="wan22",
        resolution="1080p",
        duration_sec=5
    )

    # 3c. Generate dialogue audio
    if shot["dialogue"]:
        audio_url = await generate_speech(
            text=shot["dialogue"],
            voice_id=character_bible["hero"]["voice_id"]
        )

        # 3d. Apply lip sync
        job_id = await apply_lipsync(video_url, audio_url)
        # Poll for completion...
        video_url = final_lipsync_url

    # 3e. Cache to R2
    cached_url = await cache_video(video_url)
    shots.append(cached_url)

# 4. Stitch shots into scene
scene_path = await VideoConcatService().concatenate_videos(shots, "/tmp/scene_01.mp4")

# 5. Upload scene to R2
scene_url = await cache_video(None, open(scene_path, "rb").read())
```

**Estimated Costs per Scene** (3 shots, 5s each):
- Setting image (FLUX-2-flex): $0.04
- Character portrait (Kling): $0.03
- 3× Composite (Nano-Banana Edit): $0.45
- 3× I2V (Wan 2.2, 5s): $0.60
- 3× TTS (ElevenLabs, ~30 chars): $0.01
- 3× Lip sync (Hedra): ~$0.15
- **Total: ~$1.28 per scene**

**For 90-page screenplay** (~60 scenes):
- **Total: ~$77** (without optimizations)

**Optimizations**:
1. **Reuse setting images** across scenes in same location (reduce T2I calls)
2. **Reuse character portraits** across scenes (reduce T2I calls)
3. **Batch I2V generations** in parallel (use `POST /api/flow/batch`)
4. **Use cheaper models** for non-critical shots (e.g., `wan21` instead of `wan22`)

### **7.4 Database Schema Considerations**

**Snowflake should track**:
- `screenplay_id` → Links to Snowflake screenplay record
- `scene_id` → Links to scene in screenplay
- `shot_id` → Links to shot in scene
- `asset_type` → "setting_image", "character_portrait", "composite_frame", "shot_video", "scene_video"
- `asset_url` → R2 cached URL
- `pipeline_id` → Links to i2v Pipeline record for tracking

**Example table**:
```sql
CREATE TABLE snowflake_assets (
    id INTEGER PRIMARY KEY,
    screenplay_id INTEGER NOT NULL,
    scene_id INTEGER,
    shot_id INTEGER,
    asset_type VARCHAR(50) NOT NULL,  -- setting_image, character_portrait, etc.
    asset_url VARCHAR(500) NOT NULL,  -- R2 cached URL
    pipeline_id INTEGER,  -- Foreign key to i2v Pipeline table
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **7.5 Error Handling for Snowflake Integration**

**Critical Errors**:
1. **Model Unavailable**: Fallback to alternative model (e.g., `wan22` → `wan21`)
2. **Rate Limit**: Use cooldown manager (automatic in pipeline executor)
3. **Generation Failure**: Retry with different seed or lower quality settings
4. **Asset Storage Failure**: Fallback to local filesystem cache

**Recommended Pattern**:
```python
from app.services.error_classifier import ErrorClassifier

classifier = ErrorClassifier()

try:
    video_url = await generate_video(...)
except Exception as e:
    classified = classifier.classify(e)

    if classified.retryable:
        # Retry with exponential backoff
        for attempt in range(classified.max_retries):
            await asyncio.sleep(classified.base_delay_seconds * (2 ** attempt))
            try:
                video_url = await generate_video(...)
                break
            except Exception as retry_error:
                if attempt == classified.max_retries - 1:
                    raise  # Final attempt failed
    else:
        # Non-retryable error, log and skip
        logger.error("Non-retryable error", error=str(e))
        raise
```

---

## 8. EXTERNAL API INTEGRATIONS

### **8.1 Fal.ai**
- **Purpose**: Primary provider for T2I, I2V, face swap
- **Authentication**: API key via `FAL_API_KEY` env var
- **Base URLs**:
  - Submit: `https://queue.fal.run/{model_path}`
  - Status: `https://queue.fal.run/{model_path}/requests/{request_id}/status`
- **Client**: `app/fal_client.py`, `app/image_client.py`, `app/face_swap_client.py`

### **8.2 Vast.ai**
- **Purpose**: Self-hosted SwarmUI instances for I2V
- **Authentication**: SSH keys + API key
- **Client**: `app/services/vastai_client.py`, `app/services/vastai_orchestrator.py`
- **Features**: Instance pooling, health checks, progress tracking

### **8.3 ElevenLabs**
- **Purpose**: TTS voice synthesis
- **Authentication**: API key via `ELEVENLABS_API_KEY` env var
- **Client**: `app/services/tts_service.py`

### **8.4 Hedra**
- **Purpose**: Lip sync
- **Authentication**: API key via `HEDRA_API_KEY` env var
- **Client**: `app/services/lipsync_service.py`

### **8.5 Cloudflare R2**
- **Purpose**: Permanent media storage
- **Authentication**: Access key + secret key
- **Client**: `app/services/r2_cache.py`

### **8.6 Instagram API**
- **Purpose**: Publishing reels
- **Authentication**: OAuth 2.0 (Instagram Login)
- **Client**: `app/routers/instagram.py`

### **8.7 Twitter API**
- **Purpose**: Publishing tweets
- **Authentication**: OAuth 1.0a and OAuth 2.0
- **Client**: `app/services/twitter_client.py`, `app/routers/twitter.py`

### **8.8 Anthropic (Claude)**
- **Purpose**: Prompt enhancement, caption generation, content generation
- **Authentication**: API key via `ANTHROPIC_API_KEY` env var
- **Client**: Used in various services (caption_generator, prompt_enhancer, etc.)

---

## 9. KEY CONFIGURATION FILES

### **9.1 `.env` (Environment Variables)**
```bash
# Fal.ai
FAL_API_KEY=your_fal_key

# ElevenLabs
ELEVENLABS_API_KEY=your_elevenlabs_key

# Hedra
HEDRA_API_KEY=your_hedra_key

# Cloudflare R2
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
R2_BUCKET_NAME=your_bucket
R2_ENDPOINT_URL=https://your_account.r2.cloudflarestorage.com

# Anthropic (Claude)
ANTHROPIC_API_KEY=your_anthropic_key

# Instagram
INSTAGRAM_APP_ID=your_app_id
INSTAGRAM_APP_SECRET=your_app_secret
INSTAGRAM_REDIRECT_URI=http://localhost:5173/auth/instagram/callback

# Twitter
TWITTER_API_KEY=your_twitter_key
TWITTER_API_SECRET=your_twitter_secret

# Database
DATABASE_URL=sqlite:///./wan_jobs.db

# JWT
JWT_SECRET_KEY=your_jwt_secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_MINUTES=10080

# User Defaults
DEFAULT_USER_TIER=starter
DEFAULT_USER_CREDITS=1000
```

### **9.2 `app/config.py` (Settings)**
Central configuration using Pydantic BaseSettings.

### **9.3 `app/database.py` (Database)**
SQLAlchemy setup with SQLite (wan_jobs.db).

---

## 10. SUMMARY

**i2v** is a comprehensive AI video generation platform with:

1. **Multi-provider support**: Fal.ai (20+ I2V models, 13+ T2I models), Vast.ai (self-hosted), ElevenLabs (TTS), Hedra (lip sync)
2. **Pipeline system**: Multi-step workflows (T2I → I2V → TTS → Lip Sync → Stitch)
3. **Social media integration**: Instagram & Twitter publishing, scheduling, campaigns
4. **Robust error handling**: Retry logic, cooldown management, orphan detection
5. **Permanent storage**: Cloudflare R2 cache
6. **Rich API**: 20+ routers with 100+ endpoints

**For Snowflake integration**, the key services are:
- **T2I**: `generation_service.generate_image()` with `flux-2-flex` or `kling-image`
- **I2I**: `image_client.generate_flux_inpainting()` or `nano-banana-edit` for compositing
- **I2V**: `generation_service.generate_video()` with `wan22`, `veo31-fast`, or `kling26-pro`
- **TTS**: `tts_service.generate_speech()` with ElevenLabs
- **Lip Sync**: `lipsync_service.apply_lipsync()` with Hedra
- **Stitching**: `video_concat.VideoConcatService.concatenate_videos()`
- **Storage**: `r2_cache.cache_video()` and `cache_image()`

**Recommended workflow**:
1. Generate setting images (once per location)
2. Generate character portraits (once per character)
3. For each shot: inpaint character → animate → add audio → lip sync
4. Stitch shots into scenes
5. Stitch scenes into film
6. Cache all assets to R2

**Estimated cost**: ~$1.28 per scene (3 shots, 5s each) = ~$77 for 90-page screenplay

---

**End of I2V Codebase Digest**
