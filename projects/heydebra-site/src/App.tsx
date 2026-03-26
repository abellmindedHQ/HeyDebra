import { Navbar } from './components/Navbar'
import { Hero } from './components/Hero'
import { WhatIsDebra } from './components/WhatIsDebra'
import { WhatSheDoes } from './components/WhatSheDoes'
import { TheVoice } from './components/TheVoice'
import { TheStack } from './components/TheStack'
import { BuiltBy } from './components/BuiltBy'
import { Footer } from './components/Footer'
import { Particles } from './components/Particles'

function App() {
  return (
    <div className="relative min-h-screen bg-deep-black">
      {/* Skip to main content - accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-hot-pink focus:text-white focus:rounded focus:font-semibold"
      >
        Skip to main content
      </a>
      <Particles />
      <Navbar />
      <main id="main-content" className="relative z-10">
        <Hero />
        <WhatIsDebra />
        <WhatSheDoes />
        <TheVoice />
        <TheStack />
        <BuiltBy />
      </main>
      <Footer />
    </div>
  )
}

export default App
