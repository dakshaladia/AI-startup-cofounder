'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  LightBulbIcon, 
  ChartBarIcon, 
  CpuChipIcon, 
  DocumentTextIcon,
  ArrowRightIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'
import UploadArea from './components/UploadArea'
import IdeaGenerator from './components/IdeaGenerator'
import IdeaTimeline from './components/IdeaTimeline'
import ArtifactViewer from './components/ArtifactViewer'

export default function HomePage() {
  const [activeTab, setActiveTab] = useState('generate')
  const [generatedIdeas, setGeneratedIdeas] = useState([])
  const [isGenerating, setIsGenerating] = useState(false)

  const handleIdeaGeneration = async (topic: string, constraints: any) => {
    setIsGenerating(true)
    try {
      // Mock idea generation - replace with actual API call
      const mockIdeas = [
        {
          id: '1',
          title: 'AI-Powered Personal Finance Assistant',
          description: 'An intelligent financial advisor that learns from user behavior to provide personalized investment recommendations.',
          market_analysis: 'Large and growing market with high demand for personalized financial services.',
          feasibility_score: 0.8,
          novelty_score: 0.7,
          overall_score: 0.75,
          created_at: new Date().toISOString()
        },
        {
          id: '2',
          title: 'Blockchain-Based Supply Chain Transparency',
          description: 'A decentralized platform that provides end-to-end visibility and traceability for supply chains.',
          market_analysis: 'Emerging market with increasing regulatory requirements for transparency.',
          feasibility_score: 0.6,
          novelty_score: 0.9,
          overall_score: 0.75
        }
      ]
      
      setGeneratedIdeas(mockIdeas)
    } catch (error) {
      console.error('Failed to generate ideas:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  const tabs = [
    { id: 'generate', name: 'Generate Ideas', icon: LightBulbIcon },
    { id: 'upload', name: 'Upload Data', icon: DocumentTextIcon },
    { id: 'timeline', name: 'Idea Timeline', icon: ChartBarIcon },
    { id: 'artifacts', name: 'Artifacts', icon: CpuChipIcon },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <SparklesIcon className="h-8 w-8 text-primary-600" />
              <h1 className="ml-2 text-xl font-bold text-gray-900">
                AI Startup Co-Founder
              </h1>
            </div>
            <nav className="flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <tab.icon className="h-4 w-4 mr-2" />
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'generate' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Generate Startup Ideas
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Use our AI-powered multi-agent pipeline to generate innovative startup ideas
                based on market analysis, feasibility assessment, and novelty detection.
              </p>
            </div>
            
            <IdeaGenerator 
              onGenerate={handleIdeaGeneration}
              isGenerating={isGenerating}
            />
            
            {generatedIdeas.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="mt-8"
              >
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  Generated Ideas
                </h3>
                <div className="grid gap-6 md:grid-cols-2">
                  {generatedIdeas.map((idea) => (
                    <div key={idea.id} className="card">
                      <div className="flex justify-between items-start mb-4">
                        <h4 className="text-lg font-semibold text-gray-900">
                          {idea.title}
                        </h4>
                        <div className="flex space-x-2">
                          <span className="badge badge-primary">
                            Score: {idea.overall_score}
                          </span>
                        </div>
                      </div>
                      <p className="text-gray-600 mb-4">{idea.description}</p>
                      <div className="flex justify-between items-center">
                        <div className="flex space-x-4 text-sm text-gray-500">
                          <span>Feasibility: {idea.feasibility_score}</span>
                          <span>Novelty: {idea.novelty_score}</span>
                        </div>
                        <button className="btn btn-primary text-sm">
                          View Details
                          <ArrowRightIcon className="h-4 w-4 ml-1" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </motion.div>
        )}

        {activeTab === 'upload' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Upload Data
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Upload documents, images, and other data to enhance idea generation
                with multimodal analysis and context.
              </p>
            </div>
            
            <UploadArea />
          </motion.div>
        )}

        {activeTab === 'timeline' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Idea Timeline
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Track the evolution of your ideas through the multi-agent pipeline
                and see how they improve over time.
              </p>
            </div>
            
            <IdeaTimeline ideas={generatedIdeas} />
          </motion.div>
        )}

        {activeTab === 'artifacts' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Artifacts
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                View generated mockups, presentations, and other artifacts
                created by the AI system.
              </p>
            </div>
            
            <ArtifactViewer />
          </motion.div>
        )}
      </main>
    </div>
  )
}
