import React, { useState } from 'react';
import NovelSetupForm from './components/NovelSetupForm';
import PipelineProgress from './components/PipelineProgress';
import ArtifactViewer from './components/ArtifactViewer';
import { NovelProject } from './types';
import './App.css';

function App() {
  const [activeProject, setActiveProject] = useState<NovelProject | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleProjectStart = (project: NovelProject) => {
    setActiveProject(project);
    setIsGenerating(true);
    // Start generation pipeline
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                Snowflake Novel Generator
              </h1>
              <span className="ml-3 text-sm text-gray-500">
                Systematic Novel Generation Engine
              </span>
            </div>
            <div className="flex items-center space-x-4">
              {activeProject && (
                <span className="text-sm text-gray-600">
                  Project: <span className="font-medium">{activeProject.projectName}</span>
                </span>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!activeProject ? (
          <NovelSetupForm onSubmit={handleProjectStart} />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <ArtifactViewer 
                project={activeProject} 
                currentStep={currentStep}
              />
            </div>
            <div>
              <PipelineProgress 
                currentStep={currentStep}
                isGenerating={isGenerating}
                project={activeProject}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;