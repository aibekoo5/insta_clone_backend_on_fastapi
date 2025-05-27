"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { toast } from "@/components/ui/use-toast"

export function NotificationSettings() {
  const handleSave = () => {
    toast({
      title: "Notification settings saved",
      description: "Your notification settings have been updated successfully",
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Notification Settings</CardTitle>
        <CardDescription>Manage your notification preferences and control what you get notified about.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <h3 className="text-sm font-medium">Push Notifications</h3>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="push-likes" className="flex flex-col space-y-1">
                <span>Likes</span>
                <span className="font-normal text-sm text-muted-foreground">Notify when someone likes your post.</span>
              </Label>
              <Switch id="push-likes" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="push-comments" className="flex flex-col space-y-1">
                <span>Comments</span>
                <span className="font-normal text-sm text-muted-foreground">
                  Notify when someone comments on your post.
                </span>
              </Label>
              <Switch id="push-comments" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="push-follows" className="flex flex-col space-y-1">
                <span>New followers</span>
                <span className="font-normal text-sm text-muted-foreground">Notify when someone follows you.</span>
              </Label>
              <Switch id="push-follows" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="push-mentions" className="flex flex-col space-y-1">
                <span>Mentions</span>
                <span className="font-normal text-sm text-muted-foreground">Notify when someone mentions you.</span>
              </Label>
              <Switch id="push-mentions" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="push-direct-messages" className="flex flex-col space-y-1">
                <span>Direct messages</span>
                <span className="font-normal text-sm text-muted-foreground">
                  Notify when you receive a direct message.
                </span>
              </Label>
              <Switch id="push-direct-messages" defaultChecked />
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-sm font-medium">Email Notifications</h3>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="email-security" className="flex flex-col space-y-1">
                <span>Security and login emails</span>
                <span className="font-normal text-sm text-muted-foreground">
                  Security alerts and login notifications.
                </span>
              </Label>
              <Switch id="email-security" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="email-product" className="flex flex-col space-y-1">
                <span>Product emails</span>
                <span className="font-normal text-sm text-muted-foreground">
                  Updates about new features and improvements.
                </span>
              </Label>
              <Switch id="email-product" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="email-news" className="flex flex-col space-y-1">
                <span>News and updates</span>
                <span className="font-normal text-sm text-muted-foreground">News, tips, and platform updates.</span>
              </Label>
              <Switch id="email-news" />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="email-support" className="flex flex-col space-y-1">
                <span>Support emails</span>
                <span className="font-normal text-sm text-muted-foreground">Responses to your support requests.</span>
              </Label>
              <Switch id="email-support" defaultChecked />
            </div>
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button onClick={handleSave}>Save changes</Button>
      </CardFooter>
    </Card>
  )
}
