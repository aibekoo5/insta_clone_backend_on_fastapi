"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Home, Search, User, PlusSquare, Bell } from "lucide-react"
import { cn } from "@/lib/utils"

export function MainNav() {
  const pathname = usePathname()

  const links = [
    {
      name: "Home",
      href: "/",
      icon: <Home className="h-5 w-5" />,
    },
    {
      name: "Explore",
      href: "/explore",
      icon: <Search className="h-5 w-5" />,
    },
    {
      name: "Create",
      href: "/create",
      icon: <PlusSquare className="h-5 w-5" />,
    },
    {
      name: "Notifications",
      href: "/notifications",
      icon: <Bell className="h-5 w-5" />,
    },
    {
      name: "Profile",
      href: "/profile",
      icon: <User className="h-5 w-5" />,
    },
  ]

  return (
    <nav className="fixed bottom-0 left-0 z-50 w-full border-t bg-background md:relative md:border-r md:border-t-0 md:h-screen md:w-14 lg:w-64">
      <div className="hidden items-center px-4 py-4 md:flex">
        <Link href="/" className="flex items-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="mr-2 h-6 w-6"
          >
            <path d="M15 6v12a3 3 0 1 0 3-3H6a3 3 0 1 0 3 3V6a3 3 0 1 0-3 3h12a3 3 0 1 0-3-3" />
          </svg>
          <span className="hidden text-xl font-bold lg:inline-block">SocialApp</span>
        </Link>
      </div>
      <div className="flex h-16 items-center justify-around md:h-auto md:flex-col md:items-center md:justify-start md:gap-4 md:px-2 md:py-8">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={cn(
              "flex h-9 w-9 items-center justify-center rounded-md p-0 md:h-10 md:w-10 lg:w-full lg:justify-start lg:px-3",
              pathname === link.href
                ? "bg-primary/10 text-primary"
                : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
            )}
          >
            <span className="flex items-center">
              {link.icon}
              <span className="hidden lg:ml-2 lg:inline-block">{link.name}</span>
            </span>
          </Link>
        ))}
      </div>
    </nav>
  )
}
