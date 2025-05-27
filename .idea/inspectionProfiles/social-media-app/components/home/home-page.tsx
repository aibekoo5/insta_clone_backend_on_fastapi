import { Shell } from "@/components/layout/shell"
import { Feed } from "@/components/home/feed"
import { Stories } from "@/components/home/stories"

export default function HomePage() {
  return (
    <Shell>
      <div className="space-y-4">
        <Stories />
        <Feed />
      </div>
    </Shell>
  )
}
