"use client"

import type React from "react"

import { useState } from "react"
import Image from "next/image"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "@/components/ui/use-toast"
import { Camera } from "lucide-react"

const formSchema = z.object({
  username: z.string().min(3, {
    message: "Username must be at least 3 characters",
  }),
  fullName: z.string().min(2, {
    message: "Full name must be at least 2 characters",
  }),
  email: z.string().email({
    message: "Please enter a valid email address",
  }),
  bio: z.string().max(150, {
    message: "Bio must be at most 150 characters",
  }),
})

interface ProfileType {
  id: number
  username: string
  fullName: string
  email: string 
  avatar: string
  bio: string
  postsCount: number
  followersCount: number
  followingCount: number
  isCurrentUser: boolean
}

interface EditProfileFormProps {
  profile: ProfileType
  onSuccess: () => void
}

export function EditProfileForm({ profile, onSuccess }: EditProfileFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [avatarFile, setAvatarFile] = useState<File | null>(null)
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null)

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: profile.username,
      fullName: profile.fullName,
      email: profile.email, // Use the real email from the profile
      bio: profile.bio,
    },
  })

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.type.startsWith("image/")) {
      toast({
        title: "Invalid file",
        description: "Please select an image file",
        variant: "destructive",
      })
      return
    }

    setAvatarFile(file)
    const reader = new FileReader()
    reader.onload = () => {
      setAvatarPreview(reader.result as string)
    }
    reader.readAsDataURL(file)
  }

  async function onSubmit(values: z.infer<typeof formSchema>) {
  setIsSubmitting(true);

  try {
    const formData = new FormData();
    formData.append("username", values.username);
    formData.append("full_name", values.fullName);
    formData.append("email", values.email);
    formData.append("bio", values.bio);
    if (avatarFile) {
      formData.append("profile_picture", avatarFile);
    }

    const response = await fetch("/api/profile/me", {
      method: "PUT",
      body: formData,
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error("Failed to update profile");
    }

    toast({
      title: "Profile updated",
      description: "Your profile has been updated successfully",
    });

    onSuccess();
  } catch (error) {
    toast({
      title: "Error",
      description: "Failed to update profile. Please try again.",
      variant: "destructive",
    });
  } finally {
    setIsSubmitting(false);
  }
}

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <div className="flex justify-center">
          <div className="relative">
            <div className="relative h-24 w-24 overflow-hidden rounded-full">
              <Image src={avatarPreview || profile.avatar} alt={profile.username} fill className="object-cover" />
            </div>
            <label
              htmlFor="avatar-upload"
              className="absolute bottom-0 right-0 flex h-8 w-8 cursor-pointer items-center justify-center rounded-full bg-primary text-primary-foreground"
            >
              <Camera className="h-4 w-4" />
              <span className="sr-only">Change avatar</span>
            </label>
            <input id="avatar-upload" type="file" accept="image/*" className="hidden" onChange={handleAvatarChange} />
          </div>
        </div>

        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="fullName"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Full Name</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="bio"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Bio</FormLabel>
              <FormControl>
                <Textarea {...field} rows={3} maxLength={150} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex gap-2">
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Saving..." : "Save changes"}
          </Button>
          <Button type="button" variant="outline" onClick={onSuccess}>
            Cancel
          </Button>
        </div>
      </form>
    </Form>
  )
}
