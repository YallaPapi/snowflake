# Changelog

## v2.0.0 - Major Pipeline Improvements (2025-08-19)

### 🚀 Major Features
- **Complete E2E Pipeline**: All 11 Snowflake Method steps fully implemented and tested
- **Step 10 Implementation**: Full manuscript generation with scene-by-scene prose
- **OpenRouter Integration**: Support for uncensored models for adult/erotic content
- **Export System**: Professional DOCX, EPUB, and Markdown export functionality
- **Progress Tracking**: Save/resume capability with comprehensive checkpoint system

### 📈 Performance Improvements
- **Step 9 Enhanced**: Individual scene brief generation (20 briefs) with concrete details
- **Step 3 Optimized**: Reduced retry attempts to prevent timeouts
- **Token Optimization**: Better token limits and batching strategies
- **Error Recovery**: Comprehensive retry logic with exponential backoff

### 🛠️ Technical Improvements
- **Multi-Provider Support**: Claude, GPT-4, and OpenRouter integration
- **Quality Validation**: Strict validators for each step with fix suggestions
- **API Infrastructure**: Complete REST API and observability system
- **Docker Support**: Full containerization with docker-compose

### 🎯 Quality Enhancements
- **Better Prompts**: Improved prompts for longer, more detailed content
- **Concrete Details**: Scene briefs now include specific goals, conflicts, and stakes
- **Prose Length**: Step 10 generates full-length scenes (2000+ words each)
- **Validation System**: Comprehensive checking with actionable fix suggestions

### 📊 Adult Content Support
- **OpenRouter Models**: Integration with uncensored models
- **Content Ratings**: Support for suggestive, mature, and explicit content
- **Specialized Models**: Midnight Rose, MythoMax, Dolphin for adult fiction
- **Quality Control**: Maintains narrative coherence in adult scenes

### 🔧 Developer Experience
- **Progress Reports**: Detailed status tracking and time estimation
- **Error Handling**: Graceful degradation with meaningful error messages
- **Testing Suite**: Comprehensive E2E and unit tests
- **Documentation**: Complete API documentation and usage examples

### 📈 Production Readiness: 85%
- ✅ All core functionality implemented
- ✅ Professional export formats
- ✅ Multi-provider AI support
- ✅ Progress tracking and resumption
- ✅ Comprehensive error handling
- ⚠️ Performance optimization ongoing
- ⚠️ Quality consistency improvements needed

### 🏗️ Architecture
```
Pipeline: Steps 0-10 ✅
Validation: All steps ✅
Export: DOCX/EPUB/MD ✅
Progress: Save/Resume ✅
API: REST endpoints ✅
Docker: Full support ✅
```

### 💰 Cost Estimates (per novel)
- Claude 3.5 Sonnet: $5-15
- GPT-4 Turbo: $15-30
- OpenRouter: $2-25 (varies by model)

### ⏱️ Generation Time
- Total: 20-60 minutes
- Steps 0-8: 5-15 minutes
- Step 9: 5-10 minutes
- Step 10: 10-30 minutes

### 🔗 Breaking Changes
- Requires API keys for AI providers
- New dependency: `python-docx`, `ebooklib`
- OpenRouter support requires additional API key

---

## v1.0.0 - Initial Implementation (Previous)
- Basic Snowflake Method steps 0-8
- Simple AI integration
- JSON artifact storage
- Basic validation system