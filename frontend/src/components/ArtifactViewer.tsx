import React, { useState } from 'react';
import { 
  FileText, Download, Eye, Code, Check, X, 
  AlertTriangle, ChevronDown, ChevronRight 
} from 'lucide-react';
import { NovelProject } from '../types';

interface ArtifactViewerProps {
  project: NovelProject;
  currentStep: number;
}

interface Artifact {
  step: number;
  name: string;
  status: 'pending' | 'valid' | 'invalid' | 'processing';
  content?: any;
  errors?: string[];
  warnings?: string[];
}

// Mock artifacts for demonstration
const mockArtifacts: Artifact[] = [
  {
    step: 0,
    name: 'First Things First',
    status: 'valid',
    content: {
      category: 'Romantic Suspense',
      story_kind: 'Enemies-to-lovers with espionage backdrop.',
      audience_delight: 'Undercover reveals, forced proximity, betrayal twist, heroic sacrifice ending.'
    }
  }
];

export default function ArtifactViewer({ project, currentStep }: ArtifactViewerProps) {
  const [selectedArtifact, setSelectedArtifact] = useState<number>(0);
  const [viewMode, setViewMode] = useState<'formatted' | 'json'>('formatted');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['current']));

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const renderArtifactContent = (artifact: Artifact) => {
    if (!artifact.content) return null;

    if (viewMode === 'json') {
      return (
        <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-xs">
          {JSON.stringify(artifact.content, null, 2)}
        </pre>
      );
    }

    // Formatted view based on step
    switch (artifact.step) {
      case 0: // First Things First
        return (
          <div className="space-y-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Category</h4>
              <p className="text-gray-900">{artifact.content.category}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Story Kind</h4>
              <p className="text-gray-900">{artifact.content.story_kind}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Audience Delight</h4>
              <p className="text-gray-900">{artifact.content.audience_delight}</p>
            </div>
          </div>
        );
      
      default:
        return (
          <div className="text-gray-500 text-center py-8">
            Artifact viewer for step {artifact.step} not yet implemented
          </div>
        );
    }
  };

  const currentArtifact = mockArtifacts[selectedArtifact] || mockArtifacts[0];

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 px-6 py-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-xl font-semibold text-white">Artifact Viewer</h3>
            <p className="text-purple-100 text-sm mt-1">
              Step {currentArtifact.step}: {currentArtifact.name}
            </p>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setViewMode(viewMode === 'formatted' ? 'json' : 'formatted')}
              className="p-2 bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
              title="Toggle view mode"
            >
              {viewMode === 'formatted' ? <Code className="w-4 h-4 text-white" /> : <Eye className="w-4 h-4 text-white" />}
            </button>
            <button
              className="p-2 bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
              title="Download artifact"
            >
              <Download className="w-4 h-4 text-white" />
            </button>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Sidebar - Artifact List */}
        <div className="w-64 bg-gray-50 border-r border-gray-200">
          <div className="p-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Generated Artifacts</h4>
            
            {/* Current Step */}
            <div className="mb-4">
              <button
                onClick={() => toggleSection('current')}
                className="flex items-center justify-between w-full text-left text-sm font-medium text-gray-700 mb-2"
              >
                <span>Current Step</span>
                {expandedSections.has('current') ? 
                  <ChevronDown className="w-4 h-4" /> : 
                  <ChevronRight className="w-4 h-4" />
                }
              </button>
              {expandedSections.has('current') && (
                <div className="space-y-1">
                  {mockArtifacts.filter(a => a.step <= currentStep).map((artifact, idx) => (
                    <button
                      key={idx}
                      onClick={() => setSelectedArtifact(idx)}
                      className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-colors flex items-center justify-between ${
                        selectedArtifact === idx
                          ? 'bg-white border border-purple-300 text-purple-700'
                          : 'hover:bg-gray-100 text-gray-600'
                      }`}
                    >
                      <span className="flex items-center">
                        <FileText className="w-3 h-3 mr-2" />
                        Step {artifact.step}
                      </span>
                      {artifact.status === 'valid' && <Check className="w-3 h-3 text-green-600" />}
                      {artifact.status === 'invalid' && <X className="w-3 h-3 text-red-600" />}
                      {artifact.status === 'processing' && <div className="w-3 h-3 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Pending Steps */}
            <div>
              <button
                onClick={() => toggleSection('pending')}
                className="flex items-center justify-between w-full text-left text-sm font-medium text-gray-700 mb-2"
              >
                <span>Pending Steps</span>
                {expandedSections.has('pending') ? 
                  <ChevronDown className="w-4 h-4" /> : 
                  <ChevronRight className="w-4 h-4" />
                }
              </button>
              {expandedSections.has('pending') && (
                <div className="space-y-1">
                  {Array.from({ length: 11 - currentStep - 1 }, (_, i) => currentStep + i + 1).map(step => (
                    <div
                      key={step}
                      className="px-3 py-2 text-xs text-gray-400 flex items-center"
                    >
                      <FileText className="w-3 h-3 mr-2" />
                      Step {step}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 p-6">
          {/* Validation Status */}
          {currentArtifact.status && (
            <div className={`mb-4 p-3 rounded-lg flex items-start ${
              currentArtifact.status === 'valid' 
                ? 'bg-green-50 border border-green-200'
                : currentArtifact.status === 'invalid'
                ? 'bg-red-50 border border-red-200'
                : currentArtifact.status === 'processing'
                ? 'bg-blue-50 border border-blue-200'
                : 'bg-gray-50 border border-gray-200'
            }`}>
              {currentArtifact.status === 'valid' && (
                <>
                  <Check className="w-5 h-5 text-green-600 mt-0.5 mr-2 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-green-900">Validation Passed</p>
                    <p className="text-xs text-green-700 mt-1">
                      All requirements met according to Snowflake Method
                    </p>
                  </div>
                </>
              )}
              {currentArtifact.status === 'invalid' && (
                <>
                  <X className="w-5 h-5 text-red-600 mt-0.5 mr-2 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-red-900">Validation Failed</p>
                    {currentArtifact.errors && (
                      <ul className="text-xs text-red-700 mt-1 space-y-1">
                        {currentArtifact.errors.map((error, idx) => (
                          <li key={idx}>• {error}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                </>
              )}
              {currentArtifact.status === 'processing' && (
                <>
                  <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mt-0.5 mr-2 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-blue-900">Generating...</p>
                    <p className="text-xs text-blue-700 mt-1">
                      AI model is generating this artifact
                    </p>
                  </div>
                </>
              )}
            </div>
          )}

          {/* Warnings */}
          {currentArtifact.warnings && currentArtifact.warnings.length > 0 && (
            <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <div className="flex items-start">
                <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 mr-2 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-amber-900">Warnings</p>
                  <ul className="text-xs text-amber-700 mt-1 space-y-1">
                    {currentArtifact.warnings.map((warning, idx) => (
                      <li key={idx}>• {warning}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Artifact Content */}
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <div className="bg-gray-100 px-4 py-2 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h4 className="text-sm font-medium text-gray-700">
                  Artifact Content
                </h4>
                <span className="text-xs text-gray-500">
                  {viewMode === 'formatted' ? 'Formatted View' : 'JSON View'}
                </span>
              </div>
            </div>
            <div className="p-4">
              {currentArtifact.content ? (
                renderArtifactContent(currentArtifact)
              ) : (
                <div className="text-center py-12 text-gray-400">
                  <FileText className="w-12 h-12 mx-auto mb-3" />
                  <p className="text-sm">No content generated yet</p>
                </div>
              )}
            </div>
          </div>

          {/* Metadata */}
          <div className="mt-4 text-xs text-gray-500">
            <dl className="flex flex-wrap gap-x-6 gap-y-2">
              <div>
                <dt className="inline font-medium">Generated:</dt>
                <dd className="inline ml-1">{new Date().toLocaleString()}</dd>
              </div>
              <div>
                <dt className="inline font-medium">Version:</dt>
                <dd className="inline ml-1">1.0.0</dd>
              </div>
              <div>
                <dt className="inline font-medium">Model:</dt>
                <dd className="inline ml-1">claude-3-5-sonnet</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}