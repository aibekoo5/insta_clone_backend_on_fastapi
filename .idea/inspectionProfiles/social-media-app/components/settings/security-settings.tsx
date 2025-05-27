"use client"

import { Label } from "@/components/ui/label"

import { useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Switch } from "@/components/ui/switch"
import { toast } from "@/components/ui/use-toast"

const passwordFormSchema = z
  .object({
    currentPassword: z.string().min(8, {
      message: "Password must be at least 8 characters",
    }),
    newPassword: z.string().min(8, {
      message: "Password must be at least 8 characters",
    }),
    confirmPassword: z.string(),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  })

export function SecuritySettings() {
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false)

  const passwordForm = useForm<z.infer<typeof passwordFormSchema>>({
    resolver: zodResolver(passwordFormSchema),
    defaultValues: {
      currentPassword: "",
      newPassword: "",
      confirmPassword: "",
    },
  })

async function onPasswordSubmit(values: z.infer<typeof passwordFormSchema>) {
  try {
    const response = await fetch("/api/auth/change-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        current_password: values.currentPassword,
        new_password: values.newPassword,
      }),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || "Failed to change password");
    }

    toast({
      title: "Password changed",
      description: "Your password has been changed successfully",
    });

    passwordForm.reset();
  } catch (error: any) {
    toast({
      title: "Error",
      description: error.message || "Failed to change password",
      variant: "destructive",
    });
  }
}

async function toggleTwoFactor() {
  try {
    const response = await fetch("/api/auth/two-factor", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ enable: !twoFactorEnabled }),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || "Failed to update two-factor authentication");
    }

    setTwoFactorEnabled(!twoFactorEnabled);

    toast({
      title: !twoFactorEnabled
        ? "Two-factor authentication enabled"
        : "Two-factor authentication disabled",
      description: !twoFactorEnabled
        ? "Two-factor authentication has been enabled for your account"
        : "Two-factor authentication has been disabled for your account",
    });
  } catch (error: any) {
    toast({
      title: "Error",
      description: error.message || "Failed to update two-factor authentication",
      variant: "destructive",
    });
  }
}

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Change Password</CardTitle>
          <CardDescription>Update your password to keep your account secure.</CardDescription>
        </CardHeader>
        <Form {...passwordForm}>
          <form onSubmit={passwordForm.handleSubmit(onPasswordSubmit)}>
            <CardContent className="space-y-4">
              <FormField
                control={passwordForm.control}
                name="currentPassword"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Current Password</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="••••••••" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={passwordForm.control}
                name="newPassword"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>New Password</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="••••••••" {...field} />
                    </FormControl>
                    <FormDescription>Password must be at least 8 characters long.</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={passwordForm.control}
                name="confirmPassword"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Confirm New Password</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="••••••••" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
            <CardFooter>
              <Button type="submit">Change password</Button>
            </CardFooter>
          </form>
        </Form>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Two-Factor Authentication</CardTitle>
          <CardDescription>Add an extra layer of security to your account.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between space-y-2">
            <div className="space-y-0.5">
              <Label htmlFor="two-factor">
                {twoFactorEnabled ? "Two-factor authentication is enabled" : "Enable two-factor authentication"}
              </Label>
              <p className="text-sm text-muted-foreground">
                Protect your account with an additional security layer. When enabled, you'll be required to enter both
                your password and an authentication code to sign in.
              </p>
            </div>
            <Switch id="two-factor" checked={twoFactorEnabled} onCheckedChange={toggleTwoFactor} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Login Activity</CardTitle>
          <CardDescription>Review your account login activity and manage active sessions.</CardDescription>
        </CardHeader>
        <CardContent>
          <Button variant="outline">View login activity</Button>
        </CardContent>
      </Card>
    </div>
  )
}
