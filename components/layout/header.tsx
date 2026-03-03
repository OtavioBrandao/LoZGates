"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Zap, BookOpen } from "lucide-react"

const navItems = [
  { href: "/", label: "Inicio", icon: Zap },
  { href: "/problems", label: "Problemas", icon: BookOpen },
]

export function Header() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-50 flex items-center justify-between border-b border-border bg-background/80 px-4 py-3 backdrop-blur-md md:px-6">
      <Link href="/" className="flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 glow-cyan-sm">
          <Zap className="h-5 w-5 text-primary" />
        </div>
        <span className="font-mono text-lg font-bold text-foreground">
          LoZ<span className="text-primary">Gates</span>
        </span>
      </Link>

      <nav className="flex items-center gap-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <item.icon className="h-4 w-4" />
              <span className="hidden sm:inline">{item.label}</span>
            </Link>
          )
        })}
      </nav>
    </header>
  )
}
