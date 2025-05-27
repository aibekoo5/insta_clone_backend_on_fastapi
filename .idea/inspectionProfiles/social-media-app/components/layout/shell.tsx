import type React from "react"
import { MainNav } from "@/components/layout/main-nav"
import { RightSidebar } from "@/components/layout/right-sidebar"

interface ShellProps {
  children: React.ReactNode
}

export function Shell({ children }: ShellProps) {
  return (
    <div className="flex min-h-screen">
      <MainNav />
      <main className="flex-1 pb-20 md:ml-14 md:pb-0 lg:ml-64">
        <div className="mx-auto max-w-4xl p-4 md:p-6">{children}</div>
      </main>
      <RightSidebar />
    </div>
  )
}
