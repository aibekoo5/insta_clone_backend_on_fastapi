"use client"

import { useState, useEffect } from "react"
import Image from "next/image"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Bell, Heart, MessageCircle, UserPlus, Check } from "lucide-react"

interface Notification {
  id: number
  type: "like" | "comment" | "follow" | "mention"
  username: string
  avatar: string
  content: string
  postImage?: string
  time: string
  unread: boolean
}

export function Notifications() {
  const [notifications, setNotifications] = useState<Notification[]>([])

  useEffect(() => {
    // Replace with your actual backend URL
    fetch("http://localhost:8000/notifications/", {
      credentials: "include", // send cookies for authentication
    })
      .then((res) => res.json())
      .then((data) => {
        // Map backend notifications to frontend Notification interface
        const mapped = data.map((n: any) => ({
          id: n.id,
          type: n.notification_type,
          username: n.sender?.username || "unknown",
          avatar: n.sender?.profile_picture || "/placeholder.svg?height=40&width=40",
          content:
            n.notification_type === "like"
              ? "liked your post"
              : n.notification_type === "comment"
              ? "commented on your post"
              : n.notification_type === "follow"
              ? "started following you"
              : n.notification_type === "mention"
              ? "mentioned you"
              : "notification",
          postImage: n.post?.image_url || undefined,
          time: new Date(n.created_at).toLocaleString(), // You can format as needed
          unread: !n.is_read,
        }))
        setNotifications(mapped)
      })
      .catch((err) => {
        // handle error
        console.error(err)
      })
  }, [])

  const markAllAsRead = () => {
    fetch("http://localhost:8000/notifications/read-all", {
      method: "POST",
      credentials: "include",
    }).then(() => {
      setNotifications((prev) =>
        prev.map((notification) => ({ ...notification, unread: false }))
      )
    })
  }

  const getNotificationIcon = (type: Notification["type"]) => {
    switch (type) {
      case "like":
        return <Heart className="h-4 w-4 text-red-500" />
      case "comment":
        return <MessageCircle className="h-4 w-4 text-green-500" />
      case "follow":
        return <UserPlus className="h-4 w-4 text-purple-500" />
      case "mention":
        return <MessageCircle className="h-4 w-4 text-blue-500" />
      default:
        return <Bell className="h-4 w-4" />
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Notifications</h1>
        <Button variant="ghost" size="sm" onClick={markAllAsRead}>
          <Check className="mr-2 h-4 w-4" />
          Mark all as read
        </Button>
      </div>

      <div className="space-y-2">
        {notifications.map((notification) => (
          <Card
            key={notification.id}
            className={`flex items-center gap-4 p-4 ${notification.unread ? "bg-muted/40" : ""}`}
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-muted">
              {getNotificationIcon(notification.type)}
            </div>

            <div className="flex-1 space-y-1">
              <div className="flex items-center gap-1">
                <Link href={`/profile/${notification.username}`} className="font-medium hover:underline">
                  {notification.username}
                </Link>
                <span className="text-sm text-muted-foreground">{notification.content}</span>
              </div>
              <p className="text-xs text-muted-foreground">{notification.time}</p>
            </div>

            {notification.postImage && (
              <Link href="#" className="shrink-0">
                <Image
                  src={notification.postImage || "/placeholder.svg"}
                  alt="Post"
                  width={40}
                  height={40}
                  className="rounded-md object-cover"
                />
              </Link>
            )}

            {notification.type === "follow" && (
              <Button variant="outline" size="sm" className="shrink-0">
                Follow
              </Button>
            )}
          </Card>
        ))}
      </div>
    </div>
  )
}