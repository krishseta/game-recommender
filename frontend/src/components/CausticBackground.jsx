import { motion } from 'framer-motion'

const CausticBackground = () => {
  return (
    <>
      {/* Base gradient */}
      <div className="caustic-bg" />
      
      {/* Additional floating orbs for depth */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <motion.div
          animate={{
            x: [0, 100, 0],
            y: [0, -50, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="absolute top-1/4 left-1/3 w-96 h-96 rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(156, 169, 134, 0.08) 0%, transparent 70%)',
            filter: 'blur(60px)',
          }}
        />
        
        <motion.div
          animate={{
            x: [0, -80, 0],
            y: [0, 60, 0],
            scale: [1, 1.1, 1],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: 'easeInOut',
            delay: 2,
          }}
          className="absolute bottom-1/3 right-1/4 w-80 h-80 rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(212, 165, 116, 0.06) 0%, transparent 70%)',
            filter: 'blur(70px)',
          }}
        />

        <motion.div
          animate={{
            x: [0, 60, 0],
            y: [0, -40, 0],
            scale: [1, 1.15, 1],
          }}
          transition={{
            duration: 30,
            repeat: Infinity,
            ease: 'easeInOut',
            delay: 5,
          }}
          className="absolute top-1/2 right-1/3 w-72 h-72 rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(122, 138, 111, 0.05) 0%, transparent 70%)',
            filter: 'blur(80px)',
          }}
        />
      </div>

      {/* Subtle noise texture overlay */}
      <div 
        className="fixed inset-0 pointer-events-none opacity-[0.015]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />
    </>
  )
}

export default CausticBackground
