"use client"

import type React from "react"
import { get } from "@/lib/api";
import { useState } from "react"
import { useEffect } from "react";
import Image from "next/image"
import Link from "next/link"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Search, Compass, Hash, TrendingUp } from "lucide-react"

interface SearchResult {
  id: number
  type: "user" | "post" | "tag"
  text: string
  secondaryText?: string
  image?: string
}

export function Explore() {
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [trendingPosts, setTrendingPosts] = useState<any[]>([]);

  useEffect(() => {
    async function fetchTrending() {
      try {
        const posts = await get("/posts/trending"); // Adjust endpoint as needed
        setTrendingPosts(posts);
      } catch {
        setTrendingPosts([]);
      }
    }
    fetchTrending();
  }, []);

  const handleSearch = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);

    if (query.trim().length === 0) {
      setSearchResults([]);
      return;
    }

    try {
      // Example: GET /search?q=your_query
      const response = await fetch(`http://localhost:8000/search?q=${encodeURIComponent(query)}`, {
        credentials: "include",
      });
      if (!response.ok) throw new Error("Search failed");
      const results = await response.json();
      // Adapt this mapping to your backend's response structure
      setSearchResults(results);
    } catch (error) {
      setSearchResults([]);
    }
  };

  return (
    <div className="space-y-6">
      <div className="relative">
        <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search users, tags, or posts"
          className="pl-10"
          value={searchQuery}
          onChange={handleSearch}
        />
        {searchResults.length > 0 && (
          <div className="absolute z-10 mt-1 w-full rounded-md border bg-background p-2 shadow-md">
            {searchResults.map((result) => (
              <Link
                key={result.id}
                href={
                  result.type === "user"
                    ? `/profile/${result.text}`
                    : result.type === "tag"
                      ? `/explore/tags/${result.text.substring(1)}`
                      : "#"
                }
                className="flex items-center gap-3 rounded-md p-2 hover:bg-accent"
              >
                {result.type === "user" && result.image && (
                  <Image
                    src={result.image || "/placeholder.svg"}
                    alt={result.text}
                    width={40}
                    height={40}
                    className="rounded-full"
                  />
                )}
                {result.type === "tag" && (
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-muted">
                    <Hash className="h-5 w-5" />
                  </div>
                )}
                <div>
                  <p className="font-medium">{result.text}</p>
                  {result.secondaryText && <p className="text-xs text-muted-foreground">{result.secondaryText}</p>}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      <Tabs defaultValue="trending">
        <TabsList className="w-full">
          <TabsTrigger value="trending" className="flex-1">
            <TrendingUp className="mr-2 h-4 w-4" />
            Trending
          </TabsTrigger>
          <TabsTrigger value="discover" className="flex-1">
            <Compass className="mr-2 h-4 w-4" />
            Discover
          </TabsTrigger>
        </TabsList>
        <TabsContent value="trending" className="mt-4">
          <div className="grid grid-cols-3 gap-1 md:gap-2">
            {trendingPosts.map((post) => (
              <Link key={post.id} href={`/posts/${post.id}`} className="relative aspect-square">
                <Image src={post.image || "/placeholder.svg"} alt={`Post ${post.id}`} fill className="object-cover" />
              </Link>
            ))}
          </div>
        </TabsContent>
        <TabsContent value="discover" className="mt-4">
          <div className="grid grid-cols-3 gap-1 md:gap-2">
            {/* Random posts would be displayed here */}
            {trendingPosts
              .slice()
              .reverse()
              .map((post) => (
                <Link key={post.id} href={`/posts/${post.id}`} className="relative aspect-square">
                  <Image src={post.image || "/placeholder.svg"} alt={`Post ${post.id}`} fill className="object-cover" />
                </Link>
              ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
