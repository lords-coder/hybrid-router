'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Navbar from '@/components/Navbar'
import AnimatedBackground from '@/components/AnimatedBackground'
import GlassCard from '@/components/GlassCard'
import { Brain, Zap, Bot, Clock, Coins, TrendingUp, AlertCircle, Loader2, Target, Cpu, Shield, ArrowRight } from 'lucide-react'

export default function RouterDashboard() {
  const [prompt, setPrompt] = useState('')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleRoute = async () => {
    if (!prompt.trim()) return
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch('http://localhost:8000/api/route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      })

      if (!response.ok) throw new Error(`Server error: ${response.status}`)
      const data = await response.json()

      if (data.success) {
        setResult({
          analysis: data.analysis,
          response: data.response,
          request_id: data.request_id,
          timestamp: data.timestamp,
        })
      } else {
        setError(data.detail || data.response?.error || 'Failed to route prompt')
      }
    } catch (e: any) {
      setError(`Could not connect to backend: ${e.message}`)
    }
    setLoading(false)
  }

  const analysis = result?.analysis
  const response = result?.response
  const isLocal = analysis?.is_local

  return (
    <main className="min-h-screen relative">
      <AnimatedBackground />
      <Navbar />

      <div className="max-w-5xl mx-auto pt-32 px-6 pb-20">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10"
        >
          <h1 className="text-4xl font-bold text-white mb-2">Token-Efficient <span className="text-gradient">Router</span></h1>
          <p className="text-gray-400">Type a prompt and watch the agent pick the cheapest capable model</p>
        </motion.div>

        <GlassCard className="mb-8">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleRoute()
              }
            }}
            className="w-full h-40 bg-transparent border-none focus:outline-none text-lg text-white resize-none placeholder-gray-500"
            placeholder="Try: 'What is the capital of France?' or 'Write a Python function to sort a list'"
          />
          <div className="flex items-center justify-between mt-4">
            <p className="text-xs text-gray-500">Press Enter to send</p>
            <button
              onClick={handleRoute}
              disabled={loading || !prompt.trim()}
              className="premium-button px-8 py-3 flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Routing...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  Route & Answer
                </>
              )}
            </button>
          </div>
        </GlassCard>

        {error && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <GlassCard className="border-red-500/20">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            </GlassCard>
          </motion.div>
        )}

        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              {analysis && (
                <>
                  <GlassCard className={isLocal ? 'border-green-500/30' : ''}>
                    <div className="flex items-center gap-3 mb-4">
                      {isLocal ? (
                        <div className="p-2 rounded-xl bg-green-500/10">
                          <Shield className="w-5 h-5 text-green-400" />
                        </div>
                      ) : (
                        <div className="p-2 rounded-xl bg-indigo-500/10">
                          <Brain className="w-5 h-5 text-indigo-400" />
                        </div>
                      )}
                      <div>
                        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
                          Routing Decision
                        </h3>
                        {isLocal && (
                          <p className="text-xs text-green-400 font-medium">ZERO Fireworks tokens used!</p>
                        )}
                      </div>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div className="p-3 rounded-xl bg-white/5">
                        <p className="text-xs text-gray-500 mb-1">Task Type</p>
                        <p className="text-sm font-medium text-white capitalize">{analysis.task_type.replace(/_/g, ' ')}</p>
                      </div>
                      <div className="p-3 rounded-xl bg-white/5">
                        <p className="text-xs text-gray-500 mb-1">Complexity</p>
                        <p className="text-sm font-medium text-white capitalize">{analysis.complexity.replace(/_/g, ' ')}</p>
                      </div>
                      <div className="p-3 rounded-xl bg-white/5">
                        <p className="text-xs text-gray-500 mb-1">Confidence</p>
                        <p className="text-sm font-medium text-green-400">{(analysis.confidence * 100).toFixed(0)}%</p>
                      </div>
                      <div className="p-3 rounded-xl bg-white/5">
                        <p className="text-xs text-gray-500 mb-1">Provider</p>
                        <p className={`text-sm font-medium capitalize ${isLocal ? 'text-green-400' : 'text-indigo-400'}`}>
                          {isLocal ? 'Local Model' : 'Fireworks AI'}
                        </p>
                      </div>
                    </div>
                    <div className="p-3 rounded-xl bg-indigo-500/5 border border-indigo-500/10">
                      <p className="text-xs text-gray-500 mb-1">Why this model?</p>
                      <p className="text-sm text-gray-300">{analysis.selection_reason}</p>
                    </div>
                  </GlassCard>

                  <div className="grid md:grid-cols-3 gap-6">
                    <GlassCard>
                      <div className="flex items-center gap-3 mb-3">
                        <div className={`p-2 rounded-xl ${isLocal ? 'bg-green-500/10' : 'bg-indigo-500/10'}`}>
                          <Cpu className={`w-5 h-5 ${isLocal ? 'text-green-400' : 'text-indigo-400'}`} />
                        </div>
                        <h4 className="text-sm font-semibold text-white">Selected Model</h4>
                      </div>
                      <p className="text-lg font-bold text-white mb-1">{analysis.selected_model.display_name}</p>
                      <p className="text-xs text-gray-500 font-mono capitalize">{analysis.selected_model.provider} provider</p>
                      {!isLocal && (
                        <div className="mt-3 pt-3 border-t border-white/5">
                          <p className="text-xs text-gray-500">Cost per 1K tokens</p>
                          <p className="text-sm font-medium text-white">${analysis.selected_model.cost_per_1k_input}</p>
                        </div>
                      )}
                    </GlassCard>

                    <GlassCard>
                      <div className="flex items-center gap-3 mb-3">
                        <div className={`p-2 rounded-xl ${isLocal ? 'bg-green-500/10' : 'bg-yellow-500/10'}`}>
                          <Coins className={`w-5 h-5 ${isLocal ? 'text-green-400' : 'text-yellow-400'}`} />
                        </div>
                        <h4 className="text-sm font-semibold text-white">Token Cost</h4>
                      </div>
                      <p className={`text-lg font-bold mb-1 ${isLocal ? 'text-green-400' : 'text-yellow-400'}`}>
                        {isLocal ? 'FREE (LOCAL)' : 'Fireworks Tokens'}
                      </p>
                      <p className="text-xs text-gray-500">
                        {isLocal ? 'Zero Fireworks tokens - best possible score' : 'Routed through FIREWORKS_BASE_URL'}
                      </p>
                      <div className="mt-3 pt-3 border-t border-white/5">
                        <p className="text-xs text-gray-500">vs paid APIs</p>
                        <p className="text-sm font-medium text-green-400">100% saved</p>
                      </div>
                    </GlassCard>

                    <GlassCard>
                      <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 rounded-xl bg-purple-500/10">
                          <Target className="w-5 h-5 text-purple-400" />
                        </div>
                        <h4 className="text-sm font-semibold text-white">Token Usage</h4>
                      </div>
                      <p className="text-lg font-bold text-white mb-1">
                        {response?.total_tokens || analysis.estimated_tokens.total} tokens
                      </p>
                      <p className="text-xs text-gray-500">Estimated total tokens</p>
                      <div className="mt-3 pt-3 border-t border-white/5">
                        <p className="text-xs text-gray-500">Tokens saved by compression</p>
                        <p className="text-sm font-medium text-purple-400">{analysis.optimization.tokens_saved} tokens</p>
                      </div>
                    </GlassCard>
                  </div>
                </>
              )}

              {response && (
                <GlassCard className="glass-glow">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 rounded-xl bg-white/10">
                      <Bot className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white">AI Response</h3>
                      <p className="text-xs text-gray-400">From {analysis?.selected_model.display_name}</p>
                    </div>
                  </div>

                  {response.success ? (
                    <div className="prose prose-invert max-w-none">
                      <div className="text-gray-200 text-base leading-relaxed whitespace-pre-wrap bg-white/5 rounded-xl p-6 border border-white/5">
                        {response.content}
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20">
                      <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                      <div>
                        <p className="text-red-400 font-medium text-sm">Request Failed</p>
                        <p className="text-red-400/70 text-xs mt-1">{response.error}</p>
                      </div>
                    </div>
                  )}

                  {response.success && (
                    <div className="mt-6 pt-4 border-t border-white/5 flex items-center gap-6 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {response.processing_time_ms}ms
                      </span>
                      <span>{response.input_tokens} input tokens</span>
                      <span>{response.output_tokens} output tokens</span>
                      <span className={isLocal ? 'text-green-400' : 'text-yellow-400'}>
                        {isLocal ? 'LOCAL (0 FW tokens)' : `${response.fireworks_tokens} FW tokens`}
                      </span>
                    </div>
                  )}
                </GlassCard>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </main>
  )
}
