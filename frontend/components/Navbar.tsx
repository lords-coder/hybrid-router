'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter, usePathname } from 'next/navigation'
import { motion } from 'framer-motion'
import { Brain, Sparkles, Menu, X, LogOut, User } from 'lucide-react'
import { supabase } from '@/services/supabase'

const navLinks = [
  { name: 'Home', href: '/' },
  { name: 'Router', href: '/router' },
  { name: 'Analytics', href: '/analytics' },
  { name: 'Settings', href: '/settings' },
  { name: 'Models', href: '/models' },
]

export default function Navbar() {
  const router = useRouter()
  const pathname = usePathname()
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      setUser(user)
      setLoading(false)
    }
    getUser()

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      setUser(session?.user ?? null)
    })

    return () => subscription.unsubscribe()
  }, [])

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const handleLogout = async () => {
    await supabase.auth.signOut()
    setUser(null)
    router.push('/')
  }

  const hideAuth = pathname === '/login' || pathname === '/signup'

  return (
    <header className="fixed top-0 left-0 right-0 z-50 flex justify-center p-6">
      <motion.nav
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className={`
          flex items-center justify-between px-6 py-3 rounded-full transition-all duration-500
          ${scrolled
            ? 'glass-panel w-full max-w-4xl'
            : 'bg-transparent w-full max-w-6xl'}
        `}
      >
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center transition-transform group-hover:rotate-12">
            <Brain className="w-5 h-5 text-black" />
          </div>
          <span className="text-sm font-medium text-white tracking-tight">Token Router</span>
        </Link>

        <div className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              href={link.href}
              className="text-xs font-medium text-gray-400 hover:text-white transition-colors duration-200"
            >
              {link.name}
            </Link>
          ))}

          {!hideAuth && (
            <div className="flex items-center gap-4 ml-4 pl-4 border-l border-white/10">
              {loading ? (
                <div className="w-20 h-8 rounded-full bg-white/5 animate-pulse" />
              ) : user ? (
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
                    <div className="w-5 h-5 rounded-full bg-indigo-500 flex items-center justify-center">
                      <User className="w-3 h-3 text-white" />
                    </div>
                    <span className="text-xs font-medium text-white max-w-[100px] truncate">
                      {user.email?.split('@')[0]}
                    </span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="p-2 rounded-full hover:bg-white/10 transition-colors group"
                    title="Sign Out"
                  >
                    <LogOut className="w-4 h-4 text-gray-400 group-hover:text-white" />
                  </button>
                </div>
              ) : (
                <>
                  <Link href="/login" className="text-xs font-medium text-gray-400 hover:text-white transition-colors">
                    Sign In
                  </Link>
                  <Link
                    href="/signup"
                    className="px-4 py-1.5 bg-white text-black text-xs font-bold rounded-full hover:bg-gray-200 transition-all"
                  >
                    Get Started
                  </Link>
                </>
              )}
            </div>
          )}
        </div>

        <button
          className="md:hidden p-2 text-gray-400"
          onClick={() => setMobileOpen(!mobileOpen)}
        >
          {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </motion.nav>
    </header>
  )
}
