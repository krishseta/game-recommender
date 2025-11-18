import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { SiWindows, SiApple, SiLinux } from 'react-icons/si'
import axios from 'axios'

const FilterComponent = ({ filters, setFilters, alpha, setAlpha, topN, setTopN }) => {
  const [genres, setGenres] = useState([])
  const [expandedSection, setExpandedSection] = useState(null)

  useEffect(() => {
    fetchGenres()
  }, [])

  const fetchGenres = async () => {
    try {
      const response = await axios.get('/api/genres')
      setGenres(response.data.genres.slice(0, 12)) // Top 12 genres
    } catch (error) {
      console.error('Failed to fetch genres:', error)
    }
  }

  const toggleGenre = (genre) => {
    setFilters((prev) => ({
      ...prev,
      genres: prev.genres.includes(genre)
        ? prev.genres.filter((g) => g !== genre)
        : [...prev.genres, genre],
    }))
  }

  return (
    <div className="liquid-glass rounded-3xl p-10 max-w-4xl mx-auto">
      {/* Title */}
      <div className="text-center mb-10">
        <h3 className="text-2xl font-light text-taupe-700 editorial-title mb-2">
          Refine Your Search
        </h3>
        <p className="text-sm text-taupe-400">Customize your discovery experience</p>
      </div>

      {/* Vertical Centered Layout */}
      <div className="space-y-10">
        {/* Search Mode */}
        <div className="text-center">
          <label className="block text-xs font-medium text-taupe-500 uppercase tracking-wider mb-4">
            Search Mode
          </label>
          <div className="flex items-center justify-center space-x-6 max-w-md mx-auto">
            <span className="text-xs text-taupe-400 font-medium">Relevance</span>
            <div className="flex-1 relative">
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={alpha}
                onChange={(e) => setAlpha(parseFloat(e.target.value))}
                className="w-full h-1 bg-taupe-200 rounded-full appearance-none cursor-pointer accent-sage-500"
              />
              {/* Dot indicators */}
              <div className="absolute top-1/2 left-0 right-0 flex justify-between px-1 pointer-events-none" style={{ transform: 'translateY(-50%)' }}>
                {[0, 0.5, 1].map((val) => (
                  <div
                    key={val}
                    className={`dot-indicator ${Math.abs(alpha - val) < 0.15 ? 'active' : ''}`}
                  />
                ))}
              </div>
            </div>
            <span className="text-xs text-taupe-400 font-medium">Quality</span>
          </div>
          <div className="mt-3">
            <span className="text-xs text-sage-500 font-semibold px-4 py-1.5 bg-sage-400/10 rounded-full">
              {alpha === 1 ? 'Semantic' : alpha === 0 ? 'Quality' : 'Hybrid'}
            </span>
          </div>
        </div>

        {/* Platforms */}
        <div className="text-center">
          <label className="block text-xs font-medium text-taupe-500 uppercase tracking-wider mb-4">
            Platforms
          </label>
          <div className="flex items-center justify-center space-x-4">
            {[
              { key: 'windows', icon: SiWindows, label: 'Windows' },
              { key: 'mac', icon: SiApple, label: 'macOS' },
              { key: 'linux', icon: SiLinux, label: 'Linux' },
            ].map(({ key, icon: Icon, label }) => (
              <motion.button
                key={key}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setFilters((prev) => ({ ...prev, [key]: !prev[key] }))}
                className={`relative p-5 rounded-2xl transition-all duration-300 ${
                  filters[key]
                    ? 'bg-sage-400/20 border-2 border-sage-400'
                    : 'bg-white/40 border-2 border-taupe-200 hover:border-taupe-300'
                }`}
              >
                <Icon className={`text-2xl ${filters[key] ? 'text-sage-600' : 'text-taupe-400'}`} />
                {filters[key] && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="absolute -top-1 -right-1 w-3 h-3 bg-sage-500 rounded-full"
                  />
                )}
              </motion.button>
            ))}
          </div>
        </div>

        {/* Genres */}
        <div className="text-center">
          <label className="block text-xs font-medium text-taupe-500 uppercase tracking-wider mb-4">
            Genres {filters.genres.length > 0 && `(${filters.genres.length})`}
          </label>
          <div className="flex flex-wrap justify-center gap-2 max-w-2xl mx-auto">
            {genres.map((genre) => (
              <motion.button
                key={genre}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => toggleGenre(genre)}
                className={`px-5 py-2.5 rounded-full text-sm font-medium transition-all duration-300 ${
                  filters.genres.includes(genre)
                    ? 'bg-sage-400/20 border border-sage-400 text-sage-700'
                    : 'bg-white/40 border border-taupe-200 text-taupe-600 hover:border-taupe-300'
                }`}
              >
                {genre}
              </motion.button>
            ))}
          </div>
          {filters.genres.length > 0 && (
            <motion.button
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              onClick={() => setFilters((prev) => ({ ...prev, genres: [] }))}
              className="mt-4 text-xs text-taupe-500 hover:text-taupe-700 underline"
            >
              Clear genres
            </motion.button>
          )}
        </div>

        {/* Price Range */}
        <div className="text-center">
          <label className="block text-xs font-medium text-taupe-500 uppercase tracking-wider mb-4">
            Maximum Price: {filters.maxPrice >= 100 ? 'Any' : `$${filters.maxPrice}`}
          </label>
          <div className="max-w-md mx-auto">
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={filters.maxPrice}
              onChange={(e) => setFilters((prev) => ({ ...prev, maxPrice: parseInt(e.target.value) }))}
              className="w-full h-1 bg-taupe-200 rounded-full appearance-none cursor-pointer accent-amber-500"
            />
            <div className="flex justify-between text-xs text-taupe-400 mt-2">
              <span>Free</span>
              <span>$100+</span>
            </div>
          </div>
        </div>

        {/* Results Count */}
        <div className="text-center">
          <label className="block text-xs font-medium text-taupe-500 uppercase tracking-wider mb-4">
            Results: {topN}
          </label>
          <div className="max-w-md mx-auto">
            <input
              type="range"
              min="6"
              max="24"
              step="6"
              value={topN}
              onChange={(e) => setTopN(parseInt(e.target.value))}
              className="w-full h-1 bg-taupe-200 rounded-full appearance-none cursor-pointer accent-amber-500"
            />
            <div className="flex justify-between text-xs text-taupe-400 mt-2">
              <span>6</span>
              <span>24</span>
            </div>
          </div>
        </div>
      </div>

      {/* Reset Button */}
      <div className="mt-10 text-center">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() =>
            setFilters({
              maxPrice: 100,
              genres: [],
              windows: false,
              mac: false,
              linux: false,
            })
          }
          className="px-8 py-3 bg-white/50 hover:bg-white/70 border border-taupe-200 hover:border-taupe-300 text-taupe-600 hover:text-taupe-700 font-medium rounded-full transition-all duration-300 text-sm"
        >
          Reset All Filters
        </motion.button>
      </div>
    </div>
  )
}

export default FilterComponent
