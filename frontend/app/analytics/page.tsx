'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Navbar from '@/components/Navbar'
import AnimatedBackground from '@/components/AnimatedBackground'
import GlassCard from '@/components/GlassCard'
import { BarChart3, TrendingUp, Zap, Clock, Coins, Activity, RefreshCw, Shield, Globe } from 'lucide-react'

interface AnalyticsData {
  total_requests: number
  total_tokens: number
  total_fireworks_tokens: number
  total_local_tokens: number
  local_requests: number
  fireworks_requests: number
  local_percent: number
  tokens_saved_by_local: number
  avg_processing_time: number
  avg_confidence: number
  model_usage: Record<string, any>
  task_distribution: Record<string, number>
  complexity_distribution: Record<string, number>
}

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchAnalytics = async () => {
    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/analytics/summary')
      const json = await res.json()
      if (json.success) setData(json.data)
    } catch (e) {
      console.error('Failed to fetch analytics')
    }
    setLoading(false)
  }

  useEffect(() => { fetchAnalytics() }, [])

  const stats = data ? [
    { icon: BarChart3, label: 'Total Requests', value: data.total_requests, color: 'text-indigo-400' },
    { icon: Shield, label: 'Local Requests', value: data.local_requests, color: 'text-green-400' },
    { icon: Globe, label: 'Fireworks Requests', value: data.fireworks_requests, color: 'text-yellow-400' },
    { icon: Zap, label: 'Fireworks Tokens', value: data.total_fireworks_tokens.toLocaleString(), color: 'text-yellow-400' },
    { icon: TrendingUp, label: 'Tokens Saved (Local)', value: data.tokens_saved_by_local.toLocaleString(), color: 'text-green-400' },
    { icon: Coins, label: 'Local Ratio', value: `${data.local_percent}%`, color: 'text-green-400' },
    { icon: Clock, label: 'Avg Response', value: `${data.avg_processing_time.toFixed(0)}ms`, color: 'text-blue-400' },
    { icon: Activity, label: 'Confidence', value: `${(data.avg_confidence * 100).toFixed(0)}%`, color: 'text-pink-400' },
  ] : []

  return (
    <main className="min-h-screen relative">
      <AnimatedBackground />
      <Navbar />

      <div className="max-w-6xl mx-auto pt-32 px-6 pb-20">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-10"
        >
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Analytics</h1>
            <p className="text-gray-400">Track routing performance and Fireworks token usage</p>
          </div>
          <button
            onClick={fetchAnalytics}
            className="p-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all"
          >
            <RefreshCw className={`w-5 h-5 text-gray-400 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </motion.div>

        {data ? (
          <>
            <div className="grid md:grid-cols-4 gap-4 mb-10">
              {stats.map((stat, i) => (
                <GlassCard key={i} delay={i * 0.05}>
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-white/5">
                      <stat.icon className={`w-5 h-5 ${stat.color}`} />
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs">{stat.label}</p>
                      <p className="text-xl font-bold text-white">{stat.value}</p>
                    </div>
                  </div>
                </GlassCard>
              ))}
            </div>

            {data.total_requests > 0 && (
              <div className="grid md:grid-cols-2 gap-6">
                <GlassCard delay={0.3}>
                  <h3 className="text-lg font-semibold text-white mb-4">Task Distribution</h3>
                  <div className="space-y-3">
                    {Object.entries(data.task_distribution).map(([task, count]) => (
                      <div key={task} className="flex items-center justify-between">
                        <span className="text-gray-400 text-sm capitalize">{task.replace(/_/g, ' ')}</span>
                        <div className="flex items-center gap-3">
                          <div className="w-32 h-2 rounded-full bg-white/5 overflow-hidden">
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${(count / data.total_requests) * 100}%` }}
                              className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"
                            />
                          </div>
                          <span className="text-white text-sm w-8 text-right">{count}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </GlassCard>

                <GlassCard delay={0.4}>
                  <h3 className="text-lg font-semibold text-white mb-4">Model Usage</h3>
                  <div className="space-y-3">
                    {Object.entries(data.model_usage).map(([model, stats]: [string, any]) => (
                      <div key={model} className="flex items-center justify-between">
                        <span className="text-gray-400 text-sm">{model}</span>
                        <div className="flex items-center gap-3">
                          <span className="text-white text-sm">{stats.count} req</span>
                          <span className="text-gray-500 text-sm">{stats.fireworks_tokens} fw tokens</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </GlassCard>
              </div>
            )}
          </>
        ) : (
          <GlassCard>
            <div className="text-center py-20">
              <BarChart3 className="w-12 h-12 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 text-lg mb-2">No analytics yet</p>
              <p className="text-gray-500 text-sm">Start routing prompts to see your performance data</p>
            </div>
          </GlassCard>
        )}
      </div>
    </main>
  )
}
