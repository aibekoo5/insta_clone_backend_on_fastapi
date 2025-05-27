"use client"
import Image from "next/image"
import Link from "next/link"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search } from "lucide-react"
import { useEffect, useState } from "react"

export function RightSidebar() {
  const [suggestedUsers, setSuggestedUsers] = useState<SuggestedUser[]>([]);
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null);

  interface SuggestedUser {
  id: string;
  username: string;
  profile_picture?: string;
  fullName: string;
  avatar: string;
}

  useEffect(() => {
    async function fetchSuggestedUsers() {
      setLoading(true)
      setError(null)
      try {
        const res = await fetch("/api/search/recommended-users", {
          credentials: "include", // send cookies if using cookie auth
        })
        if (!res.ok) throw new Error("Failed to fetch")
        const data = await res.json()
        setSuggestedUsers(data)
      } catch (err) {
        setError("Could not load suggestions")
      } finally {
        setLoading(false)
      }
    }
    fetchSuggestedUsers()
  }, [])

  const handleFollow = async (userId: string) => {
    try {
      await fetch(`/api/follow/${userId}`, {
        method: "POST",
        credentials: "include",
      })
      // Optionally update UI or refetch suggestions
    } catch (err) {
      alert("Failed to follow user")
    }
  }

  return (
    <div className="hidden lg:block lg:w-80 border-l p-4">
      <div className="sticky top-4 space-y-4">
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Search" className="pl-8" />
        </div>

        <Card className="p-4">
          <h3 className="mb-4 text-lg font-medium">Suggested for you</h3>
          {loading && <p>Loading...</p>}
          {error && <p className="text-red-500">{error}</p>}
          <div className="space-y-4">
            {suggestedUsers.map((user) => (
              <div key={user.id} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Image
                    src={user.profile_picture || "/placeholder.svg"}
                    alt={user.username}
                    height={32}
                    width={32}
                    className="rounded-full object-cover"
                  />
                  <div>
                    <p className="text-sm font-medium">{user.username}</p>
                    <p className="text-xs text-muted-foreground">{user.fullName}</p>
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-8 text-xs"
                  onClick={() => handleFollow(user.id)}
                >
                  Follow
                </Button>
              </div>
            ))}
          </div>
        </Card>

        <div className="text-xs text-muted-foreground">
          <div className="flex flex-wrap gap-2">
            <Link href="#" className="hover:underline">
              About
            </Link>
            <Link href="#" className="hover:underline">
              Help
            </Link>
            <Link href="#" className="hover:underline">
              Privacy
            </Link>
            <Link href="#" className="hover:underline">
              Terms
            </Link>
            <Link href="#" className="hover:underline">
              API
            </Link>
          </div>
          <p className="mt-4">© 2024 SocialApp</p>
        </div>
      </div>
    </div>
  )
}