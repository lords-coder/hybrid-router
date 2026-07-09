import './globals.css'

export const metadata = {
  title: 'Hybrid Token-Efficient Routing Agent',
  description: 'Intelligent Fireworks AI model routing - local-first, zero-token optimization',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
