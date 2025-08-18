export interface NovelProject {
  projectId: string;
  projectName: string;
  authorName?: string;
  createdAt: string;
  
  // Story Brief
  storyBrief: string;
  targetWordCount: number;
  
  // Step 0: First Things First
  category: string;
  storyType: 'character-driven' | 'plot-driven';
  storyPromise: string;
  story_kind?: string;  // Generated with tropes
  audience_delight?: string;  // Generated with satisfiers
  
  // Configuration
  temperature?: number;
  validateStrictly?: boolean;
  
  // Pipeline State
  currentStep?: number;
  artifacts?: Artifact[];
  status?: 'setup' | 'generating' | 'completed' | 'failed';
}

export interface Artifact {
  step: number;
  name: string;
  version: string;
  createdAt: string;
  content: any;
  metadata: {
    projectId: string;
    modelName: string;
    promptHash: string;
    validatorVersion: string;
    temperature: number;
    seed?: number;
  };
  validationStatus: 'pending' | 'valid' | 'invalid';
  validationErrors?: string[];
  validationWarnings?: string[];
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings?: string[];
  suggestions?: string[];
}