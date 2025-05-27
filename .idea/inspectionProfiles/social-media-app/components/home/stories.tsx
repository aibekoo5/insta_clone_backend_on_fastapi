"use client"

import { useState, useEffect } from "react"
import Image from "next/image"
import { Card } from "@/components/ui/card"
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"
import { Plus } from "lucide-react"
import { get } from "@/lib/api" // Make sure this import path is correct
import { Dialog, DialogContent } from "@/components/ui/dialog"

interface Story {
  id: string
  username: string
  avatar: string
  isCreate?: boolean
}

export function Stories() {
  const [stories, setStories] = useState<Story[]>([])
  const [activeStory, setActiveStory] = useState<Story | null>(null)
  const [currentUser, setCurrentUser] = useState<{ username: string; avatar: string } | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false)

  useEffect(() => {
    async function fetchStories() {
      try {
        const user = await get("/profile/me");
        setCurrentUser(user);
        // Fetch stories from your backend
        const data = await get("/media/stories/following")
        // Optionally, fetch your own story and prepend it
        const myStories = await get("/media/stories/me")
        // Map backend data to your Story interface
        const mappedStories: Story[] = [
          {
            id: "create",
            username: "Add new",
            isCreate: true,
            avatar: user.avatar || "/placeholder.svg?height=70&width=70", // Use current user's avatar
          },
          ...myStories.map((story: any) => ({
            id: String(story.id),
            username: story.user.username,
            avatar: story.user.avatar || "/placeholder.svg?height=70&width=70",
          })),
          ...data.map((story: any) => ({
            id: String(story.id),
            username: story.user.username,
            avatar: story.user.avatar || "/placeholder.svg?height=70&width=70",
          })),
        ];
        setStories(mappedStories)
      } catch (error) {
          setStories([
            {
              id: "create",
              username: "Add new",
              isCreate: true,
              avatar: "/placeholder.svg?height=70&width=70",
            },
          ]);
        } 
    }
    fetchStories()
  }, [])

  const handleStoryClick = (id: string) => {
    if (id === "create") {
      console.log("Create story clicked")
      return
    }
    const story = stories.find((s) => s.id === id) || null
    setActiveStory(story)
    setIsModalOpen(true)
  }
  const handleCloseModal = () => {
    setIsModalOpen(false)
    setActiveStory(null)
  }

return (
    <Card className="px-4 py-3">
      <ScrollArea className="w-full">
        <div className="flex gap-3">
          {stories.map((story) => (
            <button
              key={story.id}
              className="flex flex-col items-center gap-1"
              onClick={() => handleStoryClick(story.id)}
            >
              <div
                className={`relative h-[70px] w-[70px] rounded-full ${
                  story.isCreate ? "bg-muted" : "bg-gradient-to-br from-pink-500 via-red-500 to-yellow-500"
                } p-[2px]`}
              >
                <div className="flex h-full w-full items-center justify-center rounded-full bg-background">
                  {story.isCreate ? (
                    <Plus className="h-8 w-8 text-foreground" />
                  ) : (
                    <Image
                      src={story.avatar || "/placeholder.svg"}
                      alt={story.username}
                      height={66}
                      width={66}
                      className="rounded-full object-cover"
                    />
                  )}
                </div>
              </div>
              <span className="text-xs">{story.username}</span>
            </button>
          ))}
        </div>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>
      {/* Modal for viewing story */}
      {activeStory && (
        <Dialog open={isModalOpen} onOpenChange={handleCloseModal}>
          <DialogContent>
            <div className="flex flex-col items-center">
              <Image
                src={activeStory.avatar || "/placeholder.svg"}
                alt={activeStory.username}
                height={120}
                width={120}
                className="rounded-full object-cover mb-4"
              />
              <span className="font-bold text-lg mb-2">{activeStory.username}</span>
              {/* Add more story content here if needed */}
              <button onClick={handleCloseModal} className="mt-4 px-4 py-2 bg-gray-200 rounded">
                Close
              </button>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </Card>
  )
}