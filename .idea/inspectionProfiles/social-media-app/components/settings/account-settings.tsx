"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { useEffect } from "react"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
import { toast } from "@/components/ui/use-toast"

const formSchema = z.object({
  username: z.string().min(3, {
    message: "Username must be at least 3 characters",
  }),
  email: z.string().email({
    message: "Please enter a valid email address",
  }),
  fullName: z.string().min(2, {
    message: "Full name must be at least 2 characters",
  }),
  bio: z.string().max(150, {
    message: "Bio must be at most 150 characters",
  }),
  website: z
    .string()
    .url({
      message: "Please enter a valid URL",
    })
    .optional()
    .or(z.literal("")),
  privateAccount: z.boolean(),
})

export function AccountSettings() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
      email: "",
      fullName: "",
      bio: "",
      website: "",
      privateAccount: false,
    },
  })

    useEffect(() => {
    fetch("/api/profile/me", { credentials: "include" })
      .then(res => res.json())
      .then(data => {
        form.reset({
          username: data.username,
          email: data.email,
          fullName: data.full_name || data.fullName || "",
          bio: data.bio || "",
          website: data.website || "",
          privateAccount: data.private_account || false,
        })
      })
      .catch(() => {
        // handle error if needed
      })
    }, [form])

  function onSubmit(values: z.infer<typeof formSchema>) {
    // Send updated settings to backend
    fetch("/api/profile/me", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(values),
    })
      .then(res => {
        if (!res.ok) throw new Error("Failed to update")
        toast({
          title: "Account settings updated",
          description: "Your account settings have been updated successfully",
        })
      })
      .catch(() => {
        toast({
          title: "Error",
          description: "Failed to update account settings.",
          variant: "destructive",
        })
      })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Account Settings</CardTitle>
        <CardDescription>Update your account information.</CardDescription>
      </CardHeader>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <CardContent className="space-y-4">
            <FormField
              control={form.control}
              name="username"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Username</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormDescription>This is your public username.</FormDescription>
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
                  <FormDescription>We'll never share your email with anyone else.</FormDescription>
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
              name="bio"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Bio</FormLabel>
                  <FormControl>
                    <Textarea {...field} rows={3} maxLength={150} />
                  </FormControl>
                  <FormDescription>Tell us a little about yourself.</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="website"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Website</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormDescription>Your personal website or portfolio.</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="privateAccount"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">Private Account</FormLabel>
                    <FormDescription>
                      When your account is private, only people you approve can see your posts and stories.
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  </FormControl>
                </FormItem>
              )}
            />
          </CardContent>
          <CardFooter>
            <Button type="submit">Save changes</Button>
          </CardFooter>
        </form>
      </Form>
    </Card>
  )
}
