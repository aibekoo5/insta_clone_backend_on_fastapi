"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { toast } from "@/components/ui/use-toast"

export function PrivacySettings() {
  const handleSave = () => {
    toast({
      title: "Privacy settings saved",
      description: "Your privacy settings have been updated successfully",
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Privacy Settings</CardTitle>
        <CardDescription>Manage your privacy settings and control who can see your content.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <h3 className="text-sm font-medium">Activity Status</h3>
          <div className="flex items-center justify-between space-y-2">
            <Label htmlFor="activity-status" className="flex flex-col space-y-1">
              <span>Show activity status</span>
              <span className="font-normal text-sm text-muted-foreground">
                Allow accounts you follow and anyone you message to see when you were last active.
              </span>
            </Label>
            <Switch id="activity-status" defaultChecked />
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-sm font-medium">Story</h3>
          <div className="flex items-center justify-between space-y-2">
            <Label htmlFor="hide-story" className="flex flex-col space-y-1">
              <span>Hide story from</span>
              <span className="font-normal text-sm text-muted-foreground">Hide your story from specific people.</span>
            </Label>
            <Button variant="outline" size="sm">
              Manage
            </Button>
          </div>
          <div className="flex items-center justify-between space-y-2">
            <Label htmlFor="story-sharing" className="flex flex-col space-y-1">
              <span>Allow sharing</span>
              <span className="font-normal text-sm text-muted-foreground">
                Let people share your story as messages.
              </span>
            </Label>
            <Switch id="story-sharing" defaultChecked />
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-sm font-medium">Comments</h3>
          <div className="flex items-center justify-between space-y-2">
            <Label htmlFor="comment-control" className="flex flex-col space-y-1">
              <span>Comment control</span>
              <span className="font-normal text-sm text-muted-foreground">Control who can comment on your posts.</span>
            </Label>
            <Button variant="outline" size="sm">
              Edit
            </Button>
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-sm font-medium">Tags</h3>
          <div className="flex items-center justify-between space-y-2">
            <Label htmlFor="tag-approval" className="flex flex-col space-y-1">
              <span>Manually approve tags</span>
              <span className="font-normal text-sm text-muted-foreground">
                Review tags people add to your posts before they appear.
              </span>
            </Label>
            <Switch id="tag-approval" defaultChecked />
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-sm font-medium">Mentions</h3>
          <div className="flex items-center justify-between space-y-2">
            <Label htmlFor="mentions-control" className="flex flex-col space-y-1">
              <span>Allow mentions from</span>
              <span className="font-normal text-sm text-muted-foreground">
                Control who can mention you in their posts, stories, and comments.
              </span>
            </Label>
            <Button variant="outline" size="sm">
              Edit
            </Button>
          </div>
        </div>

        <Button onClick={handleSave}>Save changes</Button>
      </CardContent>
    </Card>
  )
}
