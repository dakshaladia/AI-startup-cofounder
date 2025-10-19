'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  DocumentIcon, 
  PhotoIcon, 
  PresentationChartBarIcon,
  ArrowDownTrayIcon,
  EyeIcon,
  ShareIcon
} from '@heroicons/react/24/outline'

interface Artifact {
  id: string
  type: 'mockup' | 'presentation' | 'document' | 'image'
  title: string
  description: string
  url: string
  created_at: string
  size: string
  format: string
}

export default function ArtifactViewer() {
  const [selectedType, setSelectedType] = useState<string>('all')
  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(null)

  // Mock artifacts data
  const artifacts: Artifact[] = [
    {
      id: '1',
      type: 'mockup',
      title: 'AI Finance App Mockup',
      description: 'High-fidelity mockup of the personal finance assistant interface',
      url: '/mockups/finance-app.png',
      created_at: '2024-01-15T10:30:00Z',
      size: '2.3 MB',
      format: 'PNG'
    },
    {
      id: '2',
      type: 'presentation',
      title: 'Investor Pitch Deck',
      description: 'Comprehensive pitch deck for Series A funding round',
      url: '/presentations/pitch-deck.pdf',
      created_at: '2024-01-15T11:45:00Z',
      size: '5.7 MB',
      format: 'PDF'
    },
    {
      id: '3',
      type: 'document',
      title: 'Business Plan',
      description: 'Detailed business plan with market analysis and financial projections',
      url: '/documents/business-plan.pdf',
      created_at: '2024-01-15T12:15:00Z',
      size: '1.8 MB',
      format: 'PDF'
    },
    {
      id: '4',
      type: 'image',
      title: 'Competitor Analysis Chart',
      description: 'Visual comparison of key competitors and market positioning',
      url: '/images/competitor-analysis.png',
      created_at: '2024-01-15T13:20:00Z',
      size: '1.2 MB',
      format: 'PNG'
    }
  ]

  const artifactTypes = [
    { id: 'all', name: 'All Artifacts', count: artifacts.length },
    { id: 'mockup', name: 'Mockups', count: artifacts.filter(a => a.type === 'mockup').length },
    { id: 'presentation', name: 'Presentations', count: artifacts.filter(a => a.type === 'presentation').length },
    { id: 'document', name: 'Documents', count: artifacts.filter(a => a.type === 'document').length },
    { id: 'image', name: 'Images', count: artifacts.filter(a => a.type === 'image').length }
  ]

  const filteredArtifacts = selectedType === 'all' 
    ? artifacts 
    : artifacts.filter(artifact => artifact.type === selectedType)

  const getArtifactIcon = (type: string) => {
    switch (type) {
      case 'mockup':
        return <PhotoIcon className="h-8 w-8 text-blue-500" />
      case 'presentation':
        return <PresentationChartBarIcon className="h-8 w-8 text-green-500" />
      case 'document':
        return <DocumentIcon className="h-8 w-8 text-red-500" />
      case 'image':
        return <PhotoIcon className="h-8 w-8 text-purple-500" />
      default:
        return <DocumentIcon className="h-8 w-8 text-gray-500" />
    }
  }

  const getArtifactTypeColor = (type: string) => {
    switch (type) {
      case 'mockup':
        return 'badge badge-primary'
      case 'presentation':
        return 'badge badge-success'
      case 'document':
        return 'badge badge-danger'
      case 'image':
        return 'badge badge-warning'
      default:
        return 'badge badge-gray'
    }
  }

  return (
    <div className="space-y-6">
      {/* Filter Tabs */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        {artifactTypes.map((type) => (
          <button
            key={type.id}
            onClick={() => setSelectedType(type.id)}
            className={`flex-1 flex items-center justify-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              selectedType === type.id
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {type.name}
            <span className="ml-2 bg-gray-200 text-gray-600 px-2 py-0.5 rounded-full text-xs">
              {type.count}
            </span>
          </button>
        ))}
      </div>

      {/* Artifacts Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredArtifacts.map((artifact) => (
          <motion.div
            key={artifact.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => setSelectedArtifact(artifact)}
          >
            <div className="flex items-start space-x-4">
              {getArtifactIcon(artifact.type)}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 truncate">
                    {artifact.title}
                  </h3>
                  <span className={getArtifactTypeColor(artifact.type)}>
                    {artifact.type}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                  {artifact.description}
                </p>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>{artifact.size}</span>
                  <span>{artifact.format}</span>
                </div>
                <div className="flex items-center space-x-2 mt-3">
                  <button className="btn btn-secondary text-xs py-1 px-2">
                    <EyeIcon className="h-3 w-3 mr-1" />
                    View
                  </button>
                  <button className="btn btn-secondary text-xs py-1 px-2">
                    <ArrowDownTrayIcon className="h-3 w-3 mr-1" />
                    Download
                  </button>
                  <button className="btn btn-secondary text-xs py-1 px-2">
                    <ShareIcon className="h-3 w-3 mr-1" />
                    Share
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Empty State */}
      {filteredArtifacts.length === 0 && (
        <div className="text-center py-12">
          <DocumentIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No {selectedType === 'all' ? '' : selectedType} artifacts found
          </h3>
          <p className="text-gray-500">
            Generate some ideas to see their artifacts and outputs
          </p>
        </div>
      )}

      {/* Artifact Detail Modal */}
      {selectedArtifact && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
          >
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center space-x-3">
                {getArtifactIcon(selectedArtifact.type)}
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">
                    {selectedArtifact.title}
                  </h2>
                  <p className="text-sm text-gray-500">
                    {selectedArtifact.format} • {selectedArtifact.size}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedArtifact(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="p-6">
              <p className="text-gray-600 mb-6">{selectedArtifact.description}</p>
              
              {/* Artifact Preview */}
              <div className="bg-gray-100 rounded-lg p-8 text-center mb-6">
                {selectedArtifact.type === 'mockup' || selectedArtifact.type === 'image' ? (
                  <div className="space-y-4">
                    <PhotoIcon className="h-16 w-16 text-gray-400 mx-auto" />
                    <p className="text-gray-500">Image preview would be displayed here</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <DocumentIcon className="h-16 w-16 text-gray-400 mx-auto" />
                    <p className="text-gray-500">Document preview would be displayed here</p>
                  </div>
                )}
              </div>
              
              {/* Action Buttons */}
              <div className="flex justify-end space-x-3">
                <button className="btn btn-secondary">
                  <ShareIcon className="h-4 w-4 mr-2" />
                  Share
                </button>
                <button className="btn btn-primary">
                  <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                  Download
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}
