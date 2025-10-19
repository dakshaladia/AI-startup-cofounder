'use client'

import { motion } from 'framer-motion'
import { 
  ChartBarIcon, 
  ClockIcon, 
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline'

interface Idea {
  id: string
  title: string
  description: string
  market_analysis: string
  feasibility_score: number
  novelty_score: number
  overall_score: number
  created_at: string
}

interface IdeaTimelineProps {
  ideas: Idea[]
}

export default function IdeaTimeline({ ideas }: IdeaTimelineProps) {
  const pipelineSteps = [
    {
      id: 'market_analysis',
      name: 'Market Analysis',
      description: 'Analyzing market conditions and opportunities',
      icon: ChartBarIcon,
      color: 'blue'
    },
    {
      id: 'idea_generation',
      name: 'Idea Generation',
      description: 'Creating innovative startup concepts',
      icon: ChartBarIcon,
      color: 'green'
    },
    {
      id: 'critique',
      name: 'Critique',
      description: 'Evaluating and identifying weaknesses',
      icon: ExclamationTriangleIcon,
      color: 'yellow'
    },
    {
      id: 'refinement',
      name: 'Refinement',
      description: 'Improving ideas based on feedback',
      icon: ArrowRightIcon,
      color: 'purple'
    },
    {
      id: 'synthesis',
      name: 'Synthesis',
      description: 'Creating final polished concepts',
      icon: CheckCircleIcon,
      color: 'green'
    }
  ]

  const getStepColor = (color: string) => {
    const colors = {
      blue: 'bg-blue-100 text-blue-800 border-blue-200',
      green: 'bg-green-100 text-green-800 border-green-200',
      yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      purple: 'bg-purple-100 text-purple-800 border-purple-200'
    }
    return colors[color as keyof typeof colors] || colors.blue
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600'
    if (score >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (ideas.length === 0) {
    return (
      <div className="text-center py-12">
        <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Ideas Yet</h3>
        <p className="text-gray-500">
          Generate some ideas to see their evolution through the pipeline
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {ideas.map((idea, ideaIndex) => (
        <motion.div
          key={idea.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: ideaIndex * 0.1 }}
          className="card"
        >
          {/* Idea Header */}
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {idea.title}
              </h3>
              <p className="text-gray-600 mb-4">{idea.description}</p>
              <div className="flex space-x-4 text-sm">
                <span className={`font-medium ${getScoreColor(idea.overall_score)}`}>
                  Overall: {idea.overall_score}
                </span>
                <span className={`font-medium ${getScoreColor(idea.feasibility_score)}`}>
                  Feasibility: {idea.feasibility_score}
                </span>
                <span className={`font-medium ${getScoreColor(idea.novelty_score)}`}>
                  Novelty: {idea.novelty_score}
                </span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500 mb-1">Created</div>
              <div className="text-sm font-medium text-gray-900">
                {new Date(idea.created_at).toLocaleDateString()}
              </div>
            </div>
          </div>

          {/* Pipeline Steps */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">
              Pipeline Progress
            </h4>
            
            <div className="relative">
              {/* Timeline Line */}
              <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" />
              
              {pipelineSteps.map((step, stepIndex) => (
                <div key={step.id} className="relative flex items-start space-x-4 pb-6">
                  {/* Step Icon */}
                  <div className={`relative z-10 flex items-center justify-center w-8 h-8 rounded-full border-2 ${getStepColor(step.color)}`}>
                    <step.icon className="h-4 w-4" />
                  </div>
                  
                  {/* Step Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h5 className="text-sm font-medium text-gray-900">
                        {step.name}
                      </h5>
                      <div className="flex items-center space-x-2">
                        <ClockIcon className="h-4 w-4 text-gray-400" />
                        <span className="text-xs text-gray-500">
                          {Math.random() * 2 + 0.5}s
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {step.description}
                    </p>
                    
                    {/* Step Results */}
                    {step.id === 'market_analysis' && (
                      <div className="mt-3 p-3 bg-blue-50 rounded-md">
                        <p className="text-sm text-blue-800">
                          <strong>Market Analysis:</strong> {idea.market_analysis}
                        </p>
                      </div>
                    )}
                    
                    {step.id === 'critique' && (
                      <div className="mt-3 p-3 bg-yellow-50 rounded-md">
                        <p className="text-sm text-yellow-800">
                          <strong>Key Issues:</strong> High competition, complex implementation, regulatory challenges
                        </p>
                      </div>
                    )}
                    
                    {step.id === 'refinement' && (
                      <div className="mt-3 p-3 bg-purple-50 rounded-md">
                        <p className="text-sm text-purple-800">
                          <strong>Improvements:</strong> Simplified MVP, focused target market, clear value proposition
                        </p>
                      </div>
                    )}
                    
                    {step.id === 'synthesis' && (
                      <div className="mt-3 p-3 bg-green-50 rounded-md">
                        <p className="text-sm text-green-800">
                          <strong>Final Concept:</strong> Polished idea ready for presentation and implementation
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button className="btn btn-secondary">
              View Details
            </button>
            <button className="btn btn-primary">
              Export
            </button>
          </div>
        </motion.div>
      ))}
    </div>
  )
}
