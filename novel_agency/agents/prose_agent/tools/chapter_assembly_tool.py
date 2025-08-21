"""
Chapter Assembly Tool - Manuscript Organization

Assembles scenes into chapters and manages overall manuscript structure.
"""

from pydantic import Field
from agency_swarm.tools import BaseTool


class ChapterAssemblyTool(BaseTool):
    """
    Tool for assembling scenes into chapters and organizing the complete manuscript.
    """
    
    action: str = Field(..., description="Action to perform: 'assemble_chapters', 'create_transitions', 'format_manuscript', 'analyze_structure'")
    scene_prose: list = Field(default=[], description="List of completed scene prose")
    scene_metadata: list = Field(default=[], description="Scene metadata with chapter hints and transitions")
    target_chapters: int = Field(default=0, description="Target number of chapters (0 = auto-determine)")
    manuscript_format: str = Field(default="markdown", description="Output format: 'markdown', 'docx', 'plain_text'")
    
    def run(self) -> str:
        """Execute chapter assembly tool action"""
        
        if self.action == "assemble_chapters":
            return self._assemble_chapters()
        elif self.action == "create_transitions":
            return self._create_transitions()
        elif self.action == "format_manuscript":
            return self._format_manuscript()
        elif self.action == "analyze_structure":
            return self._analyze_structure()
        else:
            return "Error: Invalid action. Use 'assemble_chapters', 'create_transitions', 'format_manuscript', or 'analyze_structure'"
    
    def _assemble_chapters(self) -> str:
        """Assemble scenes into coherent chapters"""
        if not self.scene_prose:
            return "Error: Scene prose required for chapter assembly"
        
        total_scenes = len(self.scene_prose)
        
        # Determine chapter structure
        if self.target_chapters > 0:
            chapters_count = self.target_chapters
        else:
            # Auto-determine based on scene count (3-5 scenes per chapter typically)
            chapters_count = max(1, total_scenes // 4)
        
        assembly_report = f"📚 CHAPTER ASSEMBLY\n\n"
        assembly_report += f"Total scenes: {total_scenes}\n"
        assembly_report += f"Target chapters: {chapters_count}\n\n"
        
        # Group scenes into chapters
        chapters = self._group_scenes_into_chapters(chapters_count)
        
        assembly_report += f"**Chapter Structure:**\n"
        total_words = 0
        
        for i, chapter in enumerate(chapters):
            chapter_num = i + 1
            chapter_scenes = chapter['scenes']
            chapter_word_count = sum(len(prose.split()) for prose in chapter_scenes)
            total_words += chapter_word_count
            
            assembly_report += f"Chapter {chapter_num}: {len(chapter_scenes)} scenes, ~{chapter_word_count:,} words\n"
            
            # Show scene summaries if available
            if self.scene_metadata and len(self.scene_metadata) >= len(chapter_scenes):
                for j, scene_idx in enumerate(chapter.get('scene_indices', [])):
                    if scene_idx < len(self.scene_metadata):
                        scene_meta = self.scene_metadata[scene_idx]
                        scene_summary = scene_meta.get('summary', f'Scene {scene_idx + 1}')
                        assembly_report += f"  - {scene_summary[:80]}...\n"
            
            assembly_report += "\n"
        
        assembly_report += f"**Manuscript Totals:**\n"
        assembly_report += f"Total words: ~{total_words:,}\n"
        assembly_report += f"Average chapter length: ~{total_words // chapters_count:,} words\n"
        
        # Check for structural issues
        structural_issues = self._check_chapter_balance(chapters)
        if structural_issues:
            assembly_report += f"\n**Structural Notes:**\n"
            for issue in structural_issues:
                assembly_report += f"- {issue}\n"
        else:
            assembly_report += f"\n✅ Chapter structure appears well-balanced\n"
        
        return assembly_report
    
    def _create_transitions(self) -> str:
        """Create smooth transitions between scenes and chapters"""
        if not self.scene_prose or not self.scene_metadata:
            return "Error: Scene prose and metadata required for transition creation"
        
        transitions_report = f"🔗 TRANSITION ANALYSIS\n\n"
        
        transition_suggestions = []
        
        # Analyze scene-to-scene transitions
        for i in range(len(self.scene_prose) - 1):
            current_scene_meta = self.scene_metadata[i] if i < len(self.scene_metadata) else {}
            next_scene_meta = self.scene_metadata[i + 1] if i + 1 < len(self.scene_metadata) else {}
            
            current_chapter = current_scene_meta.get('chapter_hint', 1)
            next_chapter = next_scene_meta.get('chapter_hint', 1)
            
            # Check for chapter breaks
            if next_chapter > current_chapter:
                transition_suggestions.append({
                    'type': 'chapter_break',
                    'position': i + 1,
                    'suggestion': f"Chapter break between scenes {i+1} and {i+2}",
                    'current_scene': current_scene_meta.get('summary', 'Scene'),
                    'next_scene': next_scene_meta.get('summary', 'Scene')
                })
            
            # Check for POV changes
            current_pov = current_scene_meta.get('pov', 'unknown')
            next_pov = next_scene_meta.get('pov', 'unknown')
            
            if current_pov != next_pov:
                transition_suggestions.append({
                    'type': 'pov_change',
                    'position': i + 1,
                    'suggestion': f"POV change from {current_pov} to {next_pov}",
                    'recommendation': "Consider scene break or clear transition marker"
                })
            
            # Check for time/location jumps
            current_time = current_scene_meta.get('time', '')
            next_time = next_scene_meta.get('time', '')
            current_location = current_scene_meta.get('location', '')
            next_location = next_scene_meta.get('location', '')
            
            if current_location != next_location and current_location and next_location:
                transition_suggestions.append({
                    'type': 'location_change',
                    'position': i + 1,
                    'suggestion': f"Location change: {current_location} → {next_location}",
                    'recommendation': "Ensure smooth geographical transition"
                })
        
        transitions_report += f"**Transition Analysis:**\n"
        transitions_report += f"Total transitions analyzed: {len(self.scene_prose) - 1}\n"
        transitions_report += f"Recommendations: {len(transition_suggestions)}\n\n"
        
        # Group by transition type
        chapter_breaks = [t for t in transition_suggestions if t['type'] == 'chapter_break']
        pov_changes = [t for t in transition_suggestions if t['type'] == 'pov_change']
        location_changes = [t for t in transition_suggestions if t['type'] == 'location_change']
        
        if chapter_breaks:
            transitions_report += f"**Chapter Breaks ({len(chapter_breaks)}):**\n"
            for break_point in chapter_breaks:
                transitions_report += f"- After scene {break_point['position']}: {break_point['current_scene']}\n"
                transitions_report += f"  New chapter starts with: {break_point['next_scene']}\n\n"
        
        if pov_changes:
            transitions_report += f"**POV Changes ({len(pov_changes)}):**\n"
            for change in pov_changes:
                transitions_report += f"- Scene {change['position']+1}: {change['suggestion']}\n"
                transitions_report += f"  {change['recommendation']}\n\n"
        
        if location_changes:
            transitions_report += f"**Location Changes ({len(location_changes)}):**\n"
            for change in location_changes:
                transitions_report += f"- Scene {change['position']+1}: {change['suggestion']}\n"
                transitions_report += f"  {change['recommendation']}\n\n"
        
        if not transition_suggestions:
            transitions_report += f"✅ No major transition issues identified\n"
        
        return transitions_report
    
    def _format_manuscript(self) -> str:
        """Format complete manuscript in specified format"""
        if not self.scene_prose:
            return "Error: Scene prose required for manuscript formatting"
        
        # Determine chapter structure
        chapters_count = self.target_chapters if self.target_chapters > 0 else max(1, len(self.scene_prose) // 4)
        chapters = self._group_scenes_into_chapters(chapters_count)
        
        # Format based on specified format
        if self.manuscript_format == "markdown":
            formatted_text = self._format_as_markdown(chapters)
        elif self.manuscript_format == "docx":
            formatted_text = self._format_as_docx_structure(chapters)
        else:  # plain_text
            formatted_text = self._format_as_plain_text(chapters)
        
        word_count = len(' '.join(self.scene_prose).split())
        
        formatting_report = f"📄 MANUSCRIPT FORMATTING\n\n"
        formatting_report += f"Format: {self.manuscript_format}\n"
        formatting_report += f"Chapters: {len(chapters)}\n"
        formatting_report += f"Total words: ~{word_count:,}\n\n"
        
        formatting_report += f"**Sample Output:**\n"
        formatting_report += f"```{self.manuscript_format}\n"
        formatting_report += formatted_text[:500] + "...\n"
        formatting_report += f"```\n\n"
        
        formatting_report += f"✅ Manuscript formatted successfully in {self.manuscript_format} format\n"
        
        return formatting_report
    
    def _analyze_structure(self) -> str:
        """Analyze overall manuscript structure"""
        if not self.scene_prose:
            return "Error: Scene prose required for structure analysis"
        
        analysis = f"🏗️ MANUSCRIPT STRUCTURE ANALYSIS\n\n"
        
        # Basic metrics
        total_scenes = len(self.scene_prose)
        total_words = sum(len(prose.split()) for prose in self.scene_prose)
        avg_scene_length = total_words // total_scenes if total_scenes > 0 else 0
        
        analysis += f"**Overview:**\n"
        analysis += f"Total scenes: {total_scenes}\n"
        analysis += f"Total words: ~{total_words:,}\n"
        analysis += f"Average scene length: ~{avg_scene_length:,} words\n\n"
        
        # Chapter analysis
        chapters_count = self.target_chapters if self.target_chapters > 0 else max(1, total_scenes // 4)
        chapters = self._group_scenes_into_chapters(chapters_count)
        
        analysis += f"**Chapter Analysis:**\n"
        chapter_lengths = []
        for i, chapter in enumerate(chapters):
            chapter_words = sum(len(prose.split()) for prose in chapter['scenes'])
            chapter_lengths.append(chapter_words)
            analysis += f"Chapter {i+1}: {len(chapter['scenes'])} scenes, {chapter_words:,} words\n"
        
        # Structure assessment
        analysis += f"\n**Structure Assessment:**\n"
        
        # Check chapter balance
        if chapter_lengths:
            min_length = min(chapter_lengths)
            max_length = max(chapter_lengths)
            length_ratio = max_length / min_length if min_length > 0 else 0
            
            if length_ratio > 2.0:
                analysis += f"⚠️ Chapter lengths vary significantly ({min_length:,} to {max_length:,} words)\n"
            else:
                analysis += f"✅ Chapter lengths are reasonably balanced\n"
        
        # Check overall length for genre
        if total_words < 70000:
            analysis += f"📏 Length note: {total_words:,} words (typical novel range: 70,000-100,000)\n"
        elif total_words > 120000:
            analysis += f"📏 Length note: {total_words:,} words (longer than typical novel)\n"
        else:
            analysis += f"✅ Word count in typical novel range\n"
        
        # Scene length consistency
        scene_lengths = [len(prose.split()) for prose in self.scene_prose]
        if scene_lengths:
            scene_min = min(scene_lengths)
            scene_max = max(scene_lengths)
            
            if scene_max > scene_min * 3:
                analysis += f"⚠️ Scene lengths vary widely ({scene_min} to {scene_max} words)\n"
            else:
                analysis += f"✅ Scene lengths are consistent\n"
        
        return analysis
    
    def _group_scenes_into_chapters(self, chapters_count: int) -> list:
        """Group scenes into chapters based on metadata hints"""
        chapters = []
        
        if not self.scene_metadata:
            # Simple grouping without metadata
            scenes_per_chapter = len(self.scene_prose) // chapters_count
            remainder = len(self.scene_prose) % chapters_count
            
            start_idx = 0
            for i in range(chapters_count):
                end_idx = start_idx + scenes_per_chapter + (1 if i < remainder else 0)
                chapter_scenes = self.scene_prose[start_idx:end_idx]
                
                chapters.append({
                    'scenes': chapter_scenes,
                    'scene_indices': list(range(start_idx, end_idx))
                })
                start_idx = end_idx
        
        else:
            # Use chapter hints from metadata
            current_chapter = 1
            current_scenes = []
            current_indices = []
            
            for i, (prose, metadata) in enumerate(zip(self.scene_prose, self.scene_metadata)):
                chapter_hint = metadata.get('chapter_hint', current_chapter)
                
                if chapter_hint > current_chapter and current_scenes:
                    # Start new chapter
                    chapters.append({
                        'scenes': current_scenes,
                        'scene_indices': current_indices
                    })
                    current_scenes = [prose]
                    current_indices = [i]
                    current_chapter = chapter_hint
                else:
                    current_scenes.append(prose)
                    current_indices.append(i)
            
            # Add final chapter
            if current_scenes:
                chapters.append({
                    'scenes': current_scenes,
                    'scene_indices': current_indices
                })
        
        return chapters
    
    def _check_chapter_balance(self, chapters: list) -> list:
        """Check for chapter balance issues"""
        issues = []
        
        chapter_lengths = [sum(len(prose.split()) for prose in chapter['scenes']) for chapter in chapters]
        
        if not chapter_lengths:
            return issues
        
        avg_length = sum(chapter_lengths) / len(chapter_lengths)
        
        for i, length in enumerate(chapter_lengths):
            if length < avg_length * 0.5:
                issues.append(f"Chapter {i+1} is significantly shorter than average ({length:,} vs {avg_length:,.0f} words)")
            elif length > avg_length * 1.8:
                issues.append(f"Chapter {i+1} is significantly longer than average ({length:,} vs {avg_length:,.0f} words)")
        
        return issues
    
    def _format_as_markdown(self, chapters: list) -> str:
        """Format manuscript as Markdown"""
        formatted = "# Novel Title\n\n"
        
        for i, chapter in enumerate(chapters):
            formatted += f"## Chapter {i + 1}\n\n"
            
            for j, scene_prose in enumerate(chapter['scenes']):
                if j > 0:
                    formatted += "\n---\n\n"  # Scene separator
                formatted += scene_prose + "\n\n"
        
        return formatted
    
    def _format_as_plain_text(self, chapters: list) -> str:
        """Format manuscript as plain text"""
        formatted = "NOVEL TITLE\n" + "=" * 50 + "\n\n"
        
        for i, chapter in enumerate(chapters):
            formatted += f"CHAPTER {i + 1}\n" + "-" * 20 + "\n\n"
            
            for scene_prose in chapter['scenes']:
                formatted += scene_prose + "\n\n"
        
        return formatted
    
    def _format_as_docx_structure(self, chapters: list) -> str:
        """Format manuscript structure for DOCX export"""
        structure = {
            'title': 'Novel Title',
            'chapters': []
        }
        
        for i, chapter in enumerate(chapters):
            chapter_data = {
                'number': i + 1,
                'title': f'Chapter {i + 1}',
                'scenes': chapter['scenes']
            }
            structure['chapters'].append(chapter_data)
        
        return f"DOCX Structure: {len(structure['chapters'])} chapters, ready for document export"