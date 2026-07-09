'use client'

import { motion } from 'framer-motion'
import Navbar from '@/components/Navbar'
import AnimatedBackground from '@/components/AnimatedBackground'
import GlassCard from '@/components/GlassCard'
import Link from 'next/link'
import { Sparkles, Zap, Brain, ArrowRight, Shield, Cpu, BarChart3 } from 'lucide-react'

export default function Home() {
  return (
    <main className="min-h-screen text-white selection:bg-indigo-500/30">
      <AnimatedBackground />
      <Navbar />

      <section className="relative pt-48 pb-32 px-6 overflow-hidden">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-indigo-300 mb-8">
              <Sparkles className="w-3 h-3" />
              <span>Track 1 - AI Agent Track</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold tracking-tighter mb-8 leading-[1.1]">
              Hybrid <span className="text-gradient">Token-Efficient</span> Router
            </h1>

            <p className="text-lg md:text-xl text-gray-400 mb-12 max-w-2xl mx-auto leading-relaxed">
              An AI agent that routes every prompt to the cheapest capable model.
              Local-first strategy: <span className="text-green-400 font-semibold">zero Fireworks tokens</span> for simple tasks,
              cheapest Fireworks model for complex ones.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                href="/router"
                className="premium-button px-8 py-4 flex items-center gap-2 text-lg"
              >
                Launch Router
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                href="/analytics"
                className="px-8 py-4 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all text-lg font-medium"
              >
                View Analytics
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-6 py-20">
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          {[
            {
              icon: Shield,
              title: 'Local-First Routing',
              desc: 'Simple tasks run on a local Qwen 2.5 model inside the container. Zero Fireworks tokens = best possible score.',
              color: 'text-green-400',
              bg: 'bg-green-500/10',
            },
            {
              icon: Zap,
              title: 'Cheapest Fireworks Model',
              desc: 'Complex tasks route to the most cost-effective Fireworks AI model that meets the accuracy threshold.',
              color: 'text-yellow-400',
              bg: 'bg-yellow-500/10',
            },
            {
              icon: Cpu,
              title: 'Gemma 2 Integration',
              desc: 'Gemma 2 9B and 2B models via Fireworks AI for the Best Use of Gemma Models bonus challenge.',
              color: 'text-purple-400',
              bg: 'bg-purple-500/10',
            },
            {
              icon: BarChart3,
              title: '8 Task Categories',
              desc: 'Factual knowledge, math, sentiment, summarization, NER, code debugging, logical reasoning, code generation.',
              color: 'text-blue-400',
              bg: 'bg-blue-500/10',
            },
          ].map((feature, i) => (
            <GlassCard key={i} delay={i * 0.1}>
              <div className={`w-12 h-12 rounded-2xl ${feature.bg} flex items-center justify-center mb-4 border border-white/5`}>
                <feature.icon className={`w-6 h-6 ${feature.color}`} />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-white">{feature.title}</h3>
              <p className="text-gray-400 leading-relaxed text-sm">{feature.desc}</p>
            </GlassCard>
          ))}
        </div>

        <GlassCard delay={0.4}>
          <div className="text-center">
            <h3 className="text-xl font-bold text-white mb-3">Scoring Strategy</h3>
            <p className="text-gray-400 max-w-2xl mx-auto text-sm leading-relaxed">
              Judging is based on <span className="text-white font-medium">token count</span> and <span className="text-white font-medium">output accuracy</span>.
              Local inference uses <span className="text-green-400 font-bold">zero Fireworks tokens</span> while counting fully toward accuracy.
              The router automatically classifies each task and routes to the optimal provider.
            </p>
          </div>
        </GlassCard>
      </section>
    </main>
  )
}
