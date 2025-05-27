"use client"

import { useState, useEffect } from "react"
import Image from "next/image"
import Link from "next/link"
import { Heart, MessageCircle, Share2, Bookmark, MoreHorizontal } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { get } from "@/lib/api"

interface Post {
  id: number
  username: string
  userAvatar: string
  image: string
  caption: string
  likesCount: number
  commentsCount: number
  liked: boolean
  saved: boolean
  comments: { id: number; username: string; text: string }[]
}

export function Feed() {
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [newComments, setNewComments] = useState<Record<number, string>>({})
  const [currentUser, setCurrentUser] = useState<{ username: string } | null>(null);

    useEffect(() => {
      async function fetchCurrentUser() {
        try {
          const user = await get("/profile/me");
          setCurrentUser(user);
        } catch {
          setCurrentUser(null);
        }
      }

      async function fetchPosts() {
        setLoading(true)
        setError(null)
        try {
          // Fetch posts from your backend
          const data = await get("/posts/")
          // Map backend data to your Post interface if needed
          const mappedPosts = data.map((post: any) => ({
            id: post.id,
            username: post.owner.username,
            userAvatar: post.owner.profile_picture || "/placeholder.svg?height=32&width=32",
            image: post.image_url || "/placeholder.svg?height=600&width=600",
            caption: post.caption,
            likesCount: post.likes_count ?? 0,
            commentsCount: post.comments_count ?? 0,
            liked: post.liked ?? false,
            saved: post.saved ?? false,
            comments: post.comments?.map((c: any) => ({
              id: c.id,
              username: c.user.username,
              text: c.text,
            })) ?? [],
          }))
          setPosts(mappedPosts)
        } catch (err: any) {
          setError("Failed to load posts")
        } finally {
          setLoading(false)
        }
      }
      fetchCurrentUser();
      fetchPosts()
    }, [])

  const handleLike = (postId: number) => {
    setPosts((prevPosts) =>
      prevPosts.map((post) =>
        post.id === postId
          ? {
              ...post,
              liked: !post.liked,
              likesCount: post.liked ? post.likesCount - 1 : post.likesCount + 1,
            }
          : post,
      ),
    )
  }

  const handleSave = (postId: number) => {
    setPosts((prevPosts) => prevPosts.map((post) => (post.id === postId ? { ...post, saved: !post.saved } : post)))
  }

  const handleCommentChange = (postId: number, value: string) => {
    setNewComments({ ...newComments, [postId]: value })
  }

  const handleAddComment = (postId: number) => {
    if (!newComments[postId]?.trim() || !currentUser) return;

    setPosts((prevPosts) =>
      prevPosts.map((post) =>
        post.id === postId
          ? {
              ...post,
              comments: [
                ...post.comments,
                {
                  id: post.comments.length + 1,
                  username: currentUser.username, // Use actual logged-in user
                  text: newComments[postId],
                },
              ],
              commentsCount: post.commentsCount + 1,
            }
          : post,
      ),
    );

    setNewComments({ ...newComments, [postId]: "" });
  };

    if (loading) {
      return <div>Loading...</div>
    }

    if (error) {
      return <div className="text-red-500">{error}</div>
    }

  return (
    <div className="space-y-4">
      {posts.map((post) => (
        <Card key={post.id} className="overflow-hidden">
          <CardHeader className="p-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Image
                  src={post.userAvatar || "/placeholder.svg"}
                  alt={post.username}
                  width={32}
                  height={32}
                  className="rounded-full object-cover"
                />
                <Link href={`/profile/${post.username}`} className="font-medium">
                  {post.username}
                </Link>
              </div>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <MoreHorizontal className="h-5 w-5" />
              </Button>
            </div>
          </CardHeader>
          <Image
            src={post.image || "/placeholder.svg"}
            alt={post.caption}
            width={600}
            height={600}
            className="aspect-square w-full object-cover"
          />
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex gap-3">
                <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => handleLike(post.id)}>
                  <Heart className={`h-5 w-5 ${post.liked ? "fill-red-500 text-red-500" : ""}`} />
                </Button>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <MessageCircle className="h-5 w-5" />
                </Button>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Share2 className="h-5 w-5" />
                </Button>
              </div>
              <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => handleSave(post.id)}>
                <Bookmark className={`h-5 w-5 ${post.saved ? "fill-foreground" : ""}`} />
              </Button>
            </div>
            <div className="mt-3">
              <p className="text-sm font-medium">{post.likesCount} likes</p>
              <div className="mt-1 text-sm">
                <span className="font-medium">{post.username}</span> <span>{post.caption}</span>
              </div>
              {post.commentsCount > 0 && (
                <button className="mt-1 text-xs text-muted-foreground">View all {post.commentsCount} comments</button>
              )}
            </div>
            <ScrollArea className="mt-2 max-h-24">
              {post.comments.map((comment) => (
                <div key={comment.id} className="flex gap-2 py-1 text-sm">
                  <span className="font-medium">{comment.username}</span>
                  <span>{comment.text}</span>
                </div>
              ))}
            </ScrollArea>
          </CardContent>
          <Separator />
          <CardFooter className="p-3">
            <div className="flex w-full items-center gap-2">
              <Input
                value={newComments[post.id] || ""}
                onChange={(e) => handleCommentChange(post.id, e.target.value)}
                placeholder="Add a comment..."
                className="border-0 bg-transparent px-0 focus-visible:ring-0"
              />
              <Button
                onClick={() => handleAddComment(post.id)}
                variant="ghost"
                size="sm"
                disabled={!newComments[post.id]?.trim()}
                className="text-primary"
              >
                Post
              </Button>
            </div>
          </CardFooter>
        </Card>
      ))}
    </div>
  )
}
