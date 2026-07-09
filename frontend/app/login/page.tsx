'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import Navbar from '@/components/Navbar'
import AnimatedBackground from '@/components/AnimatedBackground'
import GlassCard from '@/components/GlassCard'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Lock, Mail, ArrowRight, Loader2, CheckCircle, AlertCircle, KeyRound } from 'lucide-react'
import { supabase } from '@/services/supabase'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [mode, setMode] = useState<'login' | 'reset'>('login')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    if (!email || !password) {
      setError('Please fill in all fields')
      setLoading(false)
      return
    }

    const { data, error: authError } = await supabase.auth.signInWithPassword({
      email,
      password
    })

    if (authError) {
      setError(authError.message)
      setLoading(false)
      return
    }

    setSuccess('Signed in successfully! Redirecting...')
    setTimeout(() => router.push('/router'), 1000)
  }

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    if (!email) {
      setError('Please enter your email address')
      setLoading(false)
      return
    }

    const { error: resetError } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/login`,
    })

    if (resetError) {
      setError(resetError.message)
      setLoading(false)
      return
    }

    setSuccess('Password reset email sent! Check your inbox.')
    setLoading(false)
  }

  return (
    <main className="min-h-screen relative flex items-center justify-center px-6">
      <AnimatedBackground />
      <Navbar />

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-md"
      >
        <GlassCard className="p-10">
          <div className="text-center mb-10">
            <h1 className="text-3xl font-bold text-white mb-2">
              {mode === 'login' ? 'Welcome Back' : 'Reset Password'}
            </h1>
            <p className="text-gray-400 text-sm">
              {mode === 'login'
                ? 'Sign in to access the routing dashboard'
                : 'Enter your email to receive a reset link'}
            </p>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 p-3 rounded-xl bg-red-500/10 border border-red-500/20 mb-6"
            >
              <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
              <p className="text-red-400 text-sm">{error}</p>
            </motion.div>
          )}

          {success && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 p-3 rounded-xl bg-green-500/10 border border-green-500/20 mb-6"
            >
              <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
              <p className="text-green-400 text-sm">{success}</p>
            </motion.div>
          )}

          {mode === 'login' ? (
            <form className="space-y-6" onSubmit={handleLogin}>
              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 ml-1 uppercase tracking-wider">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 glass-input focus:ring-2 ring-indigo-500/20 transition-all"
                    placeholder="name@company.com"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 ml-1 uppercase tracking-wider">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 glass-input focus:ring-2 ring-indigo-500/20 transition-all"
                    placeholder="Enter your password"
                  />
                </div>
              </div>

              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={() => { setMode('reset'); setError(''); setSuccess('') }}
                  className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
                >
                  Forgot password?
                </button>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="premium-button w-full py-3 flex items-center justify-center gap-2 text-base disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Signing In...
                  </>
                ) : (
                  <>
                    Sign In
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          ) : (
            <form className="space-y-6" onSubmit={handleResetPassword}>
              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-400 ml-1 uppercase tracking-wider">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 glass-input focus:ring-2 ring-indigo-500/20 transition-all"
                    placeholder="name@company.com"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="premium-button w-full py-3 flex items-center justify-center gap-2 text-base disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Sending Reset Link...
                  </>
                ) : (
                  <>
                    <KeyRound className="w-4 h-4" />
                    Send Reset Link
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={() => { setMode('login'); setError(''); setSuccess('') }}
                className="w-full text-center text-sm text-gray-400 hover:text-white transition-colors"
              >
                Back to Sign In
              </button>
            </form>
          )}

          {mode === 'login' && (
            <div className="mt-8 text-center">
              <p className="text-sm text-gray-500">
                Don't have an account?{' '}
                <Link href="/signup" className="text-white font-medium hover:underline">
                  Create one
                </Link>
              </p>
            </div>
          )}
        </GlassCard>
      </motion.div>
    </main>
  )
}
