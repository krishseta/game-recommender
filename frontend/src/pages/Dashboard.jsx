import { useState, useEffect, useRef } from 'react'
import { HiOutlineSearch, HiOutlineAdjustments, HiOutlineX, HiOutlineSparkles } from 'react-icons/hi'
import { toast } from 'react-toastify'
import axios from 'axios'

const Dashboard = () => {
  const [query, setQuery] = useState('')
  const [games, setGames] = useState([])
  const [loading, setLoading] = useState(false)
  const [showFilterModal, setShowFilterModal] = useState(false)
  const [genres, setGenres] = useState([])
  const [filters, setFilters] = useState({
    maxPrice: 100,
    genres: [],
    windows: false,
    mac: false,
    linux: false,
  })
  const [alpha, setAlpha] = useState(0.5)
  const [topN, setTopN] = useState(12)
  
  const searchInputRef = useRef(null)

  useEffect(() => {
    searchInputRef.current?.focus()
  }, [])

  useEffect(() => {
    const fetchGenres = async () => {
      try {
        const response = await axios.get('/api/genres')
        setGenres(response.data.genres.slice(0, 12))
      } catch (error) {
        console.error('Failed to fetch genres:', error)
      }
    }
    fetchGenres()
  }, [])

  const handleSearch = async () => {
    if (!query.trim()) {
      toast.warning('Enter a search query', { theme: 'dark' })
      return
    }

    setLoading(true)
    try {
      const response = await axios.post('/api/recommend', {
        query,
        filters: {
          max_price: filters.maxPrice < 100 ? filters.maxPrice : null,
          genres: filters.genres.length > 0 ? filters.genres : null,
          windows: filters.windows || undefined,
          mac: filters.mac || undefined,
          linux: filters.linux || undefined,
        },
        alpha,
        top_n: topN,
      })

      setGames(response.data.games)
      
      if (response.data.games.length === 0) {
        toast.info('No games found', { theme: 'dark' })
      }
    } catch (error) {
      console.error('Search error:', error)
      toast.error('Search failed', { theme: 'dark' })
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSearch()
  }

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      {/* Ambient Background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-orange-500/5 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-pink-500/5 rounded-full blur-[120px]" />
      </div>

      {/* Noise Texture Overlay */}
      <div className="fixed inset-0 opacity-[0.015] pointer-events-none bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIj48ZmlsdGVyIGlkPSJhIiB4PSIwIiB5PSIwIj48ZmVUdXJidWxlbmNlIGJhc2VGcmVxdWVuY3k9Ii43NSIgc3RpdGNoVGlsZXM9InN0aXRjaCIgdHlwZT0iZnJhY3RhbE5vaXNlIi8+PGZlQ29sb3JNYXRyaXggdHlwZT0ic2F0dXJhdGUiIHZhbHVlcz0iMCIvPjwvZmlsdGVyPjxwYXRoIGQ9Ik0wIDBoMzAwdjMwMEgweiIgZmlsdGVyPSJ1cmwoI2EpIiBvcGFjaXR5PSIuMDUiLz48L3N2Zz4=')]" />

      {/* Main Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-6 py-20">
        {/* Header */}
        <div className="text-center mb-20 space-y-6">
          <div className="inline-flex items-center gap-2 text-sm text-white/40 tracking-[0.2em] uppercase mb-4">
            <HiOutlineSparkles className="w-4 h-4" />
            <span>Arcade</span>
          </div>
          
          <h1 className="text-6xl md:text-7xl font-light tracking-tight leading-tight pb-4">
            Discover your next
            <span className="block mt-2 pb-2 bg-gradient-to-r from-orange-400 via-red-500 to-pink-500 bg-clip-text text-transparent">
              gaming obsession
            </span>
          </h1>
          
          <p className="text-white/40 text-lg font-light max-w-xl mx-auto">
            AI-powered recommendations tailored to your taste
          </p>
        </div>

        {/* Search Bar */}
        <div className="max-w-3xl mx-auto mb-16">
          <div className="relative group">
            {/* Glow Effect */}
            <div className="absolute -inset-0.5 bg-gradient-to-r from-orange-500/20 to-pink-500/20 rounded-2xl blur opacity-0 group-hover:opacity-100 transition duration-500" />
            
            {/* Glass Container */}
            <div className="relative bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-2xl p-2">
              <div className="flex items-center gap-2">
                <div className="flex-1 flex items-center gap-4 px-4">
                  <HiOutlineSearch className="w-5 h-5 text-white/30" />
                  <input
                    ref={searchInputRef}
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Describe your ideal game..."
                    className="flex-1 bg-transparent border-none outline-none text-white placeholder:text-white/30 text-lg font-light py-4"
                  />
                </div>
                
                <button
                  onClick={() => setShowFilterModal(true)}
                  className="px-6 py-4 bg-white/[0.05] hover:bg-white/[0.08] border border-white/10 rounded-xl transition-all duration-300 flex items-center gap-2"
                >
                  <HiOutlineAdjustments className="w-4 h-4" />
                  <span className="text-sm font-medium">Filters</span>
                </button>
                
                <button
                  onClick={handleSearch}
                  disabled={loading}
                  className="px-8 py-4 bg-gradient-to-r from-orange-500 to-pink-500 hover:from-orange-400 hover:to-pink-400 rounded-xl font-medium transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-orange-500/20"
                >
                  {loading ? 'Searching...' : 'Search'}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center py-20">
            <div className="relative">
              <div className="w-16 h-16 border-2 border-white/10 border-t-orange-400 rounded-full animate-spin" />
              <div className="absolute inset-0 w-16 h-16 border-2 border-white/5 rounded-full blur-sm" />
            </div>
          </div>
        )}

        {/* Results Grid */}
        {!loading && games.length > 0 && (
          <div className="space-y-8">
            <div className="text-center">
              <p className="text-sm text-white/40 tracking-wider uppercase">
                {games.length} {games.length === 1 ? 'Game' : 'Games'} Found
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {games.map((game, index) => (
                <div
                  key={game.appid}
                  className="group relative"
                  style={{ 
                    animation: 'fadeInUp 0.5s ease-out forwards',
                    animationDelay: `${index * 0.08}s`,
                    opacity: 0
                  }}
                >
                  {/* Card Glow */}
                  <div className="absolute -inset-0.5 bg-gradient-to-r from-orange-500/10 to-pink-500/10 rounded-2xl blur opacity-0 group-hover:opacity-100 transition duration-500" />
                  
                  {/* Card */}
                  <div className="relative bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden hover:bg-white/[0.05] transition-all duration-300">
                    {/* Game Image */}
                    <div className="relative h-48 overflow-hidden bg-gradient-to-br from-orange-500/10 to-pink-500/10">
                      {game.header_image ? (
                        <>
                          <img 
                            src={game.header_image}
                            alt={game.name}
                            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                          />
                          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                        </>
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <span className="text-6xl opacity-20">🎮</span>
                        </div>
                      )}
                      
                      {/* Floating badges */}
                      <div className="absolute top-3 left-3 right-3 flex items-start justify-between">
                        <div className="bg-black/60 backdrop-blur-xl px-3 py-1.5 rounded-full border border-white/10">
                          <span className="text-sm font-semibold text-orange-400">
                            {game.price === 0 ? 'FREE' : `$${game.price.toFixed(2)}`}
                          </span>
                        </div>
                        <div className="bg-black/60 backdrop-blur-xl px-3 py-1.5 rounded-full flex items-center gap-1.5 border border-white/10">
                          <HiOutlineSparkles className="text-orange-400 text-sm" />
                          <span className="text-sm font-semibold text-white">{game.final_score.toFixed(2)}</span>
                        </div>
                      </div>
                    </div>

                    {/* Game Info */}
                    <div className="p-5">
                      {/* Title */}
                      <h3 className="text-lg font-semibold mb-3 line-clamp-2 text-white group-hover:text-orange-400 transition-colors duration-300">
                        {game.name}
                      </h3>

                      {/* Genre Pills */}
                      {game.genres && game.genres.length > 0 && (
                        <div className="flex flex-wrap gap-2 mb-4">
                          {game.genres.slice(0, 3).map((genre, idx) => (
                            <span
                              key={idx}
                              className="text-xs px-2.5 py-1 bg-white/[0.05] text-white/60 rounded-full font-medium border border-white/10"
                            >
                              {genre}
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Stats */}
                      <div className="grid grid-cols-2 gap-3 mb-4 pb-4 border-b border-white/10">
                        <div>
                          <div className="text-xs text-white/40 mb-1 uppercase tracking-wider">Rating</div>
                          <div className="text-base font-semibold text-orange-400">
                            {game.weighted_rating.toFixed(3)}
                          </div>
                        </div>
                        <div>
                          <div className="text-xs text-white/40 mb-1 uppercase tracking-wider">Positive</div>
                          <div className="text-base font-semibold text-pink-400">
                            {game.positive + game.negative > 0
                              ? ((game.positive / (game.positive + game.negative)) * 100).toFixed(0)
                              : 0}%
                          </div>
                        </div>
                      </div>

                      {/* Score Breakdown */}
                      <div>
                        <div className="text-xs text-white/40 mb-3 uppercase tracking-wider font-medium">
                          Match Analysis
                        </div>
                        <div className="space-y-2.5">
                          <div>
                            <div className="flex items-center justify-between mb-1.5">
                              <span className="text-xs text-white/50">Semantic</span>
                              <span className="text-xs font-semibold text-orange-400">
                                {(game.semantic_score * 100).toFixed(0)}%
                              </span>
                            </div>
                            <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                              <div
                                style={{ 
                                  width: `${game.semantic_score * 100}%`,
                                  animation: 'expandWidth 0.8s ease-out forwards',
                                  animationDelay: `${index * 0.08 + 0.4}s`
                                }}
                                className="h-full bg-gradient-to-r from-orange-500 to-orange-400 rounded-full"
                              />
                            </div>
                          </div>
                          <div>
                            <div className="flex items-center justify-between mb-1.5">
                              <span className="text-xs text-white/50">Quality</span>
                              <span className="text-xs font-semibold text-pink-400">
                                {(game.quality_score * 100).toFixed(0)}%
                              </span>
                            </div>
                            <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                              <div
                                style={{ 
                                  width: `${game.quality_score * 100}%`,
                                  animation: 'expandWidth 0.8s ease-out forwards',
                                  animationDelay: `${index * 0.08 + 0.5}s`
                                }}
                                className="h-full bg-gradient-to-r from-pink-500 to-pink-400 rounded-full"
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && games.length === 0 && (
          <div className="text-center py-32">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-2xl mb-6">
              <HiOutlineSearch className="w-8 h-8 text-white/30" />
            </div>
            <h3 className="text-2xl font-light text-white/60 mb-2">
              Start your discovery
            </h3>
            <p className="text-white/40">
              Enter a search query to find games
            </p>
          </div>
        )}
      </div>

      {/* Filter Modal */}
      {showFilterModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-6">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-black/60 backdrop-blur-xl"
            onClick={() => setShowFilterModal(false)}
          />
          
          {/* Modal */}
          <div className="relative w-full max-w-3xl bg-black/90 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-2xl max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-2xl font-light mb-1">Refine Your Search</h2>
                <p className="text-sm text-white/40">Customize your discovery experience</p>
              </div>
              <button
                onClick={() => setShowFilterModal(false)}
                className="p-2 hover:bg-white/5 rounded-xl transition-colors"
              >
                <HiOutlineX className="w-5 h-5" />
              </button>
            </div>

            {/* Filter Options */}
            <div className="space-y-8">
              {/* Search Mode (Alpha) */}
              <div>
                <label className="block text-xs font-medium text-white/60 uppercase tracking-wider mb-4">
                  Search Mode
                </label>
                <div className="flex items-center gap-4 mb-3">
                  <span className="text-xs text-white/40 font-medium">Relevance</span>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={alpha}
                    onChange={(e) => setAlpha(parseFloat(e.target.value))}
                    className="flex-1 h-2 bg-white/10 rounded-full appearance-none cursor-pointer slider"
                  />
                  <span className="text-xs text-white/40 font-medium">Quality</span>
                </div>
                <div className="text-center">
                  <span className="text-xs text-orange-400 font-semibold px-4 py-1.5 bg-orange-400/10 rounded-full border border-orange-400/20">
                    {alpha === 1 ? 'Pure Semantic' : alpha === 0 ? 'Pure Quality' : `Hybrid (${alpha.toFixed(1)})`}
                  </span>
                </div>
              </div>

              {/* Platform */}
              <div>
                <label className="block text-xs font-medium text-white/60 uppercase tracking-wider mb-4">
                  Platforms
                </label>
                <div className="flex justify-center gap-3">
                  {[
                    { key: 'windows', label: 'Windows' },
                    { key: 'mac', label: 'macOS' },
                    { key: 'linux', label: 'Linux' }
                  ].map(({ key, label }) => (
                    <button
                      key={key}
                      onClick={() => setFilters({...filters, [key]: !filters[key]})}
                      className={`px-6 py-3 rounded-xl border transition-all ${
                        filters[key]
                          ? 'bg-orange-500/20 border-orange-500/50 text-orange-400'
                          : 'bg-white/[0.03] border-white/10 text-white/60 hover:bg-white/[0.05]'
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Genres */}
              <div>
                <label className="block text-xs font-medium text-white/60 uppercase tracking-wider mb-4">
                  Genres {filters.genres.length > 0 && `(${filters.genres.length})`}
                </label>
                <div className="flex flex-wrap justify-center gap-2 max-w-2xl mx-auto">
                  {genres.map((genre) => (
                    <button
                      key={genre}
                      onClick={() => {
                        setFilters((prev) => ({
                          ...prev,
                          genres: prev.genres.includes(genre)
                            ? prev.genres.filter((g) => g !== genre)
                            : [...prev.genres, genre],
                        }))
                      }}
                      className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                        filters.genres.includes(genre)
                          ? 'bg-orange-500/20 border border-orange-500/50 text-orange-400'
                          : 'bg-white/[0.03] border border-white/10 text-white/60 hover:bg-white/[0.05]'
                      }`}
                    >
                      {genre}
                    </button>
                  ))}
                </div>
                {filters.genres.length > 0 && (
                  <button
                    onClick={() => setFilters((prev) => ({ ...prev, genres: [] }))}
                    className="mt-4 text-xs text-white/40 hover:text-white/60 underline block mx-auto"
                  >
                    Clear genres
                  </button>
                )}
              </div>

              {/* Max Price */}
              <div>
                <label className="block text-xs font-medium text-white/60 uppercase tracking-wider mb-4">
                  Maximum Price: {filters.maxPrice >= 100 ? 'Any' : `$${filters.maxPrice}`}
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  value={filters.maxPrice}
                  onChange={(e) => setFilters({...filters, maxPrice: parseInt(e.target.value)})}
                  className="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer slider"
                />
                <div className="flex justify-between text-xs text-white/40 mt-2">
                  <span>Free</span>
                  <span>$100+</span>
                </div>
              </div>

              {/* Results Count */}
              <div>
                <label className="block text-xs font-medium text-white/60 uppercase tracking-wider mb-4">
                  Number of Results: {topN}
                </label>
                <input
                  type="range"
                  min="6"
                  max="24"
                  step="6"
                  value={topN}
                  onChange={(e) => setTopN(parseInt(e.target.value))}
                  className="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer slider"
                />
                <div className="flex justify-between text-xs text-white/40 mt-2">
                  <span>6</span>
                  <span>24</span>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="flex gap-3 mt-8">
              <button
                onClick={() => {
                  setFilters({
                    maxPrice: 100,
                    genres: [],
                    windows: false,
                    mac: false,
                    linux: false,
                  })
                  setAlpha(0.5)
                  setTopN(12)
                }}
                className="flex-1 px-6 py-4 bg-white/[0.03] hover:bg-white/[0.05] border border-white/10 rounded-xl transition-all"
              >
                Reset All
              </button>
              <button
                onClick={() => setShowFilterModal(false)}
                className="flex-1 px-6 py-4 bg-gradient-to-r from-orange-500 to-pink-500 hover:from-orange-400 hover:to-pink-400 rounded-xl font-medium transition-all shadow-lg shadow-orange-500/20"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes expandWidth {
          from {
            width: 0;
          }
        }

        .slider::-webkit-slider-thumb {
          appearance: none;
          width: 18px;
          height: 18px;
          background: linear-gradient(135deg, #f97316, #ec4899);
          border-radius: 50%;
          cursor: pointer;
          box-shadow: 0 0 20px rgba(249, 115, 22, 0.5);
        }
        
        .slider::-moz-range-thumb {
          width: 18px;
          height: 18px;
          background: linear-gradient(135deg, #f97316, #ec4899);
          border-radius: 50%;
          cursor: pointer;
          border: none;
          box-shadow: 0 0 20px rgba(249, 115, 22, 0.5);
        }

        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      `}</style>
    </div>
  )
}

export default Dashboard