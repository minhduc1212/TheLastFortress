"use client";

import { useState, useEffect } from "react";
import { Search, ExternalLink, Menu, X, ChevronRight, Hash } from "lucide-react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface Link {
  name: string;
  url: string;
}

interface ResourceItem {
  full_text: string;
  links: Link[];
}

interface Section {
  heading: string;
  level: string;
  text_explanations: string[];
  resource_items: ResourceItem[];
}

interface CategoryContent {
  url: string;
  title: string;
  sections: Section[];
}

interface Category {
  category_name: string;
  content: CategoryContent;
}

export default function Home() {
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [data, setData] = useState<Category[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    if (selectedCategory) {
      fetchData(selectedCategory);
    }
  }, [selectedCategory]);

  const fetchCategories = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/categories");
      const json = await res.json();
      setCategories(json);
      if (json.length > 0 && !selectedCategory) {
        setSelectedCategory(json[0]);
      }
    } catch (err) {
      console.error("Failed to fetch categories", err);
    }
  };

  const fetchData = async (category: string) => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/data?category=${encodeURIComponent(category)}`);
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error("Failed to fetch data", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery) return;
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/search?q=${encodeURIComponent(searchQuery)}`);
      const json = await res.json();
      setData(json);
      setSelectedCategory(""); // Clear selection to show search results
    } catch (err) {
      console.error("Search failed", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-neutral-50 dark:bg-neutral-950 text-neutral-900 dark:text-neutral-100 overflow-hidden">
      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-neutral-900 border-r border-neutral-200 dark:border-neutral-800 transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0",
          !isSidebarOpen && "-translate-x-full lg:hidden"
        )}
      >
        <div className="flex flex-col h-full">
          <div className="p-6 border-b border-neutral-200 dark:border-neutral-800 flex items-center justify-between">
            <h1 className="text-xl font-bold tracking-tight">FMHY Viewer</h1>
            <button onClick={() => setIsSidebarOpen(false)} className="lg:hidden p-1">
              <X size={20} />
            </button>
          </div>
          <nav className="flex-1 overflow-y-auto p-4 space-y-1">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-md text-sm transition-colors duration-200 flex items-center group",
                  selectedCategory === cat
                    ? "bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 font-medium"
                    : "text-neutral-500 hover:text-neutral-900 dark:hover:text-neutral-100 hover:bg-neutral-50 dark:hover:bg-neutral-800/50"
                )}
              >
                <ChevronRight
                  size={14}
                  className={cn(
                    "mr-2 transition-transform",
                    selectedCategory === cat ? "rotate-90 opacity-100" : "opacity-0 group-hover:opacity-100"
                  )}
                />
                {cat}
              </button>
            ))}
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <header className="h-16 flex items-center justify-between px-4 lg:px-8 border-b border-neutral-200 dark:border-neutral-800 bg-white/80 dark:bg-neutral-900/80 backdrop-blur-md z-10">
          <button onClick={() => setIsSidebarOpen(true)} className={cn("p-2 lg:hidden", isSidebarOpen && "hidden")}>
            <Menu size={20} />
          </button>
          
          <form onSubmit={handleSearch} className="flex-1 max-w-2xl mx-auto px-4">
            <div className="relative group">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400 group-focus-within:text-neutral-900 dark:group-focus-within:text-neutral-100 transition-colors" size={18} />
              <input
                type="text"
                placeholder="Search resources, sites, guides..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-neutral-100 dark:bg-neutral-800 border-none rounded-full py-2 pl-10 pr-4 focus:ring-2 focus:ring-neutral-200 dark:focus:ring-neutral-700 transition-all text-sm outline-none"
              />
            </div>
          </form>
          
          <div className="w-10 lg:w-0" /> {/* Spacer for symmetry on mobile */}
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto px-4 lg:px-8 py-8 scroll-smooth">
          <div className="max-w-4xl mx-auto space-y-12">
            {loading ? (
              <div className="flex items-center justify-center py-20 text-neutral-500">
                <div className="animate-pulse">Loading amazing things...</div>
              </div>
            ) : data.length > 0 ? (
              data.map((cat, catIdx) => (
                <div key={catIdx} className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                  <div className="space-y-2">
                    <h2 className="text-3xl font-bold tracking-tight">{cat.category_name}</h2>
                    <p className="text-sm text-neutral-500 font-mono opacity-70">{cat.content.url}</p>
                  </div>

                  <div className="grid gap-6">
                    {cat.content.sections.map((section, secIdx) => (
                      <section
                        key={secIdx}
                        className="p-6 bg-white dark:bg-neutral-900 rounded-2xl border border-neutral-200 dark:border-neutral-800 shadow-sm hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start gap-2 mb-4">
                          <Hash className="mt-1 text-neutral-300 dark:text-neutral-700" size={18} />
                          <h3 className="text-xl font-semibold">{section.heading}</h3>
                        </div>

                        {section.text_explanations.length > 0 && (
                          <div className="space-y-3 mb-6">
                            {section.text_explanations.map((text, tIdx) => (
                              <p key={tIdx} className="text-neutral-600 dark:text-neutral-400 text-sm leading-relaxed">
                                {text}
                              </p>
                            ))}
                          </div>
                        )}

                        {section.resource_items.length > 0 && (
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            {section.resource_items.map((item, itemIdx) => (
                              <div
                                key={itemIdx}
                                className="flex flex-col p-3 rounded-xl bg-neutral-50 dark:bg-neutral-800/50 border border-neutral-100 dark:border-neutral-800"
                              >
                                <span className="text-xs font-medium text-neutral-400 mb-2 uppercase tracking-wider">
                                  {item.full_text.split(":")[0]}
                                </span>
                                <div className="flex flex-wrap gap-2 mt-auto">
                                  {item.links.map((link, lIdx) => (
                                    <a
                                      key={lIdx}
                                      href={link.url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white dark:bg-neutral-800 text-sm font-medium border border-neutral-200 dark:border-neutral-700 hover:border-neutral-400 dark:hover:border-neutral-500 transition-all hover:translate-y-[-1px]"
                                    >
                                      {link.name}
                                      <ExternalLink size={12} className="opacity-50" />
                                    </a>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </section>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-20 text-neutral-500">
                <Search size={48} className="mx-auto mb-4 opacity-20" />
                <p>No results found for "{searchQuery}"</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
