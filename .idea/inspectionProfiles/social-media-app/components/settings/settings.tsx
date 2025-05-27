"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { User, Lock, Bell, Shield, LogOut } from "lucide-react"
import { AccountSettings } from "@/components/settings/account-settings"
import { PrivacySettings } from "@/components/settings/privacy-settings"
import { NotificationSettings } from "@/components/settings/notification-settings"
import { SecuritySettings } from "@/components/settings/security-settings"
import { useRouter } from "next/navigation"
import { toast } from "@/components/ui/use-toast"

export function Settings() {
  const router = useRouter()
  const [isLoggingOut, setIsLoggingOut] = useState(false)

  const handleLogout = async () => {
    setIsLoggingOut(true);
    
    try {
      const response = await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include", // send cookies if using cookie-based auth
      });
    
      if (!response.ok) {
        throw new Error("Failed to logout");
      }
    
      router.push("/login");
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to logout. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoggingOut(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Manage your account settings and preferences.</p>
      </div>

      <Tabs defaultValue="account">
        <div className="flex flex-col gap-4 md:flex-row">
          <TabsList className="h-auto w-full flex-col md:w-48 md:justify-start">
            <TabsTrigger value="account" className="w-full justify-start">
              <User className="mr-2 h-4 w-4" />
              Account
            </TabsTrigger>
            <TabsTrigger value="privacy" className="w-full justify-start">
              <Shield className="mr-2 h-4 w-4" />
              Privacy
            </TabsTrigger>
            <TabsTrigger value="notifications" className="w-full justify-start">
              <Bell className="mr-2 h-4 w-4" />
              Notifications
            </TabsTrigger>
            <TabsTrigger value="security" className="w-full justify-start">
              <Lock className="mr-2 h-4 w-4" />
              Security
            </TabsTrigger>
            <Button
              variant="ghost"
              className="mt-4 w-full justify-start"
              onClick={handleLogout}
              disabled={isLoggingOut}
            >
              <LogOut className="mr-2 h-4 w-4" />
              {isLoggingOut ? "Logging out..." : "Logout"}
            </Button>
          </TabsList>

          <div className="flex-1">
            <TabsContent value="account" className="m-0">
              <AccountSettings />
            </TabsContent>
            <TabsContent value="privacy" className="m-0">
              <PrivacySettings />
            </TabsContent>
            <TabsContent value="notifications" className="m-0">
              <NotificationSettings />
            </TabsContent>
            <TabsContent value="security" className="m-0">
              <SecuritySettings />
            </TabsContent>
          </div>
        </div>
      </Tabs>
    </div>
  )
}
