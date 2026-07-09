'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Navbar from '@/components/Navbar'
import AnimatedBackground from '@/components/AnimatedBackground'
import GlassCard from '@/components/GlassCard'
import { Cpu, Zap, Brain, ChevronRight, Globe, Shield, Star } from 'lucide-react'

interface Model {
  name: string
  display_name: string
  provider: string
  capabilities: string[]
  reasoning_score: number
  context_length: number
  max_output_tokens: number
  cost_per_1k_input: number
  speed_tier: number
  allowed: boolean
  is_gemma: boolean
}

export default function ModelsPage() {
  const [models, setModels] = useState<Model[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<Model | null>(null)
  const [filter, setFilter] = useState<'all' | 'local' | 'fireworks' | 'gemma'>('all')

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/models')
        const json = await res.json()
        if (json.success) setModels(json.data)
      } catch (e) {
        console.error('Failed to fetch models')
      }
      setLoading(false)
    }
    fetchModels()
  }, [])

  const filtered = models.filter(m => {
    if (filter === 'local') return m.provider === 'local'
    if (filter === 'fireworks') return m.provider === 'fireworks'
    if (filter === 'gemma') return m.is_gemma
    return true
  })

  const getSpeedLabel = (tier: number) => {
    const labels = ['', 'Blazing Fast', 'Fast', 'Moderate', 'Standard']
    return labels[tier] || 'Unknown'
  }

  return (
    <main className="min-h-screen relative">
      <AnimatedBackground />
      <Navbar />

      <div className="max-w-6xl mx-auto pt-32 px-6 pb-20">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10"
        >
          <h1 className="text-4xl font-bold text-white mb-2">Models</h1>
          <p className="text-gray-400">Fireworks AI models + Local models for zero-token inference</p>
        </motion.div>

        <div className="flex gap-3 mb-8 flex-wrap">
          {(['all', 'local', 'fireworks', 'gemma'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                filter === f
                  ? 'bg-white text-black'
                  : 'bg-white/5 border border-white/10 text-gray-400 hover:text-white hover:bg-white/10'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
              {f === 'local' && ' (0 tokens)'}
              {f === 'gemma' && ' (Bonus)'}
            </button>
          ))}
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {filtered.map((model, i) => (
            <GlassCard
              key={i}
              delay={i * 0.05}
              className={`cursor-pointer ${selected?.name === model.name ? 'ring-2 ring-indigo-500/50' : ''} ${
                !model.allowed && model.provider === 'fireworks' ? 'opacity-50' : ''
              }`}
            >
              <div onClick={() => setSelected(selected?.name === model.name ? null : model)}>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-xl ${
                      model.provider === 'local' ? 'bg-green-500/10' :
                      model.is_gemma ? 'bg-purple-500/10' : 'bg-indigo-500/10'
                    }`}>
                      {model.provider === 'local' ? (
                        <Shield className="w-5 h-5 text-green-400" />
                      ) : model.is_gemma ? (
                        <Star className="w-5 h-5 text-purple-400" />
                      ) : (
                        <Cpu className="w-5 h-5 text-indigo-400" />
                      )}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white">{model.display_name}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`px-2 py-0.5 text-xs rounded-md font-medium ${
                          model.provider === 'local'
                            ? 'text-green-400 bg-green-500/10'
                            : model.is_gemma
                            ? 'text-purple-400 bg-purple-500/10'
                            : 'text-indigo-400 bg-indigo-500/10'
                        }`}>
                          {model.provider === 'local' ? 'LOCAL (0 tokens)' : model.is_gemma ? 'Gemma (Bonus)' : 'Fireworks AI'}
                        </span>
                        {!model.allowed && model.provider === 'fireworks' && (
                          <span className="text-xs text-red-400">Not in ALLOWED_MODELS</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <ChevronRight className={`w-5 h-5 text-gray-500 transition-transform ${selected?.name === model.name ? 'rotate-90' : ''}`} />
                </div>

                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Cost</p>
                    <p className={`text-sm font-medium ${model.provider === 'local' ? 'text-green-400' : 'text-yellow-400'}`}>
                      {model.provider === 'local' ? 'FREE' : `$${model.cost_per_1k_input}/1K`}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Reasoning</p>
                    <p className="text-sm font-medium text-white">{(model.reasoning_score * 100).toFixed(0)}%</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Speed</p>
                    <p className="text-sm font-medium text-white">{getSpeedLabel(model.speed_tier)}</p>
                  </div>
                </div>

                <div className="flex flex-wrap gap-1.5">
                  {model.capabilities.slice(0, 4).map((cap) => (
                    <span key={cap} className="px-2 py-0.5 text-xs rounded-md bg-white/5 text-gray-400 capitalize">
                      {cap.replace(/_/g, ' ')}
                    </span>
                  ))}
                  {model.capabilities.length > 4 && (
                    <span className="px-2 py-0.5 text-xs rounded-md bg-white/5 text-gray-500">
                      +{model.capabilities.length - 4} more
                    </span>
                  )}
                </div>
              </div>

              {selected?.name === model.name && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="mt-4 pt-4 border-t border-white/5"
                >
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Provider</p>
                      <p className="text-white capitalize flex items-center gap-1">
                        <Globe className="w-3 h-3" /> {model.provider}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Context Length</p>
                      <p className="text-white">{model.context_length.toLocaleString()} tokens</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Max Output</p>
                      <p className="text-white">{model.max_output_tokens.toLocaleString()} tokens</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Model ID</p>
                      <p className="text-white font-mono text-xs">{model.name}</p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <p className="text-gray-500 text-sm mb-2">All Capabilities</p>
                    <div className="flex flex-wrap gap-1.5">
                      {model.capabilities.map((cap) => (
                        <span key={cap} className="px-2 py-0.5 text-xs rounded-md bg-indigo-500/10 text-indigo-300 capitalize">
                          {cap.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </GlassCard>
          ))}
        </div>
      </div>
    </main>
  )
}
