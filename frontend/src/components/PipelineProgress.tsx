import React from 'react';
import { CheckCircle, Circle, Loader, AlertCircle, Clock } from 'lucide-react';
import { NovelProject } from '../types';

interface PipelineProgressProps {
  currentStep: number;
  isGenerating: boolean;
  project: NovelProject;
}

const PIPELINE_STEPS = [
  { 
    id: 0, 
    name: 'First Things First', 
    description: 'Market position & audience',
    estimatedTime: '30s'
  },
  { 
    id: 1, 
    name: 'One Sentence Summary', 
    description: 'Logline (max 25 words)',
    estimatedTime: '45s'
  },
  { 
    id: 2, 
    name: 'One Paragraph', 
    description: '5 sentences + moral premise',
    estimatedTime: '1m'
  },
  { 
    id: 3, 
    name: 'Character Summaries', 
    description: 'Goals, conflicts, epiphanies',
    estimatedTime: '2m'
  },
  { 
    id: 4, 
    name: 'One Page Synopsis', 
    description: 'Expand paragraph to page',
    estimatedTime: '2m'
  },
  { 
    id: 5, 
    name: 'Character Synopses', 
    description: 'Deep character development',
    estimatedTime: '3m'
  },
  { 
    id: 6, 
    name: 'Long Synopsis', 
    description: '4-5 pages full outline',
    estimatedTime: '5m'
  },
  { 
    id: 7, 
    name: 'Character Bibles', 
    description: 'Complete character details',
    estimatedTime: '4m'
  },
  { 
    id: 8, 
    name: 'Scene List', 
    description: 'All scenes with POV & conflict',
    estimatedTime: '5m'
  },
  { 
    id: 9, 
    name: 'Scene Briefs', 
    description: 'Proactive/Reactive triads',
    estimatedTime: '10m'
  },
  { 
    id: 10, 
    name: 'First Draft', 
    description: 'Generate full manuscript',
    estimatedTime: '30m'
  }
];

export default function PipelineProgress({ currentStep, isGenerating, project }: PipelineProgressProps) {
  const getStepStatus = (stepId: number) => {
    if (stepId < currentStep) return 'completed';
    if (stepId === currentStep && isGenerating) return 'processing';
    if (stepId === currentStep) return 'current';
    return 'pending';
  };

  const calculateTotalTime = () => {
    const totalMinutes = PIPELINE_STEPS.reduce((acc, step) => {
      const time = step.estimatedTime;
      if (time.includes('m')) {
        return acc + parseInt(time);
      } else if (time.includes('s')) {
        return acc + parseInt(time) / 60;
      }
      return acc;
    }, 0);
    return Math.round(totalMinutes);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-4 py-3">
        <h3 className="text-lg font-semibold text-white">Generation Pipeline</h3>
        <p className="text-indigo-100 text-sm mt-1">
          Estimated total time: ~{calculateTotalTime()} minutes
        </p>
      </div>
      
      <div className="p-4">
        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{Math.round((currentStep / 10) * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-indigo-600 to-purple-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${(currentStep / 10) * 100}%` }}
            />
          </div>
        </div>

        {/* Steps List */}
        <div className="space-y-3">
          {PIPELINE_STEPS.map((step, index) => {
            const status = getStepStatus(step.id);
            
            return (
              <div 
                key={step.id}
                className={`flex items-start space-x-3 p-3 rounded-lg transition-all ${
                  status === 'processing' 
                    ? 'bg-indigo-50 border border-indigo-200' 
                    : status === 'completed'
                    ? 'bg-green-50 border border-green-200'
                    : status === 'current'
                    ? 'bg-yellow-50 border border-yellow-200'
                    : 'bg-gray-50 border border-gray-200'
                }`}
              >
                <div className="flex-shrink-0 mt-0.5">
                  {status === 'completed' && (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  )}
                  {status === 'processing' && (
                    <Loader className="w-5 h-5 text-indigo-600 animate-spin" />
                  )}
                  {status === 'current' && (
                    <Circle className="w-5 h-5 text-yellow-600" />
                  )}
                  {status === 'pending' && (
                    <Circle className="w-5 h-5 text-gray-400" />
                  )}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className={`text-sm font-medium ${
                      status === 'pending' ? 'text-gray-500' : 'text-gray-900'
                    }`}>
                      Step {step.id}: {step.name}
                    </h4>
                    <span className="text-xs text-gray-500 flex items-center">
                      <Clock className="w-3 h-3 mr-1" />
                      {step.estimatedTime}
                    </span>
                  </div>
                  <p className={`text-xs mt-1 ${
                    status === 'pending' ? 'text-gray-400' : 'text-gray-600'
                  }`}>
                    {step.description}
                  </p>
                  
                  {status === 'processing' && (
                    <div className="mt-2">
                      <div className="w-full bg-indigo-100 rounded-full h-1">
                        <div className="bg-indigo-600 h-1 rounded-full animate-pulse" style={{ width: '60%' }} />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Status Messages */}
        {isGenerating && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start">
              <AlertCircle className="w-4 h-4 text-blue-600 mt-0.5 mr-2 flex-shrink-0" />
              <div className="text-xs text-blue-800">
                <p className="font-medium">Generation in Progress</p>
                <p className="mt-1">
                  Each step validates before proceeding. Failures will trigger automatic revision.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Project Info */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <dl className="space-y-2">
            <div className="flex justify-between text-xs">
              <dt className="text-gray-500">Target Words:</dt>
              <dd className="font-medium text-gray-900">
                {project.targetWordCount?.toLocaleString()}
              </dd>
            </div>
            <div className="flex justify-between text-xs">
              <dt className="text-gray-500">Category:</dt>
              <dd className="font-medium text-gray-900">{project.category}</dd>
            </div>
            <div className="flex justify-between text-xs">
              <dt className="text-gray-500">Type:</dt>
              <dd className="font-medium text-gray-900 capitalize">
                {project.storyType?.replace('-', ' ')}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
}