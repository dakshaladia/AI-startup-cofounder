'use client'

import { useState, useEffect } from 'react'
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
  const [selectedIdea, setSelectedIdea] = useState(null)
  const [showIterateDialog, setShowIterateDialog] = useState(false)
  const [iterateFeedback, setIterateFeedback] = useState('')
  const [iterationType, setIterationType] = useState('synthesis')
  const [isIterating, setIsIterating] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  
  // Model settings for each agent
  const [modelSettings, setModelSettings] = useState({
    market_analyst: 'gemini-2.0-flash-lite',
    idea_generator: 'gemini-2.0-flash-lite',
    critic: 'gemini-2.0-flash-lite',
    pm_refiner: 'gemini-2.0-flash-lite',
    synthesizer: 'gemini-2.0-flash-lite'
  })

  // Load settings from localStorage on mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('modelSettings')
    if (savedSettings) {
      setModelSettings(JSON.parse(savedSettings))
    }
  }, [])

  // Save settings to localStorage when they change
  const saveModelSettings = (newSettings: any) => {
    setModelSettings(newSettings)
    localStorage.setItem('modelSettings', JSON.stringify(newSettings))
  }

  const handleIdeaGeneration = async (topic: string, constraints: any) => {
    setIsGenerating(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      const response = await fetch(`${apiUrl}/api/v1/ideas/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic,
          constraints,
          num_ideas: 2,
          model_settings: modelSettings  // Pass model settings to backend
        })
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()
      
      // Transform the API response to match our UI structure
      const ideas = data.ideas.map((idea: any) => ({
        ...idea,
        created_at: idea.created_at || new Date().toISOString()
      }))
      
      setGeneratedIdeas(ideas)
    } catch (error) {
      console.error('Failed to generate ideas:', error)
      alert('Failed to generate ideas. Please make sure the backend is running.')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleIterateIdea = async () => {
    if (!selectedIdea || !iterateFeedback.trim()) {
      alert('Please provide feedback for iteration')
      return
    }

    setIsIterating(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      const response = await fetch(`${apiUrl}/api/v1/ideas/iterate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          idea_id: selectedIdea.id,
          feedback: iterateFeedback,
          iteration_type: iterationType,
          focus_areas: [],
          constraints: {},
          model_settings: modelSettings  // Pass model settings to backend
        })
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()
      
      // Update the idea in the list
      setGeneratedIdeas(prev => prev.map(idea => 
        idea.id === selectedIdea.id ? { ...idea, ...data.updated_idea } : idea
      ))
      
      // Update selected idea
      setSelectedIdea({ ...selectedIdea, ...data.updated_idea })
      
      // Close dialog and reset
      setShowIterateDialog(false)
      setIterateFeedback('')
      
      alert('Idea iterated successfully!')
    } catch (error) {
      console.error('Failed to iterate idea:', error)
      alert('Failed to iterate idea. Please try again.')
    } finally {
      setIsIterating(false)
    }
  }

  const tabs = [
    { id: 'generate', name: 'Generate Ideas', icon: LightBulbIcon },
    // { id: 'upload', name: 'Upload Data', icon: DocumentTextIcon },
    // { id: 'timeline', name: 'Idea Timeline', icon: ChartBarIcon },
    // { id: 'artifacts', name: 'Artifacts', icon: CpuChipIcon },
  ]

  return (
    <div className="min-h-screen bg-white overflow-hidden">
      {/* Header */}
      <header className="bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <div className="flex items-center">
              <h1 className="text-2xl font-semibold text-gray-900 tracking-tight">
                Idea Generalist
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <nav className="flex space-x-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`px-4 py-2 text-sm font-medium transition-all duration-200 ${
                      activeTab === tab.id
                        ? 'text-gray-900'
                        : 'text-gray-500 hover:text-gray-900'
                    }`}
                  >
                    {tab.name}
                  </button>
                ))}
              </nav>
              <button
                onClick={() => setShowSettings(true)}
                className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span>Settings</span>
              </button>
            </div>
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
            <div className="text-center mb-16 mt-8">
              <h2 className="text-5xl font-semibold text-gray-900 mb-4 tracking-tight">
                Generate Ideas
              </h2>
              <p className="text-xl text-gray-500 max-w-2xl mx-auto font-light">
                AI-powered analysis to validate and refine your startup concepts
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
                <h3 className="text-3xl font-semibold text-gray-900 mb-8 tracking-tight">
                  Your Ideas
                </h3>
                <div className="grid gap-8 md:grid-cols-1 lg:grid-cols-2">
                  {generatedIdeas.map((idea, index) => (
                    <motion.div 
                      key={idea.id} 
                      className="bg-gray-50 rounded-2xl p-8 hover:bg-gray-100 transition-all duration-300 border border-gray-200"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      {/* Header with Score Badge */}
                      <div className="flex justify-between items-start mb-4">
                        <h4 className="text-xl font-bold text-gray-900 pr-4 leading-tight">
                          {idea.title}
                        </h4>
                        <div className="flex-shrink-0">
                          <div className={`px-3 py-1 rounded-full text-sm font-bold ${
                            idea.overall_score >= 0.8 ? 'bg-green-100 text-green-800' :
                            idea.overall_score >= 0.6 ? 'bg-blue-100 text-blue-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {(idea.overall_score * 100).toFixed(0)}%
                          </div>
                        </div>
                      </div>

                      {/* Description */}
                      <p className="text-gray-700 mb-4 leading-relaxed">{idea.description}</p>

                      {/* Scores Grid */}
                      <div className="grid grid-cols-3 gap-3 mb-4">
                        <div className="bg-blue-50 p-3 rounded-lg text-center">
                          <div className="text-xs text-gray-600 mb-1">Feasibility</div>
                          <div className="text-lg font-bold text-blue-600">
                            {(idea.feasibility_score * 100).toFixed(0)}%
                          </div>
                        </div>
                        <div className="bg-purple-50 p-3 rounded-lg text-center">
                          <div className="text-xs text-gray-600 mb-1">Novelty</div>
                          <div className="text-lg font-bold text-purple-600">
                            {(idea.novelty_score * 100).toFixed(0)}%
                          </div>
                        </div>
                        <div className="bg-green-50 p-3 rounded-lg text-center">
                          <div className="text-xs text-gray-600 mb-1">Market Signal</div>
                          <div className="text-lg font-bold text-green-600">
                            {(idea.market_signal_score * 100).toFixed(0)}%
                          </div>
                        </div>
                      </div>

                      {/* Agent Outputs Summary */}
                      {(idea.critic_output || idea.pm_refiner_output || idea.synthesizer_output) && (
                        <div className="mb-4 flex flex-wrap gap-2">
                          {idea.critic_output && (
                            <span className="badge badge-yellow text-xs">✓ Critic Review</span>
                          )}
                          {idea.pm_refiner_output && (
                            <span className="badge badge-blue text-xs">✓ PM Refinement</span>
                          )}
                          {idea.synthesizer_output && (
                            <span className="badge badge-green text-xs">✓ Final Synthesis</span>
                          )}
                        </div>
                      )}

                      {/* Key Insights Preview */}
                      {idea.synthesizer_output?.value_proposition && (
                        <div className="bg-gradient-to-r from-primary-50 to-purple-50 p-3 rounded-lg mb-4">
                          <div className="text-xs font-semibold text-gray-600 mb-1">Value Proposition</div>
                          <p className="text-sm text-gray-800 line-clamp-2">{idea.synthesizer_output.value_proposition}</p>
                        </div>
                      )}

                      {/* Action Button */}
                      <button 
                        className="w-full text-center text-sm font-medium text-gray-900 hover:text-gray-600 transition-colors py-2"
                        onClick={() => setSelectedIdea(idea)}
                      >
                        View Full Analysis →
                      </button>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </motion.div>
        )}

        {activeTab === 'upload' && (
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <UploadArea />
          </motion.div>
        )}

        {activeTab === 'timeline' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="text-center mb-16 mt-8">
              <h2 className="text-5xl font-semibold text-gray-900 mb-4 tracking-tight">
                Timeline
              </h2>
              <p className="text-xl text-gray-500 max-w-2xl mx-auto font-light">
                Track how your ideas evolve through our refinement process
              </p>
            </div>
            
            <IdeaTimeline 
              ideas={generatedIdeas} 
              onViewDetails={setSelectedIdea}
            />
          </motion.div>
        )}

        {activeTab === 'artifacts' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="text-center mb-16 mt-8">
              <h2 className="text-5xl font-semibold text-gray-900 mb-4 tracking-tight">
                Artifacts
              </h2>
              <p className="text-xl text-gray-500 max-w-2xl mx-auto font-light">
                Mockups, presentations, and visual materials for your ideas
              </p>
            </div>
            
            <ArtifactViewer />
          </motion.div>
        )}
      </main>

      {/* Idea Details Modal */}
      {selectedIdea && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedIdea(null)}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-start">
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-1">
                  {selectedIdea.title}
                </h3>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    selectedIdea.overall_score >= 0.8 ? 'bg-green-100 text-green-800' :
                    selectedIdea.overall_score >= 0.6 ? 'bg-blue-100 text-blue-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    Overall: {(selectedIdea.overall_score * 100).toFixed(0)}%
                  </span>
                  <span className="text-xs text-gray-500">•</span>
                  <span className="text-xs text-gray-500">{selectedIdea.status}</span>
                </div>
              </div>
              <button
                onClick={() => setSelectedIdea(null)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Description */}
              <div>
                <h4 className="text-sm font-semibold text-gray-500 uppercase mb-2 tracking-wide">Description</h4>
                <p className="text-gray-700 leading-relaxed">{selectedIdea.description}</p>
              </div>

              {/* Scores */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
                  <p className="text-sm text-blue-800 mb-1 font-medium">Feasibility</p>
                  <p className="text-3xl font-bold text-blue-600">{(selectedIdea.feasibility_score * 100).toFixed(0)}%</p>
                </div>
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200">
                  <p className="text-sm text-purple-800 mb-1 font-medium">Novelty</p>
                  <p className="text-3xl font-bold text-purple-600">{(selectedIdea.novelty_score * 100).toFixed(0)}%</p>
                </div>
                <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
                  <p className="text-sm text-green-800 mb-1 font-medium">Market Signal</p>
                  <p className="text-3xl font-bold text-green-600">{(selectedIdea.market_signal_score * 100).toFixed(0)}%</p>
                </div>
              </div>

              {/* Market Analysis */}
              {selectedIdea.market_analysis && typeof selectedIdea.market_analysis === 'object' && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-500 uppercase mb-3 tracking-wide">Market Analysis</h4>
                  <div className="bg-blue-50 p-4 rounded-lg space-y-3">
                    {selectedIdea.market_analysis.market_opportunity && (
                      <div>
                        <p className="text-sm font-semibold text-blue-900 mb-1">Market Opportunity</p>
                        <p className="text-sm text-blue-800">{selectedIdea.market_analysis.market_opportunity}</p>
                      </div>
                    )}
                    {selectedIdea.market_analysis.key_trends && (
                      <div>
                        <p className="text-sm font-semibold text-blue-900 mb-2">Key Trends</p>
                        <ul className="text-sm text-blue-800 space-y-1">
                          {selectedIdea.market_analysis.key_trends.slice(0, 5).map((trend, i) => (
                            <li key={i} className="flex items-start">
                              <span className="mr-2">•</span>
                              <span>{trend}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {selectedIdea.market_analysis.current_players && selectedIdea.market_analysis.current_players.length > 0 && (
                      <div>
                        <p className="text-sm font-semibold text-blue-900 mb-2">Current Players</p>
                        <div className="flex flex-wrap gap-2">
                          {selectedIdea.market_analysis.current_players.map((player, i) => (
                            <span key={i} className="bg-blue-200 text-blue-900 px-2 py-1 rounded text-xs font-medium">
                              {player}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {selectedIdea.market_analysis.competitive_landscape && (
                      <div>
                        <p className="text-sm font-semibold text-blue-900 mb-1">Competitive Landscape</p>
                        <p className="text-sm text-blue-800">{selectedIdea.market_analysis.competitive_landscape}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Critic Feedback */}
              {selectedIdea.critic_output && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-500 uppercase mb-3 tracking-wide">Critic Analysis</h4>
                  <div className="bg-yellow-50 p-4 rounded-lg space-y-3">
                    {selectedIdea.critic_output.strengths && (
                      <div>
                        <p className="text-sm font-semibold text-yellow-900 mb-2">Strengths</p>
                        <ul className="text-sm text-yellow-800 space-y-1">
                          {selectedIdea.critic_output.strengths.map((strength, i) => (
                            <li key={i} className="flex items-start">
                              <span className="mr-2 text-green-600">✓</span>
                              <span>{strength}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {selectedIdea.critic_output.weaknesses && (
                      <div>
                        <p className="text-sm font-semibold text-yellow-900 mb-2">Weaknesses</p>
                        <ul className="text-sm text-yellow-800 space-y-1">
                          {selectedIdea.critic_output.weaknesses.map((weakness, i) => (
                            <li key={i} className="flex items-start">
                              <span className="mr-2 text-red-600">⚠</span>
                              <span>{weakness}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {selectedIdea.critic_output.suggestions && (
                      <div>
                        <p className="text-sm font-semibold text-yellow-900 mb-2">Suggestions</p>
                        <ul className="text-sm text-yellow-800 space-y-1">
                          {selectedIdea.critic_output.suggestions.map((suggestion, i) => (
                            <li key={i} className="flex items-start">
                              <span className="mr-2">💡</span>
                              <span>{suggestion}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* PM Refinements */}
              {selectedIdea.pm_refiner_output && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-500 uppercase mb-3 tracking-wide">PM Refinements</h4>
                  <div className="bg-purple-50 p-4 rounded-lg space-y-3">
                    {selectedIdea.pm_refiner_output.timeline && (
                      <div className="flex items-center space-x-2 text-sm">
                        <span className="font-semibold text-purple-900">Timeline:</span>
                        <span className="bg-purple-200 text-purple-900 px-2 py-1 rounded">{selectedIdea.pm_refiner_output.timeline}</span>
                      </div>
                    )}
                    {selectedIdea.pm_refiner_output.features && (
                      <div>
                        <p className="text-sm font-semibold text-purple-900 mb-2">MVP Features</p>
                        <ul className="text-sm text-purple-800 space-y-1">
                          {selectedIdea.pm_refiner_output.features.slice(0, 6).map((feature, i) => (
                            <li key={i} className="flex items-start">
                              <span className="mr-2">✓</span>
                              <span>{feature}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {selectedIdea.pm_refiner_output.priorities && (
                      <div>
                        <p className="text-sm font-semibold text-purple-900 mb-2">Development Priorities</p>
                        <ol className="text-sm text-purple-800 space-y-1">
                          {selectedIdea.pm_refiner_output.priorities.slice(0, 5).map((priority, i) => (
                            <li key={i} className="flex items-start">
                              <span className="mr-2 font-semibold">{i+1}.</span>
                              <span>{priority}</span>
                            </li>
                          ))}
                        </ol>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Final Synthesis */}
              {selectedIdea.synthesizer_output && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-500 uppercase mb-3 tracking-wide">Final Synthesis</h4>
                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-4 rounded-lg space-y-3 border border-green-200">
                    {selectedIdea.synthesizer_output.final_concept && (
                      <div>
                        <p className="text-sm font-semibold text-green-900 mb-2">Final Concept</p>
                        <p className="text-sm text-green-800">{selectedIdea.synthesizer_output.final_concept}</p>
                      </div>
                    )}
                    {selectedIdea.synthesizer_output.value_proposition && (
                      <div>
                        <p className="text-sm font-semibold text-green-900 mb-1">Value Proposition</p>
                        <p className="text-sm text-green-800 italic">"{selectedIdea.synthesizer_output.value_proposition}"</p>
                      </div>
                    )}
                    {selectedIdea.synthesizer_output.business_model && (
                      <div>
                        <p className="text-sm font-semibold text-green-900 mb-1">Business Model</p>
                        <p className="text-sm text-green-800">{selectedIdea.synthesizer_output.business_model}</p>
                      </div>
                    )}
                    {selectedIdea.synthesizer_output.go_to_market && (
                      <div>
                        <p className="text-sm font-semibold text-green-900 mb-1">Go-to-Market Strategy</p>
                        <p className="text-sm text-green-800">{selectedIdea.synthesizer_output.go_to_market}</p>
                      </div>
                    )}
                    {selectedIdea.synthesizer_output.revenue_projections && (
                      <div>
                        <p className="text-sm font-semibold text-green-900 mb-2">Revenue Projections</p>
                        <div className="grid grid-cols-3 gap-2">
                          {Object.entries(selectedIdea.synthesizer_output.revenue_projections).map(([year, data]) => (
                            <div key={year} className="bg-white p-2 rounded text-center">
                              <p className="text-xs text-gray-600">{year.replace('year', 'Year ')}</p>
                              <p className="text-lg font-bold text-green-700">${typeof data === 'object' ? data.revenue : data}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex justify-between items-center pt-6 border-t border-gray-200">
                <button
                  onClick={() => setSelectedIdea(null)}
                  className="text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors"
                >
                  Close
                </button>
                <button 
                  onClick={() => setShowIterateDialog(true)}
                  className="bg-gray-900 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-gray-800 transition-all text-sm"
                >
                  Iterate on Idea
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Iterate Dialog */}
      {showIterateDialog && selectedIdea && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setShowIterateDialog(false)}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-lg shadow-xl max-w-2xl w-full"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6">
              {/* Header */}
              <div className="mb-6">
                <div className="flex justify-between items-start">
                  <h3 className="text-2xl font-semibold text-gray-900 mb-1">
                    Iterate on Idea
                  </h3>
                  <button
                    onClick={() => setShowIterateDialog(false)}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <p className="text-sm text-gray-500 mt-1">{selectedIdea.title}</p>
              </div>

              {/* Form */}
              <div className="space-y-6">
                {/* Iteration Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    What would you like to improve?
                  </label>
                  <select
                    value={iterationType}
                    onChange={(e) => setIterationType(e.target.value)}
                    className="w-full rounded-lg border-gray-300 focus:border-gray-400 focus:ring-0"
                  >
                    <option value="synthesis">Overall Synthesis</option>
                    <option value="refinement">Product Refinement</option>
                    <option value="critique">Critical Analysis</option>
                    <option value="market_analysis">Market Analysis</option>
                  </select>
                </div>

                {/* Feedback */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Your feedback or direction
                  </label>
                  <textarea
                    value={iterateFeedback}
                    onChange={(e) => setIterateFeedback(e.target.value)}
                    placeholder="E.g., Focus more on enterprise customers, reduce the scope to core features, add more technical details..."
                    rows={4}
                    className="w-full rounded-lg border-gray-300 focus:border-gray-400 focus:ring-0"
                  />
                </div>

                {/* Action Buttons */}
                <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                  <button
                    onClick={() => setShowIterateDialog(false)}
                    disabled={isIterating}
                    className="text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button 
                    onClick={handleIterateIdea}
                    disabled={isIterating || !iterateFeedback.trim()}
                    className="bg-gray-900 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-gray-800 transition-all text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isIterating ? (
                      <div className="flex items-center space-x-2">
                        <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        <span>Iterating...</span>
                      </div>
                    ) : (
                      'Apply Changes'
                    )}
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Settings Modal */}
      {showSettings && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setShowSettings(false)}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6">
              <div className="mb-6">
                <h3 className="text-2xl font-semibold text-gray-900 mb-1">
                  Agent Model Settings
                </h3>
                <p className="text-sm text-gray-500">Configure which AI model each agent uses</p>
              </div>

              <div className="space-y-5">
                {/* Market Analyst */}
                <div className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
                  <label className="block text-sm font-medium text-gray-900 mb-3">
                    🌍 Market Analyst
                    <span className="block text-xs font-normal text-gray-500 mt-1"> : Analyzes market trends and opportunities</span>
                  </label>
                  <select
                    value={modelSettings.market_analyst}
                    onChange={(e) => saveModelSettings({...modelSettings, market_analyst: e.target.value})}
                    className="w-full rounded-lg border-gray-300 focus:border-gray-400 focus:ring-0"
                  >
                    <option value="gemini-2.0-flash-lite">Gemini 2.0 Flash Lite (Fast)</option>
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro (Balanced)</option>
                    <option value="gemini-1.5-flash">Gemini 1.5 Flash (Fast)</option>
                    <option value="gpt-4">GPT-4 (Premium)</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Fast)</option>
                  </select>
                </div>

                {/* Idea Generator */}
                <div className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
                  <label className="block text-sm font-medium text-gray-900 mb-3">
                    💡 Idea Generator
                    <span className="block text-xs font-normal text-gray-500 mt-1"> : Generates innovative startup concepts</span>
                  </label>
                  <select
                    value={modelSettings.idea_generator}
                    onChange={(e) => saveModelSettings({...modelSettings, idea_generator: e.target.value})}
                    className="w-full rounded-lg border-gray-300 focus:border-gray-400 focus:ring-0"
                  >
                    <option value="gemini-2.0-flash-lite">Gemini 2.0 Flash Lite (Fast)</option>
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro (Balanced)</option>
                    <option value="gemini-1.5-flash">Gemini 1.5 Flash (Fast)</option>
                    <option value="gpt-4">GPT-4 (Premium)</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Fast)</option>
                  </select>
                </div>

                {/* Critic */}
                <div className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
                  <label className="block text-sm font-medium text-gray-900 mb-3">
                    🔍 Critic
                    <span className="block text-xs font-normal text-gray-500 mt-1"> : Provides critical analysis and feedback</span>
                  </label>
                  <select
                    value={modelSettings.critic}
                    onChange={(e) => saveModelSettings({...modelSettings, critic: e.target.value})}
                    className="w-full rounded-lg border-gray-300 focus:border-gray-400 focus:ring-0"
                  >
                    <option value="gemini-2.0-flash-lite">Gemini 2.0 Flash Lite (Fast)</option>
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro (Balanced)</option>
                    <option value="gemini-1.5-flash">Gemini 1.5 Flash (Fast)</option>
                    <option value="gpt-4">GPT-4 (Premium)</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Fast)</option>
                  </select>
                </div>

                {/* PM Refiner */}
                <div className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
                  <label className="block text-sm font-medium text-gray-900 mb-3">
                    📋 PM Refiner
                    <span className="block text-xs font-normal text-gray-500 mt-1">: Refines product management aspects</span>
                  </label>
                  <select
                    value={modelSettings.pm_refiner}
                    onChange={(e) => saveModelSettings({...modelSettings, pm_refiner: e.target.value})}
                    className="w-full rounded-lg border-gray-300 focus:border-gray-400 focus:ring-0"
                  >
                    <option value="gemini-2.0-flash-lite">Gemini 2.0 Flash Lite (Fast)</option>
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro (Balanced)</option>
                    <option value="gemini-1.5-flash">Gemini 1.5 Flash (Fast)</option>
                    <option value="gpt-4">GPT-4 (Premium)</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Fast)</option>
                  </select>
                </div>

                {/* Synthesizer */}
                <div className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
                  <label className="block text-sm font-medium text-gray-900 mb-3">
                    ⚡ Synthesizer
                    <span className="block text-xs font-normal text-gray-500 mt-1"> : Synthesizes final strategy and recommendations</span>
                  </label>
                  <select
                    value={modelSettings.synthesizer}
                    onChange={(e) => saveModelSettings({...modelSettings, synthesizer: e.target.value})}
                    className="w-full rounded-lg border-gray-300 focus:border-gray-400 focus:ring-0"
                  >
                    <option value="gemini-2.0-flash-lite">Gemini 2.0 Flash Lite (Fast)</option>
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro (Balanced)</option>
                    <option value="gemini-1.5-flash">Gemini 1.5 Flash (Fast)</option>
                    <option value="gpt-4">GPT-4 (Premium)</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Fast)</option>
                  </select>
                </div>
              </div>

              {/* Info Box */}
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-600">
                  <strong>Note:</strong> Model selections are saved in your browser. Different models offer different trade-offs between speed, cost, and quality. Gemini models are currently active; OpenAI models require API configuration.
                </p>
              </div>

              {/* Close Button */}
              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowSettings(false)}
                  className="bg-gray-900 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-gray-800 transition-all text-sm"
                >
                  Done
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}
