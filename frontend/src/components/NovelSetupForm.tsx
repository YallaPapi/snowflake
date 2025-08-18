import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { NovelProject } from '../types';
import { 
  BookOpen, Target, Users, Sparkles, TrendingUp, 
  AlertCircle, ChevronRight, Info, Save, Play
} from 'lucide-react';

interface NovelSetupFormProps {
  onSubmit: (data: NovelProject) => void;
}

const CATEGORIES = [
  'Romantic Suspense', 'Contemporary Romance', 'Historical Romance', 
  'Epic Fantasy', 'Urban Fantasy', 'Dark Fantasy',
  'Psychological Thriller', 'Medical Thriller', 'Legal Thriller',
  'Cozy Mystery', 'Police Procedural', 'Hard-Boiled Mystery',
  'Science Fiction', 'Space Opera', 'Dystopian',
  'Contemporary Women\'s Fiction', 'Literary Fiction', 'Historical Fiction'
];

const STORY_KINDS = [
  'character-driven', 
  'plot-driven'
];

const TROPE_SUGGESTIONS = [
  'enemies-to-lovers', 'friends-to-lovers', 'second-chance',
  'fake-relationship', 'mentor-betrayal', 'heist', 'whodunit',
  'locked-room', 'fish-out-of-water', 'chosen-one', 'quest',
  'revenge', 'redemption', 'underdog', 'coming-of-age'
];

const SATISFIER_SUGGESTIONS = [
  'slow-burn', 'betrayal-twist', 'forced-proximity', 'puzzle',
  'red-herrings', 'found-family', 'courtroom-drama', 'ticking-clock',
  'power-reversal', 'identity-reveal', 'multiple-POV', 'dual-timeline'
];

export default function NovelSetupForm({ onSubmit }: NovelSetupFormProps) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [selectedTropes, setSelectedTropes] = useState<string[]>([]);
  const [selectedSatisfiers, setSelectedSatisfiers] = useState<string[]>([]);
  
  const { register, handleSubmit, watch, formState: { errors }, setValue } = useForm<NovelProject>();
  
  const watchCategory = watch('category');
  const watchStoryBrief = watch('storyBrief');

  const handleTropeToggle = (trope: string) => {
    setSelectedTropes(prev => 
      prev.includes(trope) 
        ? prev.filter(t => t !== trope)
        : [...prev, trope]
    );
  };

  const handleSatisfierToggle = (satisfier: string) => {
    if (selectedSatisfiers.includes(satisfier)) {
      setSelectedSatisfiers(prev => prev.filter(s => s !== satisfier));
    } else if (selectedSatisfiers.length < 5) {
      setSelectedSatisfiers(prev => [...prev, satisfier]);
    }
  };

  const onFormSubmit = (data: NovelProject) => {
    // Construct story_kind with selected tropes
    const storyKindWithTropes = selectedTropes.length > 0
      ? `${data.storyPromise} featuring ${selectedTropes.join(' and ')}.`
      : data.storyPromise;
    
    // Construct audience_delight with selected satisfiers
    const audienceDelight = selectedSatisfiers.join(', ') + '.';
    
    const projectData = {
      ...data,
      story_kind: storyKindWithTropes,
      audience_delight: audienceDelight,
      projectId: `novel-${Date.now()}`,
      createdAt: new Date().toISOString()
    };
    
    onSubmit(projectData);
  };

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-8">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 px-6 py-4">
          <h2 className="text-2xl font-bold text-white">Novel Project Setup</h2>
          <p className="text-purple-100 mt-1">
            Configure your novel generation parameters following the Snowflake Method
          </p>
        </div>

        <div className="p-6 space-y-6">
          {/* Project Basics */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <BookOpen className="w-5 h-5 mr-2 text-purple-600" />
              Project Information
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Project Name *
                </label>
                <input
                  type="text"
                  {...register('projectName', { required: 'Project name is required' })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="My Amazing Novel"
                />
                {errors.projectName && (
                  <p className="mt-1 text-sm text-red-600">{errors.projectName.message}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Target Word Count *
                </label>
                <input
                  type="number"
                  {...register('targetWordCount', { 
                    required: 'Word count is required',
                    min: { value: 50000, message: 'Minimum 50,000 words for a novel' },
                    max: { value: 150000, message: 'Maximum 150,000 words' }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="90000"
                  defaultValue={90000}
                />
                {errors.targetWordCount && (
                  <p className="mt-1 text-sm text-red-600">{errors.targetWordCount.message}</p>
                )}
              </div>
            </div>
          </div>

          {/* Story Brief */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Sparkles className="w-5 h-5 mr-2 text-purple-600" />
              Story Concept
            </h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Story Brief *
                <span className="ml-2 text-xs text-gray-500">
                  (One paragraph describing your novel idea)
                </span>
              </label>
              <textarea
                {...register('storyBrief', { 
                  required: 'Story brief is required',
                  minLength: { value: 50, message: 'Brief should be at least 50 characters' }
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                rows={4}
                placeholder="A detective investigating a murder case falls in love with the prime suspect. As evidence mounts against her lover, she must choose between her duty to justice and her heart, all while uncovering a conspiracy that goes deeper than she imagined..."
              />
              {errors.storyBrief && (
                <p className="mt-1 text-sm text-red-600">{errors.storyBrief.message}</p>
              )}
            </div>
          </div>

          {/* Step 0: First Things First */}
          <div className="space-y-4 border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Target className="w-5 h-5 mr-2 text-purple-600" />
              Market Position (Step 0: First Things First)
            </h3>
            
            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category/Genre *
                <span className="ml-2 text-xs text-gray-500">
                  (Real bookstore shelf label)
                </span>
              </label>
              <select
                {...register('category', { required: 'Category is required' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">Select a category...</option>
                {CATEGORIES.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
              {errors.category && (
                <p className="mt-1 text-sm text-red-600">{errors.category.message}</p>
              )}
            </div>

            {/* Story Kind */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Story Type *
              </label>
              <div className="flex space-x-4">
                {STORY_KINDS.map(kind => (
                  <label key={kind} className="flex items-center">
                    <input
                      type="radio"
                      value={kind}
                      {...register('storyType', { required: 'Story type is required' })}
                      className="mr-2 text-purple-600 focus:ring-purple-500"
                    />
                    <span className="text-sm capitalize">{kind.replace('-', ' ')}</span>
                  </label>
                ))}
              </div>
              {errors.storyType && (
                <p className="mt-1 text-sm text-red-600">{errors.storyType.message}</p>
              )}
            </div>

            {/* Story Promise with Tropes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Core Story Promise *
                <span className="ml-2 text-xs text-gray-500">
                  (One sentence central promise)
                </span>
              </label>
              <input
                type="text"
                {...register('storyPromise', { 
                  required: 'Story promise is required',
                  maxLength: { value: 150, message: 'Keep under 150 characters' }
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="A detective must prove the innocence of the suspect she's falling for"
              />
              {errors.storyPromise && (
                <p className="mt-1 text-sm text-red-600">{errors.storyPromise.message}</p>
              )}
              
              {/* Trope Selection */}
              <div className="mt-3">
                <p className="text-sm font-medium text-gray-700 mb-2">
                  Select Tropes (Required - choose at least 1):
                </p>
                <div className="flex flex-wrap gap-2">
                  {TROPE_SUGGESTIONS.map(trope => (
                    <button
                      key={trope}
                      type="button"
                      onClick={() => handleTropeToggle(trope)}
                      className={`px-3 py-1 text-sm rounded-full transition-colors ${
                        selectedTropes.includes(trope)
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {trope}
                    </button>
                  ))}
                </div>
                {selectedTropes.length === 0 && (
                  <p className="mt-1 text-sm text-amber-600 flex items-center">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    At least one trope is required
                  </p>
                )}
              </div>
            </div>

            {/* Audience Delight Satisfiers */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Audience Satisfiers
                <span className="ml-2 text-xs text-gray-500">
                  (Select 3-5 concrete satisfiers)
                </span>
              </label>
              <div className="flex flex-wrap gap-2">
                {SATISFIER_SUGGESTIONS.map(satisfier => (
                  <button
                    key={satisfier}
                    type="button"
                    onClick={() => handleSatisfierToggle(satisfier)}
                    disabled={!selectedSatisfiers.includes(satisfier) && selectedSatisfiers.length >= 5}
                    className={`px-3 py-1 text-sm rounded-full transition-colors ${
                      selectedSatisfiers.includes(satisfier)
                        ? 'bg-indigo-600 text-white'
                        : selectedSatisfiers.length >= 5
                        ? 'bg-gray-50 text-gray-400 cursor-not-allowed'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {satisfier}
                  </button>
                ))}
              </div>
              <p className="mt-2 text-sm text-gray-600">
                Selected: {selectedSatisfiers.length}/5
                {selectedSatisfiers.length < 3 && (
                  <span className="text-amber-600 ml-2">
                    (Need at least 3)
                  </span>
                )}
              </p>
            </div>
          </div>

          {/* Advanced Options */}
          <div className="border-t pt-6">
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center text-sm font-medium text-gray-700 hover:text-gray-900"
            >
              <ChevronRight className={`w-4 h-4 mr-1 transition-transform ${showAdvanced ? 'rotate-90' : ''}`} />
              Advanced Configuration
            </button>
            
            {showAdvanced && (
              <div className="mt-4 space-y-4 pl-5">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Author Name
                  </label>
                  <input
                    type="text"
                    {...register('authorName')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="Your name (optional)"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    AI Model Temperature
                    <span className="ml-2 text-xs text-gray-500">
                      (0.1 = focused, 0.9 = creative)
                    </span>
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0.1"
                    max="0.9"
                    {...register('temperature')}
                    defaultValue={0.3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                
                <div>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      {...register('validateStrictly')}
                      defaultChecked={true}
                      className="mr-2 text-purple-600 focus:ring-purple-500"
                    />
                    <span className="text-sm text-gray-700">
                      Strict validation mode (recommended)
                    </span>
                  </label>
                </div>
              </div>
            )}
          </div>

          {/* Validation Status */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start">
              <Info className="w-5 h-5 text-blue-600 mt-0.5 mr-2 flex-shrink-0" />
              <div className="text-sm text-blue-800">
                <p className="font-medium mb-1">Pre-Generation Validation</p>
                <ul className="space-y-1 text-xs">
                  <li className={watchCategory ? 'line-through' : ''}>
                    ✓ Category must be a real bookstore shelf label
                  </li>
                  <li className={selectedTropes.length > 0 ? 'line-through' : ''}>
                    ✓ Story must include at least one trope noun
                  </li>
                  <li className={selectedSatisfiers.length >= 3 ? 'line-through' : ''}>
                    ✓ Audience delight needs 3-5 concrete satisfiers
                  </li>
                </ul>
              </div>
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="flex justify-between items-center pt-4">
            <button
              type="button"
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors flex items-center"
            >
              <Save className="w-4 h-4 mr-2" />
              Save Draft
            </button>
            
            <button
              type="submit"
              disabled={selectedTropes.length === 0 || selectedSatisfiers.length < 3}
              className={`px-6 py-2 rounded-md font-medium transition-colors flex items-center ${
                selectedTropes.length === 0 || selectedSatisfiers.length < 3
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700'
              }`}
            >
              <Play className="w-4 h-4 mr-2" />
              Start Generation
            </button>
          </div>
        </div>
      </div>
    </form>
  );
}