'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  LightBulbIcon, 
  SparklesIcon,
  ArrowRightIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'

interface IdeaGeneratorProps {
  onGenerate: (topic: string, constraints: any) => Promise<void>
  isGenerating: boolean
}

export default function IdeaGenerator({ onGenerate, isGenerating }: IdeaGeneratorProps) {
  const [topic, setTopic] = useState('')
  const [constraints, setConstraints] = useState({
    market_focus: '',
    technology_stack: [],
    target_audience: '',
    budget_range: '',
    timeline: ''
  })
  const [showAdvanced, setShowAdvanced] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!topic.trim()) return
    
    await onGenerate(topic, constraints)
  }

  const addTechnology = (tech: string) => {
    if (tech.trim() && !constraints.technology_stack.includes(tech.trim())) {
      setConstraints(prev => ({
        ...prev,
        technology_stack: [...prev.technology_stack, tech.trim()]
      }))
    }
  }

  const removeTechnology = (tech: string) => {
    setConstraints(prev => ({
      ...prev,
      technology_stack: prev.technology_stack.filter(t => t !== tech)
    }))
  }

  const technologySuggestions = [
    'AI/ML', 'Blockchain', 'Web3', 'IoT', 'AR/VR', 'Cloud', 'Mobile', 'Web'
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Main Topic Input */}
        <div className="card border-none shadow-none bg-transparent p-0">
          <div className="mb-6">
            <label htmlFor="topic" className="block text-sm font-medium text-gray-500 mb-3">
              What would you like to build?
            </label>
            <input
              type="text"
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="AI-powered personal finance, sustainable transportation, healthcare innovation..."
              className="input text-lg py-3 border-gray-200 focus:border-gray-400 focus:ring-0"
              required
            />
          </div>
          
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-sm text-gray-500 hover:text-gray-900 font-medium transition-colors"
          >
            {showAdvanced ? 'Hide' : 'Show'} advanced options
          </button>
        </div>

        {/* Advanced Options */}
        {showAdvanced && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="card space-y-6"
          >
            <h3 className="text-lg font-semibold text-gray-900">Advanced Options</h3>
            
            {/* Market Focus */}
            <div>
              <label htmlFor="market_focus" className="block text-sm font-medium text-gray-700 mb-2">
                Market Focus
              </label>
              <select
                id="market_focus"
                value={constraints.market_focus}
                onChange={(e) => setConstraints(prev => ({ ...prev, market_focus: e.target.value }))}
                className="select"
              >
                <option value="">Any market</option>
                <option value="fintech">Fintech</option>
                <option value="healthcare">Healthcare</option>
                <option value="education">Education</option>
                <option value="sustainability">Sustainability</option>
                <option value="entertainment">Entertainment</option>
                <option value="productivity">Productivity</option>
              </select>
            </div>

            {/* Technology Stack */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Technology Stack
              </label>
              <div className="space-y-3">
                <div className="flex flex-wrap gap-2">
                  {constraints.technology_stack.map((tech) => (
                    <span
                      key={tech}
                      className="badge badge-primary flex items-center space-x-1"
                    >
                      <span>{tech}</span>
                      <button
                        type="button"
                        onClick={() => removeTechnology(tech)}
                        className="ml-1 hover:text-primary-900"
                      >
                        <XMarkIcon className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex flex-wrap gap-2">
                  {technologySuggestions
                    .filter(tech => !constraints.technology_stack.includes(tech))
                    .map((tech) => (
                      <button
                        key={tech}
                        type="button"
                        onClick={() => addTechnology(tech)}
                        className="badge badge-gray hover:bg-primary-100 hover:text-primary-800 cursor-pointer"
                      >
                        + {tech}
                      </button>
                    ))}
                </div>
              </div>
            </div>

            {/* Target Audience */}
            <div>
              <label htmlFor="target_audience" className="block text-sm font-medium text-gray-700 mb-2">
                Target Audience
              </label>
              <input
                type="text"
                id="target_audience"
                value={constraints.target_audience}
                onChange={(e) => setConstraints(prev => ({ ...prev, target_audience: e.target.value }))}
                placeholder="e.g., small businesses, millennials, healthcare professionals..."
                className="input"
              />
            </div>

            {/* Budget Range */}
            <div>
              <label htmlFor="budget_range" className="block text-sm font-medium text-gray-700 mb-2">
                Budget Range
              </label>
              <select
                id="budget_range"
                value={constraints.budget_range}
                onChange={(e) => setConstraints(prev => ({ ...prev, budget_range: e.target.value }))}
                className="select"
              >
                <option value="">Any budget</option>
                <option value="bootstrap">Bootstrap ($0-10K)</option>
                <option value="seed">Seed ($10K-100K)</option>
                <option value="series_a">Series A ($100K-1M)</option>
                <option value="enterprise">Enterprise ($1M+)</option>
              </select>
            </div>

            {/* Timeline */}
            <div>
              <label htmlFor="timeline" className="block text-sm font-medium text-gray-700 mb-2">
                Implementation Timeline
              </label>
              <select
                id="timeline"
                value={constraints.timeline}
                onChange={(e) => setConstraints(prev => ({ ...prev, timeline: e.target.value }))}
                className="select"
              >
                <option value="">Any timeline</option>
                <option value="3_months">3 months</option>
                <option value="6_months">6 months</option>
                <option value="1_year">1 year</option>
                <option value="2_years">2+ years</option>
              </select>
            </div>
          </motion.div>
        )}

        {/* Generate Button */}
        <div className="text-center">
          <button
            type="submit"
            disabled={!topic.trim() || isGenerating}
            className="bg-gray-900 text-white px-8 py-3.5 rounded-lg font-medium hover:bg-gray-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-base"
          >
            {isGenerating ? (
              <div className="flex items-center space-x-3">
                <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Generating...</span>
              </div>
            ) : (
              <span>Generate Ideas</span>
            )}
          </button>
        </div>
      </form>

      {/* Generation Status */}
      {isGenerating && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-8 card text-center"
        >
          <div className="space-y-4">
            <div className="flex items-center justify-center space-x-2">
              <div className="h-5 w-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
              <span className="text-gray-600">Analyzing market conditions...</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-primary-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }} />
            </div>
            <p className="text-sm text-gray-500">
              Our AI agents are working together to generate innovative ideas for you
            </p>
          </div>
        </motion.div>
      )}
    </div>
  )
}
