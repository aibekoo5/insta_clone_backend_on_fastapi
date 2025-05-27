"use client"

import type React from "react"

import { useState, useRef } from "react"
import Image from "next/image"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { toast } from "@/components/ui/use-toast"
import { ImageIcon, VideoIcon, X } from "lucide-react"

export function CreatePost() {
  const router = useRouter()
  const [postType, setPostType] = useState<"image" | "video">("image")
  const [caption, setCaption] = useState("")
  const [isPrivate, setIsPrivate] = useState(false)
  const [media, setMedia] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (postType === "image" && !file.type.startsWith("image/")) {
      toast({
        title: "Invalid file",
        description: "Please select an image file",
        variant: "destructive",
      })
      return
    }

    if (postType === "video" && !file.type.startsWith("video/")) {
      toast({
        title: "Invalid file",
        description: "Please select a video file",
        variant: "destructive",
      })
      return
    }

    setMedia(file)
    const reader = new FileReader()
    reader.onload = () => {
      setPreview(reader.result as string)
    }
    reader.readAsDataURL(file)
  }

  const handleRemoveMedia = () => {
    setMedia(null)
    setPreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const handleSubmit = async () => {
    if (!media) {
      toast({
        title: "No media selected",
        description: "Please select an image or video to post",
        variant: "destructive",
      });
      return;
    }

    if (!caption.trim()) {
      toast({
        title: "No caption",
        description: "Please add a caption to your post",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);

    try {
      const formData = new FormData();
      formData.append(postType === "image" ? "image" : "video", media);
      formData.append("caption", caption);
      formData.append("is_private", isPrivate.toString());

      const response = await fetch("http://localhost:8000/posts/", {
        method: "POST",
        credentials: "include", // Important for cookie-based auth
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to create post");
      }

      toast({
        title: "Post created",
        description: "Your post has been created successfully",
      });

      router.push("/");
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create post. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTabChange = (value: string) => {
    setPostType(value as "image" | "video")
    setMedia(null)
    setPreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  return (
    <Card className="mx-auto max-w-md">
      <CardHeader>
        <CardTitle>Create Post</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="image" onValueChange={handleTabChange}>
          <TabsList className="w-full">
            <TabsTrigger value="image" className="flex-1">
              <ImageIcon className="mr-2 h-4 w-4" />
              Image
            </TabsTrigger>
            <TabsTrigger value="video" className="flex-1">
              <VideoIcon className="mr-2 h-4 w-4" />
              Video
            </TabsTrigger>
          </TabsList>
          <TabsContent value="image" className="mt-4">
            <div className="space-y-4">
              <div className="flex flex-col gap-2">
                <Label htmlFor="image-upload">Upload image</Label>
                <div className="aspect-square w-full overflow-hidden rounded-md border border-dashed border-muted-foreground/50">
                  {preview ? (
                    <div className="relative h-full w-full">
                      <Button
                        variant="destructive"
                        size="icon"
                        className="absolute right-2 top-2 z-10 h-8 w-8"
                        onClick={handleRemoveMedia}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                      <Image src={preview || "/placeholder.svg"} alt="Preview" fill className="object-cover" />
                    </div>
                  ) : (
                    <label
                      htmlFor="image-upload"
                      className="flex h-full w-full cursor-pointer flex-col items-center justify-center gap-2 p-4 text-center"
                    >
                      <ImageIcon className="h-12 w-12 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">Click to upload or drag and drop</span>
                    </label>
                  )}
                  <input
                    ref={fileInputRef}
                    id="image-upload"
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleFileChange}
                  />
                </div>
              </div>
            </div>
          </TabsContent>
          <TabsContent value="video" className="mt-4">
            <div className="space-y-4">
              <div className="flex flex-col gap-2">
                <Label htmlFor="video-upload">Upload video</Label>
                <div className="aspect-square w-full overflow-hidden rounded-md border border-dashed border-muted-foreground/50">
                  {preview ? (
                    <div className="relative h-full w-full">
                      <Button
                        variant="destructive"
                        size="icon"
                        className="absolute right-2 top-2 z-10 h-8 w-8"
                        onClick={handleRemoveMedia}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                      <video src={preview} controls className="h-full w-full object-cover" />
                    </div>
                  ) : (
                    <label
                      htmlFor="video-upload"
                      className="flex h-full w-full cursor-pointer flex-col items-center justify-center gap-2 p-4 text-center"
                    >
                      <VideoIcon className="h-12 w-12 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">Click to upload or drag and drop</span>
                    </label>
                  )}
                  <input
                    ref={fileInputRef}
                    id="video-upload"
                    type="file"
                    accept="video/*"
                    className="hidden"
                    onChange={handleFileChange}
                  />
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>

        <div className="mt-4 space-y-4">
          <div className="flex flex-col gap-2">
            <Label htmlFor="caption">Caption</Label>
            <Textarea
              id="caption"
              placeholder="Write a caption..."
              rows={4}
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
            />
          </div>

          <div className="flex items-center justify-between">
            <Label htmlFor="private-post" className="text-sm">
              Private post
            </Label>
            <Switch id="private-post" checked={isPrivate} onCheckedChange={setIsPrivate} />
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button className="w-full" onClick={handleSubmit} disabled={!media || !caption.trim() || isSubmitting}>
          {isSubmitting ? "Creating post..." : "Create post"}
        </Button>
      </CardFooter>
    </Card>
  )
}
