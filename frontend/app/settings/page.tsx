'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Navbar from '@/components/Navbar'
import AnimatedBackground from '@/components/AnimatedBackground'
import GlassCard from '@/components/GlassCard'
import { Globe, Key, Shield, Cpu, Save, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react'

export default function SettingsPage() {
  const [fireworksUrl, setFireworksUrl] = useState('https://api.fireworks.ai/inference/v1')
  const [fireworksKey, setFireworksKey] = useState('')
  const [localEnabled, setLocalEnabled] = useState(false)
  const [localModel, setLocalModel] = useState('Qwen/Qwen2.5-0.5B-Instruct')
  const [allowedModels, setAllowedModels] = useState('')
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => { fetchConfig() }, [])

  const fetchConfig = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/config')
      const json = await res.json()
      if (json.success) {
        const d = json.data
        setFireworksUrl(d.fireworks_base_url || 'https://api.fireworks.ai/inference/v1')
        setLocalEnabled(d.local_model_enabled || false)
        setLocalModel(d.local_model_name || 'Qwen/Qwen2.5-0.5B-Instruct')
        setAllowedModels((d.allowed_models || []).join(', '))
      }
    } catch (e) {
      setError('Could not connect to backend')
    }
  }

  const handleSave = async () => {
    setLoading(true)
    setError('')
    setSaved(false)

    try {
      const body: any = {
        fireworks_base_url: fireworksUrl,
        local_model_enabled: localEnabled,
        local_model_name: localModel,
        allowed_models: allowedModels,
      }
      if (fireworksKey.trim()) {
        body.fireworks_api_key = fireworksKey
      }

      const res = await fetch('http://localhost:8000/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      const json = await res.json()
      if (json.success) {
        setSaved(true)
        setFireworksKey('')
        setTimeout(() => setSaved(false), 5000)
      } else {
        setError(json.detail || 'Failed to save settings')
      }
    } catch (e: any) {
      setError(`Could not connect to backend: ${e.message}`)
    }
    setLoading(false)
  }

  return (
    <main className="min-h-screen relative">
      <AnimatedBackground />
      <Navbar />

      <div className="max-w-3xl mx-auto pt-32 px-6 pb-40">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10"
        >
          <h1 className="text-4xl font-bold text-white mb-2">Settings</h1>
          <p className="text-gray-400">Configure Fireworks AI and routing preferences</p>
        </motion.div>

        {error && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-red-500/10 border border-red-500/20 mb-6">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {saved && (
          <div className="flex items-center gap-2 p-4 rounded-xl bg-green-500/20 border border-green-500/30 mb-6">
            <CheckCircle className="w-5 h-5 text-green-400" />
            <p className="text-green-400 text-sm font-medium">Settings saved successfully! Changes are live now.</p>
          </div>
        )}

        <GlassCard className="mb-6">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Globe className="w-4 h-4" />
            Fireworks AI Configuration
          </h3>
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-xs font-medium text-gray-400 ml-1 uppercase tracking-wider">Base URL</label>
              <input
                type="text"
                value={fireworksUrl}
                onChange={(e) => setFireworksUrl(e.target.value)}
                className="w-full px-4 py-3 glass-input focus:ring-2 ring-indigo-500/20 transition-all"
              />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-medium text-gray-400 ml-1 uppercase tracking-wider">API Key</label>
              <input
                type="text"
                value={fireworksKey}
                onChange={(e) => setFireworksKey(e.target.value)}
                className="w-full px-4 py-3 glass-input focus:ring-2 ring-indigo-500/20 transition-all"
                placeholder="Paste your Fireworks API key here"
              />
              <p className="text-xs text-gray-500">Get your key from fireworks.ai → Account → API Keys</p>
            </div>
          </div>
        </GlassCard>

        <GlassCard className="mb-6">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Shield className="w-4 h-4" />
            Local Model (Zero Tokens)
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-white font-medium">Enable Local Model</p>
                <p className="text-xs text-gray-500">Requires torch installed in the container</p>
              </div>
              <button
                onClick={() => setLocalEnabled(!localEnabled)}
                className={`w-12 h-6 rounded-full transition-all ${
                  localEnabled ? 'bg-green-500' : 'bg-gray-600'
                }`}
              >
                <div className={`w-5 h-5 rounded-full bg-white transition-transform ${
                  localEnabled ? 'translate-x-6' : 'translate-x-0.5'
                }`} />
              </button>
            </div>
            <div className="space-y-2">
              <label className="text-xs font-medium text-gray-400 ml-1 uppercase tracking-wider">Local Model Name</label>
              <input
                type="text"
                value={localModel}
                onChange={(e) => setLocalModel(e.target.value)}
                className="w-full px-4 py-3 glass-input focus:ring-2 ring-indigo-500/20 transition-all"
              />
            </div>
          </div>
        </GlassCard>

        <GlassCard className="mb-8">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Cpu className="w-4 h-4" />
            Allowed Fireworks Models
          </h3>
          <div className="space-y-2">
            <label className="text-xs font-medium text-gray-400 ml-1 uppercase tracking-wider">Comma-separated model IDs</label>
            <textarea
              value={allowedModels}
              onChange={(e) => setAllowedModels(e.target.value)}
              className="w-full px-4 py-3 glass-input focus:ring-2 ring-indigo-500/20 transition-all h-24 resize-none font-mono text-xs"
              placeholder="accounts/fireworks/models/gemma-2-9b-it"
            />
            <p className="text-xs text-gray-500">Leave empty to allow all available models</p>
          </div>
        </GlassCard>
      </div>

      <div className="fixed bottom-0 left-0 right-0 z-50 p-6 bg-gradient-to-t from-black via-black/95 to-transparent">
        <div className="max-w-3xl mx-auto">
          <button
            onClick={handleSave}
            disabled={loading}
            className="w-full py-4 px-8 rounded-2xl font-bold text-lg flex items-center justify-center gap-3 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              color: 'white',
              boxShadow: '0 4px 20px rgba(99, 102, 241, 0.4)',
            }}
          >
            {loading ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                Save Changes
              </>
            )}
          </button>
        </div>
      </div>
    </main>
  )
}
