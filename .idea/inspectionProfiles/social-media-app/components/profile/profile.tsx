"use client"

import { useState } from "react"
import { useEffect } from "react"
import Image from "next/image"
import Link from "next/link"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Settings, Grid, Bookmark, Film, Lock, MoreHorizontal, Edit } from "lucide-react"
import { EditProfileForm } from "@/components/profile/edit-profile-form"

export function Profile() {
  const [isFollowing, setIsFollowing] = useState(false)
  const [isEditProfileOpen, setIsEditProfileOpen] = useState(false)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)
  const [posts, setPosts] = useState<Post[]>([])
  const [savedPosts, setSavedPosts] = useState<Post[]>([])
  const [reels, setReels] = useState<Reel[]>([])

  interface Profile {
    id: number
    username: string
    email: string
    fullName: string
    avatar: string
    bio: string
    postsCount: number
    followersCount: number
    followingCount: number
    isCurrentUser: boolean
    // add other fields as needed
  }

  interface Post {
    id: number
    image: string
    isPrivate?: boolean
  }

  interface Reel {
    id: number
    image: string
  }

  useEffect(() => {
    fetch("/api/profile/me", {
      credentials: "include", // send cookies for authentication
    })
      .then((res) => res.json())
      .then((data) => {
        setProfile(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))

    fetch("/api/posts", { credentials: "include" })
      .then(res => res.json())
      .then(data => setPosts(data))
      .catch(() => setPosts([]))

    // Fetch saved posts
    fetch("/api/saved-posts", { credentials: "include" })
      .then(res => res.json())
      .then(data => setSavedPosts(data))
      .catch(() => setSavedPosts([]))

    // Fetch reels
    fetch("/api/reels", { credentials: "include" })
      .then(res => res.json())
      .then(data => setReels(data))
      .catch(() => setReels([]))
  }, [])

  // Optionally, handle loading state
  if (loading) {
    return <div>Loading...</div>
  }

  if (!profile) {
    return <div>Profile not found.</div>
  }


  const handleFollowToggle = () => {
    setIsFollowing(!isFollowing)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-6 md:flex-row md:items-center md:gap-10">
        <div className="flex justify-center md:block">
          <div className="relative h-20 w-20 md:h-40 md:w-40">
            <Image
              src={profile.avatar || "/placeholder.svg"}
              alt={profile.username}
              fill
              className="rounded-full object-cover"
            />
          </div>
        </div>

        <div className="flex-1 space-y-4">
          <div className="flex flex-col items-center gap-4 md:flex-row">
            <h1 className="text-2xl font-bold">{profile.username}</h1>
            {profile.isCurrentUser ? (
              <div className="flex gap-2">
                <EditProfileForm profile={profile} onSuccess={() => setIsEditProfileOpen(false)} />

                <Link href="/settings">
                  <Button variant="ghost" size="icon" className="h-9 w-9">
                    <Settings className="h-4 w-4" />
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="flex gap-2">
                <Button variant={isFollowing ? "outline" : "default"} onClick={handleFollowToggle}>
                  {isFollowing ? "Following" : "Follow"}
                </Button>
                <Button variant="outline">Message</Button>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-9 w-9">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem>Report</DropdownMenuItem>
                    <DropdownMenuItem>Block</DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            )}
          </div>

          <div className="flex justify-center gap-8 md:justify-start">
            <div className="flex flex-col items-center md:items-start">
              <span className="font-bold">{profile.postsCount}</span>
              <span className="text-sm text-muted-foreground">posts</span>
            </div>
            <Link href="/followers" className="flex flex-col items-center md:items-start">
              <span className="font-bold">{profile.followersCount}</span>
              <span className="text-sm text-muted-foreground">followers</span>
            </Link>
            <Link href="/following" className="flex flex-col items-center md:items-start">
              <span className="font-bold">{profile.followingCount}</span>
              <span className="text-sm text-muted-foreground">following</span>
            </Link>
          </div>

          <div className="text-center md:text-left">
            <p className="font-medium">{profile.fullName}</p>
            <p className="text-sm">{profile.bio}</p>
          </div>
        </div>
      </div>

      <Separator />

      <Tabs defaultValue="posts">
        <TabsList className="w-full">
          <TabsTrigger value="posts" className="flex-1">
            <Grid className="mr-2 h-4 w-4" />
            Posts
          </TabsTrigger>
          <TabsTrigger value="saved" className="flex-1">
            <Bookmark className="mr-2 h-4 w-4" />
            Saved
          </TabsTrigger>
          <TabsTrigger value="reels" className="flex-1">
            <Film className="mr-2 h-4 w-4" />
            Reels
          </TabsTrigger>
        </TabsList>

        <TabsContent value="posts" className="mt-6">
          <div className="grid grid-cols-3 gap-1 md:gap-2">
            {posts.map((post) => (
              <Link key={post.id} href={`/posts/${post.id}`} className="relative aspect-square">
                <Image src={post.image || "/placeholder.svg"} alt={`Post ${post.id}`} fill className="object-cover" />
                {post.isPrivate && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black/60">
                    <Lock className="h-6 w-6 text-white" />
                  </div>
                )}
              </Link>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="saved" className="mt-6">
          <div className="grid grid-cols-3 gap-1 md:gap-2">
            {savedPosts.map((post) => (
              <Link key={post.id} href={`/posts/${post.id}`} className="relative aspect-square">
                <Image src={post.image || "/placeholder.svg"} alt={`Post ${post.id}`} fill className="object-cover" />
              </Link>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="reels" className="mt-6">
          <div className="grid grid-cols-3 gap-1 md:gap-2">
            {reels.map((reel) => (
              <Link key={reel.id} href={`/reels/${reel.id}`} className="relative aspect-square">
                <Image src={reel.image || "/placeholder.svg"} alt={`Reel ${reel.id}`} fill className="object-cover" />
              </Link>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
