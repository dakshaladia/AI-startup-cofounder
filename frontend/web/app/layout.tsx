import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI Startup Co-Founder',
  description: 'Multimodal AI Startup Co-Founder with multi-agent pipeline',
  keywords: ['AI', 'startup', 'co-founder', 'multimodal', 'ideas', 'innovation'],
  authors: [{ name: 'AI Startup Co-Founder Team' }],
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          {children}
        </div>
      </body>
    </html>
  )
}
